#!/usr/bin/env python3
"""
Direct Elasticsearch Ingestion Script
Sends parsed logs directly to Elasticsearch
"""

import requests
import json
import time
import sys
from datetime import datetime
from log_parser import LogParser


class ElasticsearchIngester:
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.es_url = elasticsearch_url
        self.session = requests.Session()
        
    def wait_for_elasticsearch(self, max_retries: int = 30, delay: int = 5):
        """Wait for Elasticsearch to be ready"""
        print("Waiting for Elasticsearch to be ready...")
        for attempt in range(max_retries):
            try:
                response = self.session.get(f"{self.es_url}/_cluster/health")
                if response.status_code == 200:
                    print("Elasticsearch is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"Attempt {attempt + 1}/{max_retries}: Elasticsearch not ready, waiting {delay}s...")
            time.sleep(delay)
        
        print("Warning: Could not verify Elasticsearch readiness")
        return False
    
    def send_log_entry(self, log_entry: dict, index_name: str) -> bool:
        """Send a single log entry to Elasticsearch"""
        try:
            response = self.session.post(
                f"{self.es_url}/{index_name}/_doc",
                json=log_entry,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Failed to send log entry: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to send log entry: {e}")
            return False
    
    def ingest_logs(self, log_file: str) -> dict:
        """Ingest all logs from a file"""
        parser = LogParser(log_file)
        parsed_logs = parser.parse_logs()
        
        if not parsed_logs:
            print("No logs to ingest")
            return {"successful": 0, "failed": 0, "total": 0}
        
        # Wait for Elasticsearch to be ready
        self.wait_for_elasticsearch()
        
        # Create index name based on current date
        index_name = f"ecommerce-logs-{datetime.now().strftime('%Y.%m.%d')}"
        
        print(f"Ingesting {len(parsed_logs)} log entries to {self.es_url}/{index_name}")
        
        successful = 0
        failed = 0
        total = len(parsed_logs)
        
        for i, log_entry in enumerate(parsed_logs):
            # Convert datetime objects to strings for JSON serialization
            log_entry_copy = log_entry.copy()
            if 'datetime' in log_entry_copy:
                log_entry_copy['datetime'] = log_entry_copy['datetime'].isoformat()
            
            # Add timestamp for Elasticsearch
            log_entry_copy['@timestamp'] = log_entry_copy.get('timestamp', datetime.now().isoformat())
            
            if self.send_log_entry(log_entry_copy, index_name):
                successful += 1
            else:
                failed += 1
            
            # Progress indicator
            if (i + 1) % 10 == 0 or (i + 1) == total:
                progress = ((i + 1) / total) * 100
                print(f"Progress: {i + 1}/{total} ({progress:.1f}%)")
            
            # Small delay to avoid overwhelming Elasticsearch
            time.sleep(0.1)
        
        return {
            "successful": successful,
            "failed": failed,
            "total": total
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ingest_logs.py <log_file> [elasticsearch_url]")
        sys.exit(1)
    
    log_file = sys.argv[1]
    es_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:9200"
    
    ingester = ElasticsearchIngester(es_url)
    results = ingester.ingest_logs(log_file)
    
    print(f"\nIngestion complete:")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Total: {results['total']}")
    
    if results['failed'] > 0:
        print(f"\n❌ Log ingestion completed with errors")
        sys.exit(1)
    else:
        print(f"\n✅ All logs ingested successfully!")

if __name__ == "__main__":
    main()