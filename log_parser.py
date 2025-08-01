#!/usr/bin/env python3
"""
Log Parser for SRE Assignment
Parses e-commerce platform logs and extracts key metrics
"""

import re
import json
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple


class LogParser:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.parsed_logs = []
        self.metrics = {
            'total_transactions': 0,
            'error_counts': defaultdict(int),
            'service_metrics': defaultdict(lambda: {'count': 0, 'response_times': [], 'errors': 0}),
            'status_code_distribution': Counter(),
            'user_activity': defaultdict(int),
            'hourly_distribution': defaultdict(int)
        }
        
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Parse a single log line into structured data"""
        # Regex pattern to match the log format
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) (\d+) (\d+)ms (\S+) (\S+) (.+)'
        match = re.match(pattern, line.strip())
        
        if not match:
            return None
            
        timestamp_str, service_name, status_code, response_time_str, user_id, transaction_id, additional_info = match.groups()
        
        # Parse timestamp
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        # Extract response time (remove 'ms' suffix)
        response_time = int(response_time_str)
        status_code = int(status_code)
        
        return {
            'timestamp': timestamp_str,
            'datetime': timestamp,
            'service_name': service_name,
            'status_code': status_code,
            'response_time_ms': response_time,
            'user_id': user_id,
            'transaction_id': transaction_id,
            'additional_info': additional_info.strip(),
            'is_error': status_code >= 400
        }
    
    def parse_logs(self) -> List[Dict[str, Any]]:
        """Parse all log lines and calculate metrics"""
        try:
            with open(self.log_file_path, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():
                        parsed_line = self.parse_log_line(line)
                        if parsed_line:
                            self.parsed_logs.append(parsed_line)
                            self._update_metrics(parsed_line)
                        else:
                            print(f"Warning: Could not parse line {line_num}: {line.strip()}")
        except FileNotFoundError:
            print(f"Error: Log file '{self.log_file_path}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading log file: {e}")
            sys.exit(1)
            
        return self.parsed_logs
    
    def _update_metrics(self, log_entry: Dict[str, Any]) -> None:
        """Update metrics with data from a log entry"""
        self.metrics['total_transactions'] += 1
        
        # Status code distribution
        self.metrics['status_code_distribution'][log_entry['status_code']] += 1
        
        # Error counts by status code
        if log_entry['is_error']:
            self.metrics['error_counts'][log_entry['status_code']] += 1
        
        # Service-specific metrics
        service = log_entry['service_name']
        self.metrics['service_metrics'][service]['count'] += 1
        self.metrics['service_metrics'][service]['response_times'].append(log_entry['response_time_ms'])
        
        if log_entry['is_error']:
            self.metrics['service_metrics'][service]['errors'] += 1
            
        # User activity
        self.metrics['user_activity'][log_entry['user_id']] += 1
        
        # Hourly distribution
        hour = log_entry['datetime'].hour
        self.metrics['hourly_distribution'][hour] += 1
    
    def calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate summary metrics from parsed logs"""
        if not self.parsed_logs:
            return {}
            
        total_errors = sum(self.metrics['error_counts'].values())
        error_rate = (total_errors / self.metrics['total_transactions']) * 100
        
        # Calculate average response time overall
        all_response_times = [log['response_time_ms'] for log in self.parsed_logs]
        avg_response_time = sum(all_response_times) / len(all_response_times)
        
        # Calculate service-specific metrics
        service_summary = {}
        for service, data in self.metrics['service_metrics'].items():
            if data['response_times']:
                service_avg_response = sum(data['response_times']) / len(data['response_times'])
                service_error_rate = (data['errors'] / data['count']) * 100
                service_summary[service] = {
                    'total_requests': data['count'],
                    'avg_response_time_ms': round(service_avg_response, 2),
                    'error_count': data['errors'],
                    'error_rate_percent': round(service_error_rate, 2),
                    'min_response_time_ms': min(data['response_times']),
                    'max_response_time_ms': max(data['response_times'])
                }
        
        return {
            'summary': {
                'total_transactions': self.metrics['total_transactions'],
                'total_errors': total_errors,
                'error_rate_percent': round(error_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'unique_users': len(self.metrics['user_activity']),
                'unique_services': len(self.metrics['service_metrics'])
            },
            'error_breakdown': dict(self.metrics['error_counts']),
            'status_code_distribution': dict(self.metrics['status_code_distribution']),
            'service_metrics': service_summary,
            'hourly_distribution': dict(self.metrics['hourly_distribution']),
            'top_active_users': dict(Counter(self.metrics['user_activity']).most_common(10))
        }
    
    def export_to_json(self, output_file: str = None) -> str:
        """Export parsed logs and metrics to JSON format"""
        if not output_file:
            output_file = f"parsed_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        serializable_logs = []
        for log in self.parsed_logs:
            log_copy = log.copy()
            log_copy['datetime'] = log_copy['datetime'].isoformat()
            serializable_logs.append(log_copy)
        
        export_data = {
            'metadata': {
                'source_file': self.log_file_path,
                'parsed_at': datetime.now().isoformat(),
                'total_log_entries': len(self.parsed_logs)
            },
            'metrics': self.calculate_summary_metrics(),
            'logs': serializable_logs
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Exported parsed logs to: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python log_parser.py <log_file_path> [output_json_file]")
        sys.exit(1)
    
    log_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize parser
    parser = LogParser(log_file)
    
    # Parse logs
    print(f"Parsing log file: {log_file}")
    parsed_logs = parser.parse_logs()
    print(f"Successfully parsed {len(parsed_logs)} log entries")
    
    # Calculate and display metrics
    metrics = parser.calculate_summary_metrics()
    
    print("\n" + "="*50)
    print("LOG ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total Transactions: {metrics['summary']['total_transactions']}")
    print(f"Total Errors: {metrics['summary']['total_errors']}")
    print(f"Error Rate: {metrics['summary']['error_rate_percent']}%")
    print(f"Average Response Time: {metrics['summary']['avg_response_time_ms']}ms")
    print(f"Unique Users: {metrics['summary']['unique_users']}")
    print(f"Unique Services: {metrics['summary']['unique_services']}")
    
    print("\nError Breakdown by Status Code:")
    for status_code, count in metrics['error_breakdown'].items():
        print(f"  {status_code}: {count} errors")
    
    print("\nService Performance:")
    for service, data in metrics['service_metrics'].items():
        print(f"  {service}:")
        print(f"    Requests: {data['total_requests']}")
        print(f"    Avg Response Time: {data['avg_response_time_ms']}ms")
        print(f"    Error Rate: {data['error_rate_percent']}%")
    
    # Export to JSON
    json_file = parser.export_to_json(output_file)
    if json_file:
        print(f"\nStructured data exported to: {json_file}")


if __name__ == "__main__":
    main()