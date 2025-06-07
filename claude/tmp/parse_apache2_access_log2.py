from datetime import datetime
from typing import Dict, Optional
import urllib.parse

def parse_apache_log(log_line: str) -> Dict[str, Optional[str]]:
    """
    Parse Apache error log entries into structured dictionary.
    
    Think of this like dissecting a sentence - we look for the "punctuation marks"
    (brackets) that separate different pieces of information, then extract what's
    between them.
    
    Args:
        log_line: Raw Apache log line
        
    Returns:
        Dictionary with parsed components
    """
    result = {
        'timestamp': None,
        'datetime': None,
        'module': None,
        'log_level': None,
        'pid': None,
        'client_ip': None,
        'client_port': None,
        'error_code': None,
        'error_message': None,
        'error_decoded': None,
        'file_path': None,
        'raw_line': log_line
    }
    
    # Start parsing from the beginning
    pos = 0
    
    # Extract timestamp (first bracketed section)
    if pos < len(log_line) and log_line[pos] == '[':
        end_bracket = log_line.find(']', pos)
        if end_bracket != -1:
            timestamp_str = log_line[pos + 1:end_bracket]
            result['timestamp'] = timestamp_str
            
            # Convert to Python datetime
            try:
                # Parse: "Sat Jun 07 06:18:46.938806 2025"
                dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S.%f %Y")
                result['datetime'] = dt
            except ValueError:
                # Fallback for timestamps without microseconds
                try:
                    dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
                    result['datetime'] = dt
                except ValueError:
                    pass
            
            pos = end_bracket + 1
    
    # Extract module and log level (second bracketed section)
    pos = _skip_whitespace(log_line, pos)
    if pos < len(log_line) and log_line[pos] == '[':
        end_bracket = log_line.find(']', pos)
        if end_bracket != -1:
            module_level = log_line[pos + 1:end_bracket]
            if ':' in module_level:
                module, level = module_level.split(':', 1)
                result['module'] = module.strip()
                result['log_level'] = level.strip()
            else:
                result['module'] = module_level.strip()
            
            pos = end_bracket + 1
    
    # Extract PID (third bracketed section)
    pos = _skip_whitespace(log_line, pos)
    if pos < len(log_line) and log_line[pos] == '[':
        end_bracket = log_line.find(']', pos)
        if end_bracket != -1:
            pid_str = log_line[pos + 1:end_bracket]
            if pid_str.startswith('pid '):
                result['pid'] = pid_str[4:].strip()
            
            pos = end_bracket + 1
    
    # Extract client info (fourth bracketed section)
    pos = _skip_whitespace(log_line, pos)
    if pos < len(log_line) and log_line[pos] == '[':
        end_bracket = log_line.find(']', pos)
        if end_bracket != -1:
            client_str = log_line[pos + 1:end_bracket]
            if client_str.startswith('client '):
                client_info = client_str[7:].strip()
                if ':' in client_info:
                    ip, port = client_info.rsplit(':', 1)
                    result['client_ip'] = ip
                    result['client_port'] = port
                else:
                    result['client_ip'] = client_info
            
            pos = end_bracket + 1
    
    # Extract error message (everything after the brackets)
    pos = _skip_whitespace(log_line, pos)
    if pos < len(log_line):
        remaining_text = log_line[pos:].strip()
        
        # Split error code and message
        parts = remaining_text.split(':', 1)
        if len(parts) >= 2:
            result['error_code'] = parts[0].strip()
            message_part = parts[1].strip()
            
            # Extract file path (usually at the end after the last colon or space)
            # Look for common path patterns
            if '/' in message_part:
                # Find the last part that looks like a file path
                words = message_part.split()
                for word in reversed(words):
                    if '/' in word and (word.startswith('/') or '../' in word):
                        result['file_path'] = word
                        # Remove file path from error message
                        message_part = message_part.replace(word, '').strip()
                        break
            
            result['error_message'] = message_part
            
            # Decode URL-encoded content for clearer analysis
            decoded_message = _decode_url_encoded_string(message_part)
            if decoded_message != message_part:
                result['error_decoded'] = decoded_message
        else:
            result['error_message'] = remaining_text
    
    return result

def _skip_whitespace(text: str, pos: int) -> int:
    """Helper function to skip whitespace characters."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos

def _decode_url_encoded_string(text: str) -> str:
    """
    Decode URL-encoded strings, handling both single (%) and double (%%) encoding.
    
    This is like having a spy decoder - attackers often encode their malicious
    payloads to evade detection, but we can decode them to see what they're
    really trying to do.
    
    Examples:
    - %2e becomes .
    - %%32%65 becomes %2e which then becomes .
    - /%%32%65%%32%65/ becomes /../
    """
    if not text or '%' not in text:
        return text
    
    decoded = text
    
    # Handle double encoding (%%XX format) first
    # This is like peeling an onion - multiple layers of encoding
    while '%%' in decoded:
        # Find all %%XX patterns and convert them to %XX
        import re
        # Replace %%XX with %XX (remove one layer of % encoding)
        decoded = re.sub(r'%%([0-9a-fA-F]{2})', r'%\1', decoded)
    
    # Now handle standard URL encoding (%XX format)
    try:
        # urllib.parse.unquote handles standard %XX encoding
        final_decoded = urllib.parse.unquote(decoded)
        return final_decoded
    except Exception:
        # If decoding fails, return the partially decoded version
        return decoded

# Example usage
if __name__ == "__main__":
    # Real Apache log entries for testing
    test_logs = [
        "[Sat Jun 07 00:06:33.886477 2025] [authz_core:error] [pid 145857] [client 196.251.88.60:51682] AH01630: client denied by server configuration: /var/www/americancentrist/.git/config",
        "[Sat Jun 07 01:28:03.660291 2025] [core:error] [pid 145858] [client 14.103.124.108:36734] AH10244: invalid URI path (/cgi-bin/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/.%2e/bin/sh)",
        "[Sat Jun 07 01:28:08.372068 2025] [core:error] [pid 145963] [client 14.103.124.108:39904] AH10244: invalid URI path (/cgi-bin/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/bin/sh)",
        "[Sat Jun 07 02:28:47.988719 2025] [authz_core:error] [pid 145857] [client 199.45.155.109:54886] AH01630: client denied by server configuration: /var/www/americancentrist/.well-known",
        "[Sat Jun 07 02:35:37.667665 2025] [authz_core:error] [pid 145861] [client 154.203.43.65:44255] AH01630: client denied by server configuration: /var/www/americancentrist/.env",
        "[Sat Jun 07 05:58:09.685538 2025] [authz_core:error] [pid 145858] [client 144.91.89.167:43314] AH01630: client denied by server configuration: /var/www/americancentrist/.git/config",
        "[Sat Jun 07 06:18:46.938806 2025] [authz_core:error] [pid 145857] [client 196.251.85.193:42748] AH01630: client denied by server configuration: /var/www/americancentrist/.git/config",
        "[Sat Jun 07 06:28:34.354950 2025] [authz_core:error] [pid 145861] [client 185.39.8.130:60693] AH01630: client denied by server configuration: /var/www/americancentrist/.env",
        "[Sat Jun 07 08:33:24.618629 2025] [authz_core:error] [pid 798] [client 45.39.7.153:45113] AH01630: client denied by server configuration: /var/www/americancentrist/.env",
        "[Sat Jun 07 10:45:26.191470 2025] [authz_core:error] [pid 806] [client 154.47.28.134:49073] AH01630: client denied by server configuration: /var/www/americancentrist/.env",
        "[Sat Jun 07 11:01:29.659643 2025] [authz_core:error] [pid 804] [client 213.209.143.71:34982] AH01630: client denied by server configuration: /var/www/americancentrist/.env"
    ]
    
    print("Apache Log Analysis")
    print("=" * 60)
    
    for i, log_line in enumerate(test_logs, 1):
        result = parse_apache_log(log_line)
        
        print(f"\nEntry {i}:")
        print(f"  DateTime: {result['datetime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if result['datetime'] else 'N/A'}")
        print(f"  Module: {result['module']}")
        print(f"  Level: {result['log_level']}")
        print(f"  PID: {result['pid']}")
        print(f"  Client: {result['client_ip']}:{result['client_port']}")
        print(f"  Error: {result['error_code']} - {result['error_message']}")
        if result['error_decoded']:
            print(f"  Decoded: {result['error_decoded']}")
        print(f"  Target: {result['file_path']}")
    
    # Summary analysis
    print("\n" + "=" * 60)
    print("SUMMARY ANALYSIS")
    print("=" * 60)
    
    # Parse all logs for analysis
    parsed_logs = [parse_apache_log(log) for log in test_logs]
    
    # Count by error type
    error_codes = {}
    target_files = {}
    client_ips = {}
    
    for entry in parsed_logs:
        # Count error codes
        code = entry['error_code']
        if code:
            error_codes[code] = error_codes.get(code, 0) + 1
        
        # Count target files
        file_path = entry['file_path']
        if file_path:
            target_files[file_path] = target_files.get(file_path, 0) + 1
        
        # Count client IPs
        ip = entry['client_ip']
        if ip:
            client_ips[ip] = client_ips.get(ip, 0) + 1
    
    print(f"Total entries analyzed: {len(parsed_logs)}")
    print(f"\nError codes:")
    for code, count in sorted(error_codes.items()):
        print(f"  {code}: {count} occurrences")
    
    print(f"\nMost targeted files:")
    for file_path, count in sorted(target_files.items(), key=lambda x: x[1], reverse=True):
        print(f"  {file_path}: {count} attempts")
    
    print(f"\nTop attacking IPs:")
    for ip, count in sorted(client_ips.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {ip}: {count} attempts")
