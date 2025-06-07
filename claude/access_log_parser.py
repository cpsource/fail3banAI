from datetime import datetime
from typing import Dict, Optional
import re
import urllib.parse

def parse_access_log(log_line: str) -> Dict[str, Optional[str]]:
    """
    Parse Apache access log entries into structured dictionary.
    
    Think of this like reading a guest book - each line tells us who visited,
    when they came, what they wanted, and how the server responded.
    
    Format: IP - - [timestamp] "METHOD /path HTTP/version" status size "referer" "user-agent"
    
    Args:
        log_line: Raw Apache access log line
        
    Returns:
        Dictionary with parsed components
    """
    result = {
        'client_ip': None,
        'timestamp': None,
        'datetime': None,
        'method': None,
        'path': None,
        'path_decoded': None,
        'http_version': None,
        'status_code': None,
        'response_size': None,
        'referer': None,
        'user_agent': None,
        'is_attack': False,
        'attack_type': None,
        'raw_line': log_line
    }
    
    # Use regex to parse the common log format
    # Pattern matches: IP - - [timestamp] "METHOD /path HTTP/version" status size "referer" "user-agent"
    pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d+) (\S+) "([^"]*)" "([^"]*)"'
    
    match = re.match(pattern, log_line)
    if not match:
        # Try to handle malformed requests (like SSL handshakes)
        simple_pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d+) (\S+)'
        simple_match = re.match(simple_pattern, log_line)
        if simple_match:
            result['client_ip'] = simple_match.group(1)
            result['timestamp'] = simple_match.group(2)
            result['method'] = simple_match.group(3)
            result['status_code'] = simple_match.group(4)
            result['response_size'] = simple_match.group(5)
        return result
    
    # Extract basic fields
    result['client_ip'] = match.group(1)
    result['timestamp'] = match.group(2)
    request_line = match.group(3)
    result['status_code'] = match.group(4)
    result['response_size'] = match.group(5) if match.group(5) != '-' else None
    result['referer'] = match.group(6) if match.group(6) != '-' else None
    result['user_agent'] = match.group(7) if match.group(7) != '-' else None
    
    # Parse timestamp
    try:
        # Format: 07/Jun/2025:00:08:12 +0000
        dt = datetime.strptime(result['timestamp'], "%d/%b/%Y:%H:%M:%S %z")
        result['datetime'] = dt.replace(tzinfo=None)  # Remove timezone for simpler handling
    except ValueError:
        pass
    
    # Parse request line (METHOD /path HTTP/version)
    if request_line:
        request_parts = request_line.split(' ')
        if len(request_parts) >= 2:
            result['method'] = request_parts[0]
            result['path'] = request_parts[1]
            if len(request_parts) >= 3:
                result['http_version'] = request_parts[2]
        
        # Decode URL-encoded paths
        if result['path']:
            decoded_path = _decode_url_encoded_string(result['path'])
            if decoded_path != result['path']:
                result['path_decoded'] = decoded_path
    
    # Analyze for security threats
    _analyze_security_threats(result)
    
    return result

def _decode_url_encoded_string(text: str) -> str:
    """
    Decode URL-encoded strings, handling malformed double encoding patterns.
    
    This is like having a forensic analyst's toolkit - attackers sometimes create
    malformed encodings. We need to interpret their actual intent.
    
    Example: /icons/.%%32%65/.%%32%65/ should become /icons/../../
    """
    if not text or '%' not in text:
        return text
    
    decoded = text
    
    # Handle malformed double encoding (%%XX format)
    # Treat %%XX as if it were %XX (the %% is likely a mistake)
    if '%%' in decoded:
        # Replace %%XX with %XX (treat double % as single %)
        decoded = re.sub(r'%%([0-9a-fA-F]{2})', r'%\1', decoded)
    
    # Now handle standard URL encoding (%XX format)
    try:
        # urllib.parse.unquote handles standard %XX encoding
        decoded = urllib.parse.unquote(decoded)
        
        # Additional step: look for remaining hex patterns that should be decoded
        # This handles cases where we now have patterns like "2e2e" or ".2e."
        decoded = _decode_remaining_hex_patterns(decoded)
        
        return decoded
    except Exception:
        return decoded

def _decode_remaining_hex_patterns(text: str) -> str:
    """
    Decode remaining hex patterns after URL decoding.
    
    This handles cases where we have patterns like:
    - .2e. -> ..
    - 2e2e -> ..
    - Any standalone hex values that represent ASCII characters
    """
    if not text:
        return text
    
    # Look for hex patterns in the context of file paths
    # Pattern 1: .XX. where XX is hex for a character (like .2e. -> ..)
    text = re.sub(r'\.([0-9a-fA-F]{2})\.', lambda m: '.' + chr(int(m.group(1), 16)) + '.', text)
    
    # Pattern 2: /XX/ where XX is hex (like /2e/ -> /./)
    text = re.sub(r'/([0-9a-fA-F]{2})/', lambda m: '/' + chr(int(m.group(1), 16)) + '/', text)
    
    # Pattern 3: Sequences of hex pairs like 2e2e -> ..
    def hex_sequence_replacer(match):
        hex_string = match.group(0)
        result = ""
        
        # Process pairs of hex digits
        for i in range(0, len(hex_string), 2):
            if i + 1 < len(hex_string):
                hex_pair = hex_string[i:i+2]
                try:
                    ascii_char = chr(int(hex_pair, 16))
                    # Only include printable ASCII characters that make sense in paths
                    if 32 <= ord(ascii_char) <= 126:
                        result += ascii_char
                    else:
                        result += hex_pair  # Keep original if not printable
                except ValueError:
                    result += hex_pair  # Keep original if invalid hex
            else:
                result += hex_string[i]  # Odd character at end
        
        return result
    
    # Look for sequences of hex digits that might be encoded characters
    # Be more aggressive about finding hex patterns in path contexts
    if re.search(r'[0-9a-fA-F]{2,}', text):
        # Replace sequences of 2 or more hex digits
        text = re.sub(r'\b([0-9a-fA-F]{2,})\b', hex_sequence_replacer, text)
    
    return text

def _decode_adjacent_hex_pairs(text: str) -> str:
    """
    Legacy function - now replaced by _decode_remaining_hex_patterns
    """
    return _decode_remaining_hex_patterns(text)

def _analyze_security_threats(result: Dict) -> None:
    """
    Analyze the request for common security threats and attack patterns.
    
    This is like having a security guard who recognizes suspicious behavior.
    """
    path = result.get('path_decoded') or result.get('path', '')
    user_agent = result.get('user_agent', '')
    method = result.get('method', '')
    status = result.get('status_code', '')
    
    # Common attack indicators
    attack_indicators = []
    
    # Directory traversal attacks
    if path and ('..' in path or '%2e' in path.lower()):
        attack_indicators.append('Directory Traversal')
    
    # Sensitive file access attempts
    sensitive_patterns = ['.env', '.git', '.htaccess', 'config.', 'wp-config', 
                         'admin/', '/login', 'xmlrpc.php', 'wp-login', 'boaform']
    if path and any(pattern in path.lower() for pattern in sensitive_patterns):
        attack_indicators.append('Sensitive File Access')
    
    # SQL injection patterns
    sql_patterns = ['union', 'select', 'drop', 'insert', 'update', 'delete', 'script']
    if path and any(pattern in path.lower() for pattern in sql_patterns):
        attack_indicators.append('Potential SQL Injection')
    
    # Vulnerability scanning
    vuln_patterns = ['/wp-', '/admin', '/login', '/console', '/api/', '/cgi-bin/',
                    'favicon.ico', 'robots.txt', 'sitemap.xml', '/status', '/version']
    if path and any(pattern in path.lower() for pattern in vuln_patterns):
        attack_indicators.append('Vulnerability Scanning')
    
    # Suspicious user agents
    suspicious_agents = ['zgrab', 'masscan', 'nmap', 'nikto', 'sqlmap', 'dirb',
                        'gobuster', 'wpscan', 'scanner', 'bot', 'crawler']
    if user_agent and any(agent in user_agent.lower() for agent in suspicious_agents):
        attack_indicators.append('Suspicious User Agent')
    
    # Protocol attacks (SSL handshakes, malformed requests)
    if method and ('\\x' in method or method in ['PRI', 'OPTIONS', 'CONNECT']):
        attack_indicators.append('Protocol Attack')
    
    # HTTP methods that might indicate attacks
    if method in ['HEAD', 'OPTIONS', 'TRACE', 'CONNECT']:
        attack_indicators.append('Suspicious HTTP Method')
    
    # Error responses that might indicate attacks
    if status in ['400', '403', '404', '405', '500']:
        attack_indicators.append('Error Response')
    
    # Set attack flags
    if attack_indicators:
        result['is_attack'] = True
        result['attack_type'] = ', '.join(attack_indicators)

# Example usage and testing
if __name__ == "__main__":
    # Test with sample access log entries
    test_logs = [
        '182.44.10.67 - - [07/Jun/2025:00:08:12 +0000] "GET / HTTP/1.1" 301 534 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"',
        '148.135.151.193 - - [07/Jun/2025:01:37:49 +0000] "GET /.env HTTP/1.1" 404 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36"',
        '45.131.155.254 - - [07/Jun/2025:00:40:27 +0000] "\\x16\\x03\\x01" 400 488 "-" "-"',
        '103.77.241.50 - - [07/Jun/2025:00:41:02 +0000] "POST /boaform/admin/formLogin HTTP/1.1" 404 493 "http://100.28.189.226:80/admin/login.asp" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"',
        '45.156.129.139 - - [07/Jun/2025:09:41:49 +0000] "HEAD /icons/.%%32%65/.%%32%65/apache2/icons/sphere1.png HTTP/1.1" 400 161 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"',
        '152.42.168.152 - - [07/Jun/2025:05:48:13 +0000] "GET //wp-includes/ID3/license.txt HTTP/1.1" 404 2909 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"'
    ]
    
    print("Apache Access Log Analysis")
    print("=" * 60)
    
    for i, log_line in enumerate(test_logs, 1):
        result = parse_access_log(log_line)
        
        print(f"\nEntry {i}:")
        print(f"  DateTime: {result['datetime'].strftime('%Y-%m-%d %H:%M:%S') if result['datetime'] else 'N/A'}")
        print(f"  Client IP: {result['client_ip']}")
        print(f"  Method: {result['method']}")
        print(f"  Path: {result['path']}")
        if result['path_decoded']:
            print(f"  Decoded Path: {result['path_decoded']}")
        print(f"  Status: {result['status_code']}")
        print(f"  User Agent: {result['user_agent'][:50]}..." if result['user_agent'] and len(result['user_agent']) > 50 else f"  User Agent: {result['user_agent']}")
        if result['is_attack']:
            print(f"  🚨 ATTACK DETECTED: {result['attack_type']}")
    
    print("\n" + "=" * 60)
    print("SECURITY SUMMARY")
    print("=" * 60)
    
    # Analyze all entries
    parsed_logs = [parse_access_log(log) for log in test_logs]
    attacks = [log for log in parsed_logs if log['is_attack']]
    
    print(f"Total requests analyzed: {len(parsed_logs)}")
    print(f"Suspicious/attack requests: {len(attacks)}")
    
    if attacks:
        print(f"\nAttack types detected:")
        attack_types = {}
        for attack in attacks:
            for attack_type in attack['attack_type'].split(', '):
                attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        for attack_type, count in sorted(attack_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {attack_type}: {count} times")
        
        print(f"\nTop attacking IPs:")
        attacking_ips = {}
        for attack in attacks:
            ip = attack['client_ip']
            attacking_ips[ip] = attacking_ips.get(ip, 0) + 1
        
        for ip, count in sorted(attacking_ips.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ip}: {count} attacks")

