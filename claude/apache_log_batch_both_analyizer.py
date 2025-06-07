#!/usr/bin/env python3
"""
Apache Log Batch Analyzer

This script processes multiple Apache log files (access.log, error.log, etc.)
and performs comprehensive security analysis across all of them.

Think of this as a security analyst's daily briefing tool - it examines all your
log files and gives you a complete picture of what's been happening on your server.
"""

import os
import gzip
import glob
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import argparse

def get_log_parser(log_type):
    """
    Import the appropriate parser based on log type.
    
    This is like having specialized translators for different languages -
    access logs and error logs have completely different formats.
    """
    if log_type == 'access':
        try:
            from access_log_parser import parse_access_log
            return parse_access_log
        except ImportError:
            print("ERROR: access_log_parser.py not found. Please ensure it's in the same directory.")
            sys.exit(1)
    elif log_type == 'error':
        try:
            from error_log_parser import parse_error_log
            return parse_error_log
        except ImportError:
            print("ERROR: error_log_parser.py not found. Please ensure it's in the same directory.")
            sys.exit(1)
    else:
        print(f"ERROR: Unknown log type '{log_type}'. Use 'access' or 'error'.")
        sys.exit(1)

def find_log_files(base_path=".", log_pattern="access.log"):
    """
    Find all Apache log files in the specified directory.
    
    This is like a librarian cataloging books - we find the main log file
    plus all the numbered/compressed versions.
    
    Args:
        base_path: Directory to search for log files
        log_pattern: Base name pattern (e.g., "access.log", "error.log")
    
    Returns:
        List of log file paths, sorted by recency (newest first)
    """
    log_files = []
    
    # Check for main log file
    main_log = os.path.join(base_path, log_pattern)
    if os.path.exists(main_log):
        log_files.append(main_log)
    
    # Check for rotated log files (.1, .2, .3, etc.)
    pattern = os.path.join(base_path, f"{log_pattern}.*")
    rotated_files = glob.glob(pattern)
    
    # Sort by the rotation number (extract number from filename)
    def extract_rotation_number(filename):
        try:
            # Extract number from patterns like access.log.1.gz or access.log.2
            parts = filename.split('.')
            for i, part in enumerate(parts):
                if part.isdigit():
                    return int(part)
            return 0
        except:
            return 999  # Put unrecognized files at the end
    
    rotated_files.sort(key=extract_rotation_number)
    log_files.extend(rotated_files)
    
    return log_files

def read_log_file(filepath):
    """
    Read log file, handling both plain text and gzipped files.
    
    This is like having a universal document reader - it automatically detects
    if a file is compressed (.gz) and decompresses it on-the-fly.
    
    Args:
        filepath: Path to log file (can be .gz compressed or plain text)
    
    Returns:
        List of log lines as strings
    """
    print(f"    Reading {'compressed' if filepath.endswith('.gz') else 'plain text'} file...")
    
    try:
        if filepath.endswith('.gz'):
            # Handle gzipped files - decompress while reading
            with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print(f"    Decompressed {len(lines):,} lines from {filepath}")
                return lines
        else:
            # Handle plain text files
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print(f"    Read {len(lines):,} lines from {filepath}")
                return lines
    except Exception as e:
        print(f"    ERROR: Could not read {filepath}: {e}")
        return []

def analyze_logs(log_files, max_days=None, log_parser=None):
    """
    Analyze multiple log files and aggregate security intelligence.
    
    This is like having a team of security analysts working together -
    each examines different time periods, then we combine their findings.
    """
    all_entries = []
    file_stats = {}
    
    # Parse all log files
    print("Processing log files...")
    for log_file in log_files:
        print(f"  Reading: {log_file}")
        lines = read_log_file(log_file)
        
        file_entries = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                parsed = log_parser(line)
                if parsed['datetime']:
                    # Filter by date if specified
                    if max_days:
                        cutoff_date = datetime.now() - timedelta(days=max_days)
                        if parsed['datetime'] < cutoff_date:
                            continue
                    
                    file_entries.append(parsed)
                    all_entries.append(parsed)
            except Exception as e:
                print(f"    Warning: Could not parse line {line_num} in {log_file}: {e}")
        
        file_stats[log_file] = {
            'total_lines': len(lines),
            'parsed_entries': len(file_entries),
            'parse_rate': len(file_entries) / len(lines) if lines else 0
        }
    
    return all_entries, file_stats

def generate_security_report(entries, file_stats, log_type):
    """
    Generate comprehensive security analysis report.
    
    This is like a security consultant's executive briefing - it summarizes
    threats, patterns, and recommendations based on all the data.
    """
    if not entries:
        print("No log entries found to analyze.")
        return
    
    print("\n" + "="*80)
    print(f" APACHE {log_type.upper()} LOG SECURITY ANALYSIS REPORT")
    print("="*80)
    
    # Basic statistics
    print(f"\nDATA SUMMARY:")
    print(f"  Total log entries analyzed: {len(entries):,}")
    print(f"  Time range: {min(e['datetime'] for e in entries if e['datetime'])} to {max(e['datetime'] for e in entries if e['datetime'])}")
    
    print(f"\nFILE PROCESSING SUMMARY:")
    for filename, stats in file_stats.items():
        print(f"  {filename}: {stats['parsed_entries']:,}/{stats['total_lines']:,} entries ({stats['parse_rate']:.1%} parsed)")
    
    if log_type == 'error':
        # Error log specific analysis
        _generate_error_log_analysis(entries)
    elif log_type == 'access':
        # Access log specific analysis
        _generate_access_log_analysis(entries)
    
    # Common analysis for both log types
    _generate_common_analysis(entries, log_type)

def _generate_error_log_analysis(entries):
    """Generate analysis specific to error logs."""
    # Error analysis
    error_codes = Counter(e['error_code'] for e in entries if e.get('error_code'))
    modules = Counter(e['module'] for e in entries if e.get('module'))
    log_levels = Counter(e['log_level'] for e in entries if e.get('log_level'))
    
    print(f"\nERROR ANALYSIS:")
    if error_codes:
        print(f"  Top error codes:")
        for code, count in error_codes.most_common(10):
            print(f"    {code}: {count:,} occurrences")
    
    if modules:
        print(f"\n  Affected modules:")
        for module, count in modules.most_common(10):
            print(f"    {module}: {count:,} occurrences")
    
    if log_levels:
        print(f"\n  Log levels:")
        for level, count in log_levels.most_common():
            print(f"    {level}: {count:,} occurrences")
    
    # Attack pattern analysis for error logs
    targeted_files = Counter(e['file_path'] for e in entries if e.get('file_path'))
    
    print(f"\nSECURITY THREAT ANALYSIS:")
    if targeted_files:
        print(f"  Most targeted files/paths:")
        for file_path, count in targeted_files.most_common(15):
            print(f"    {file_path}: {count:,} attempts")
    
    # Decoded attack analysis
    decoded_attacks = [e for e in entries if e.get('error_decoded')]
    if decoded_attacks:
        print(f"\n  DECODED ATTACK PATTERNS ({len(decoded_attacks):,} entries):")
        decoded_patterns = Counter(e['error_decoded'] for e in decoded_attacks)
        for pattern, count in decoded_patterns.most_common(10):
            print(f"    {pattern}: {count:,} times")

def _generate_access_log_analysis(entries):
    """Generate analysis specific to access logs."""
    # HTTP method analysis
    methods = Counter(e['method'] for e in entries if e.get('method'))
    status_codes = Counter(e['status_code'] for e in entries if e.get('status_code'))
    user_agents = Counter(e['user_agent'] for e in entries if e.get('user_agent'))
    
    print(f"\nHTTP REQUEST ANALYSIS:")
    if methods:
        print(f"  HTTP Methods:")
        for method, count in methods.most_common(10):
            print(f"    {method}: {count:,} requests")
    
    if status_codes:
        print(f"\n  Status Codes:")
        for status, count in status_codes.most_common(10):
            print(f"    {status}: {count:,} responses")
    
    # Attack pattern analysis for access logs
    targeted_paths = Counter(e['path'] for e in entries if e.get('path'))
    attack_entries = [e for e in entries if e.get('is_attack')]
    
    print(f"\nSECURITY THREAT ANALYSIS:")
    print(f"  Total requests: {len(entries):,}")
    print(f"  Suspicious/attack requests: {len(attack_entries):,} ({len(attack_entries)/len(entries)*100:.1f}%)")
    
    if targeted_paths:
        print(f"\n  Most requested paths:")
        for path, count in targeted_paths.most_common(15):
            print(f"    {path}: {count:,} requests")
    
    # Attack type analysis
    if attack_entries:
        attack_types = {}
        for entry in attack_entries:
            if entry.get('attack_type'):
                for attack_type in entry['attack_type'].split(', '):
                    attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        print(f"\n  ATTACK TYPES DETECTED:")
        for attack_type, count in sorted(attack_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    {attack_type}: {count:,} attempts")
    
    # Decoded path analysis
    decoded_attacks = [e for e in entries if e.get('path_decoded') and e['path_decoded'] != e.get('path')]
    if decoded_attacks:
        print(f"\n  DECODED ATTACK PATTERNS ({len(decoded_attacks):,} entries):")
        decoded_patterns = Counter(e['path_decoded'] for e in decoded_attacks)
        for pattern, count in decoded_patterns.most_common(10):
            print(f"    {pattern}: {count:,} times")
    
    # Suspicious user agents
    suspicious_agents = [e for e in entries if e.get('user_agent') and 
                        any(sus in e['user_agent'].lower() for sus in ['bot', 'crawler', 'scanner', 'zgrab'])]
    if suspicious_agents:
        print(f"\n  SUSPICIOUS USER AGENTS ({len(suspicious_agents):,} requests):")
        sus_agent_counter = Counter(e['user_agent'] for e in suspicious_agents)
        for agent, count in sus_agent_counter.most_common(10):
            print(f"    {agent[:80]}{'...' if len(agent) > 80 else ''}: {count:,} times")

def _generate_common_analysis(entries, log_type):
    """Generate analysis common to both log types."""
    attacking_ips = Counter(e['client_ip'] for e in entries if e.get('client_ip'))
    
    print(f"\n  Top client IP addresses:")
    for ip, count in attacking_ips.most_common(20):
        print(f"    {ip}: {count:,} requests")
    
    # Time-based analysis
    print(f"\nTIME-BASED ANALYSIS:")
    
    # Group by hour of day
    hourly_requests = defaultdict(int)
    daily_requests = defaultdict(int)
    
    for entry in entries:
        if entry['datetime']:
            hour = entry['datetime'].hour
            date = entry['datetime'].date()
            hourly_requests[hour] += 1
            daily_requests[date] += 1
    
    print(f"  Peak request hours (24-hour format):")
    sorted_hours = sorted(hourly_requests.items(), key=lambda x: x[1], reverse=True)
    for hour, count in sorted_hours[:5]:
        print(f"    {hour:02d}:00 - {count:,} requests")
    
    print(f"\n  Most active days:")
    sorted_days = sorted(daily_requests.items(), key=lambda x: x[1], reverse=True)
    for date, count in sorted_days[:10]:
        print(f"    {date}: {count:,} requests")
    
    # Security recommendations
    _generate_security_recommendations(entries, attacking_ips, log_type)

def _generate_security_recommendations(entries, attacking_ips, log_type):
    """Generate security recommendations based on analysis."""
    print(f"\nSECURITY RECOMMENDATIONS:")
    
    if log_type == 'error':
        # Error log specific recommendations
        sensitive_files = [e.get('file_path') for e in entries if e.get('file_path') and 
                          any(pattern in e['file_path'].lower() for pattern in ['.git', '.env', '.htaccess', 'config', 'backup', '.sql'])]
        
        if sensitive_files:
            print(f"  🔴 CRITICAL: Attacks targeting sensitive files detected!")
            unique_files = list(set(sensitive_files))
            print(f"     Consider blocking access to: {', '.join(unique_files[:5])}")
            
            # Get IPs attacking sensitive files
            sensitive_attackers = set()
            for entry in entries:
                if entry.get('file_path') and any(pattern in entry['file_path'].lower() for pattern in ['.git', '.env', '.htaccess', 'config', 'backup', '.sql']):
                    if entry.get('client_ip'):
                        sensitive_attackers.add(entry['client_ip'])
            
            if sensitive_attackers:
                top_sensitive_attackers = [ip for ip, count in attacking_ips.most_common() if ip in sensitive_attackers][:10]
                print(f"     🔴 CRITICAL: Block IPs targeting sensitive files: {', '.join(top_sensitive_attackers)}")
        
        # Check for directory traversal in error logs
        traversal_attacks = [e for e in entries if e.get('error_decoded') and '..' in e['error_decoded']]
        if traversal_attacks:
            print(f"  🔴 CRITICAL: {len(traversal_attacks):,} directory traversal attacks detected!")
            print(f"     Implement stronger input validation and path sanitization.")
            
            traversal_attackers = set(e['client_ip'] for e in traversal_attacks if e.get('client_ip'))
            if traversal_attackers:
                top_traversal_attackers = [ip for ip, count in attacking_ips.most_common() if ip in traversal_attackers][:10]
                print(f"     🔴 CRITICAL: Block IPs performing directory traversal: {', '.join(top_traversal_attackers)}")
    
    elif log_type == 'access':
        # Access log specific recommendations
        attack_entries = [e for e in entries if e.get('is_attack')]
        
        if attack_entries:
            print(f"  🔴 CRITICAL: {len(attack_entries):,} suspicious/attack requests detected!")
            
            # Get top attacking IPs
            attack_ips = Counter(e['client_ip'] for e in attack_entries if e.get('client_ip'))
            if attack_ips:
                top_attack_ips = [ip for ip, count in attack_ips.most_common(10)]
                print(f"     🔴 CRITICAL: Block top attacking IPs: {', '.join(top_attack_ips)}")
        
        # Check for directory traversal in access logs
        traversal_attacks = [e for e in entries if e.get('path_decoded') and '..' in e.get('path_decoded', '')]
        if traversal_attacks:
            print(f"  🔴 CRITICAL: {len(traversal_attacks):,} directory traversal attempts detected!")
            
            traversal_ips = set(e['client_ip'] for e in traversal_attacks if e.get('client_ip'))
            if traversal_ips:
                top_traversal_ips = [ip for ip, count in attacking_ips.most_common() if ip in traversal_ips][:10]
                print(f"     🔴 CRITICAL: Block IPs performing directory traversal: {', '.join(top_traversal_ips)}")
    
    # Common recommendations
    if attacking_ips:
        top_attackers = [ip for ip, count in attacking_ips.most_common(5) if count > 50]
        if top_attackers:
            print(f"  🟡 MODERATE: Consider blocking high-volume clients: {', '.join(top_attackers)}")
    
    print(f"\n  ✅ GOOD: Log monitoring is active and capturing {'attack attempts' if log_type == 'error' else 'web requests'}.")
    print(f"  ✅ GOOD: Server is responding to requests and logging activity.")

def main():
    """Main execution function with command-line interface."""
    parser = argparse.ArgumentParser(description='Analyze Apache log files for security threats')
    parser.add_argument('--log-dir', default='/var/log/apache2', help='Directory containing log files (default: /var/log/apache2)')
    parser.add_argument('--log-type', choices=['access', 'error'], default='error', 
                       help='Type of log to analyze: access or error (default: error)')
    parser.add_argument('--prefix', default='', 
                       help='Log file prefix (e.g., "ssl" for ssl-error.log or "site1" for site1-access.log)')
    parser.add_argument('--days', type=int, help='Only analyze entries from the last N days')
    parser.add_argument('--output', help='Save report to file instead of printing to console')
    
    args = parser.parse_args()
    
    # Determine log pattern based on log type and prefix
    if args.prefix:
        log_pattern = f'{args.prefix}-access.log' if args.log_type == 'access' else f'{args.prefix}-error.log'
    else:
        log_pattern = 'access.log' if args.log_type == 'access' else 'error.log'
    
    # Get the appropriate parser
    log_parser = get_log_parser(args.log_type)
    
    # Find all log files
    log_files = find_log_files(args.log_dir, log_pattern)
    
    if not log_files:
        print(f"No log files found matching pattern '{log_pattern}' in '{args.log_dir}'")
        print(f"Available log files in directory:")
        try:
            all_files = os.listdir(args.log_dir)
            log_like_files = [f for f in all_files if 'log' in f.lower()]
            for f in sorted(log_like_files):
                print(f"  {f}")
        except:
            pass
        sys.exit(1)
    
    print(f"Found {len(log_files)} {args.log_type} log files (pattern: {log_pattern}):")
    for log_file in log_files:
        size = os.path.getsize(log_file) / (1024*1024)  # Size in MB
        print(f"  {log_file} ({size:.4f} MB)")
    
    # Analyze logs
    entries, file_stats = analyze_logs(log_files, args.days, log_parser)
    
    # Generate report
    if args.output:
        # Redirect output to file
        import sys
        original_stdout = sys.stdout
        with open(args.output, 'w') as f:
            sys.stdout = f
            generate_security_report(entries, file_stats, args.log_type)
        sys.stdout = original_stdout
        print(f"Report saved to: {args.output}")
    else:
        generate_security_report(entries, file_stats, args.log_type)

if __name__ == "__main__":
    main()
