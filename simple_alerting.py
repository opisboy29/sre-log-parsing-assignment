#!/usr/bin/env python3
"""
Simple Alerting System for E-commerce Platform Logs
Monitors error rates and displays alerts
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys


class SimpleAlertManager:
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.elasticsearch_url = elasticsearch_url
        self.thresholds = {
            'error_rate': 25.0,  # Alert if error rate > 25%
            'response_time_p95': 1000,  # Alert if 95th percentile > 1000ms
            'total_errors_5min': 50,  # Alert if > 50 errors in 5 minutes
        }
        self.session = requests.Session()
        
    def query_elasticsearch(self, query: Dict[str, Any], index: str = "ecommerce-logs-*") -> Dict[str, Any]:
        """Execute query against Elasticsearch"""
        try:
            url = f"{self.elasticsearch_url}/{index}/_search"
            response = self.session.post(url, json=query, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying Elasticsearch: {e}")
            return {}
    
    def get_current_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get current metrics from the last 60 minutes (since our logs are old)"""
        
        # Query for all logs (since our sample data is from 2023)
        query = {
            "query": {"match_all": {}},
            "size": 0,
            "aggs": {
                "total_requests": {
                    "value_count": {"field": "transaction_id.keyword"}
                },
                "error_requests": {
                    "filter": {"range": {"status_code": {"gte": 400}}}
                },
                "response_time_stats": {
                    "stats": {"field": "response_time_ms"}
                },
                "response_time_percentiles": {
                    "percentiles": {
                        "field": "response_time_ms",
                        "percents": [95, 99]
                    }
                },
                "status_codes": {
                    "terms": {"field": "status_code"}
                }
            }
        }
        
        result = self.query_elasticsearch(query)
        if not result or 'aggregations' not in result:
            return {}
        
        aggs = result['aggregations']
        total_requests = aggs['total_requests']['value']
        error_count = aggs['error_requests']['doc_count']
        
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        
        response_times = aggs['response_time_stats']
        percentiles = aggs['response_time_percentiles']['values']
        
        return {
            'total_requests': total_requests,
            'error_count': error_count,
            'error_rate': round(error_rate, 2),
            'avg_response_time': round(response_times['avg'], 2),
            'p95_response_time': round(percentiles['95.0'], 2),
            'p99_response_time': round(percentiles['99.0'], 2),
            'min_response_time': response_times['min'],
            'max_response_time': response_times['max'],
            'status_codes': {bucket['key']: bucket['doc_count'] for bucket in aggs['status_codes']['buckets']}
        }
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        if not metrics:
            return alerts
        
        # Check error rate
        if metrics['error_rate'] > self.thresholds['error_rate']:
            severity = 'CRITICAL' if metrics['error_rate'] > 50 else 'WARNING'
            alerts.append({
                'type': 'High Error Rate',
                'severity': severity,
                'message': f"Error rate is {metrics['error_rate']}%, exceeding threshold of {self.thresholds['error_rate']}%",
                'current_value': f"{metrics['error_rate']}%",
                'threshold': f"{self.thresholds['error_rate']}%"
            })
        
        # Check P95 response time
        if metrics['p95_response_time'] > self.thresholds['response_time_p95']:
            severity = 'CRITICAL' if metrics['p95_response_time'] > 2000 else 'WARNING'
            alerts.append({
                'type': 'High Response Time',
                'severity': severity,
                'message': f"95th percentile response time is {metrics['p95_response_time']}ms, exceeding threshold of {self.thresholds['response_time_p95']}ms",
                'current_value': f"{metrics['p95_response_time']}ms",
                'threshold': f"{self.thresholds['response_time_p95']}ms"
            })
        
        # Check total errors
        if metrics['error_count'] > self.thresholds['total_errors_5min']:
            alerts.append({
                'type': 'High Error Count',
                'severity': 'WARNING',
                'message': f"Total error count is {metrics['error_count']}, exceeding threshold of {self.thresholds['total_errors_5min']}",
                'current_value': str(metrics['error_count']),
                'threshold': str(self.thresholds['total_errors_5min'])
            })
        
        return alerts
    
    def display_metrics_and_alerts(self):
        """Display current metrics and any alerts"""
        print("="*60)
        print("E-COMMERCE PLATFORM MONITORING")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        metrics = self.get_current_metrics()
        
        if not metrics:
            print("❌ Could not retrieve metrics from Elasticsearch")
            return
        
        print("CURRENT METRICS:")
        print("-" * 30)
        print(f"Total Requests: {metrics['total_requests']}")
        print(f"Error Count: {metrics['error_count']}")
        print(f"Error Rate: {metrics['error_rate']}%")
        print(f"Avg Response Time: {metrics['avg_response_time']}ms")
        print(f"P95 Response Time: {metrics['p95_response_time']}ms")
        print(f"P99 Response Time: {metrics['p99_response_time']}ms")
        print()
        
        print("STATUS CODE DISTRIBUTION:")
        print("-" * 30)
        for status_code, count in sorted(metrics['status_codes'].items()):
            print(f"  {status_code}: {count}")
        print()
        
        # Check for alerts
        alerts = self.check_thresholds(metrics)
        
        if alerts:
            print("🚨 ALERTS TRIGGERED:")
            print("-" * 30)
            for alert in alerts:
                icon = "🔥" if alert['severity'] == 'CRITICAL' else "⚠️"
                print(f"{icon} {alert['severity']}: {alert['type']}")
                print(f"   {alert['message']}")
                print()
        else:
            print("✅ All metrics within normal thresholds")
        
        print("="*60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple E-commerce Platform Alert Monitor')
    parser.add_argument('--elasticsearch-url', default='http://localhost:9200',
                        help='Elasticsearch URL (default: http://localhost:9200)')
    parser.add_argument('--once', action='store_true',
                        help='Run once instead of continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                        help='Monitoring interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    alert_manager = SimpleAlertManager(args.elasticsearch_url)
    
    if args.once:
        alert_manager.display_metrics_and_alerts()
    else:
        print(f"Starting continuous monitoring (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        try:
            while True:
                alert_manager.display_metrics_and_alerts()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()