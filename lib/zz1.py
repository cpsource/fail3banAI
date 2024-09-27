import re
import json

def compress_log_line(log_line):
    # Regex pattern to extract datetime, pid, script, and both IPv4 and IPv6 addresses
    pattern = r"(\[.+?\]) \[.*?\] \[pid (\d+):tid \d+\] .*? xmlrpc\.php\[\d+\]: '(.+?)' executed by ((?:\d{1,3}\.){3}\d{1,3}|[a-fA-F0-9:]+)"

    match = re.search(pattern, log_line)
    
    if match:
        datetime_str = match.group(1)       # Extract datetime
        pid = match.group(2)                # Extract PID
        script = match.group(3)             # Extract script name
        ip_address = match.group(4)         # Extract IP address (IPv4 or IPv6)

        # Create the compressed string by replacing the extracted parts with placeholders
        compressed_log = log_line
        compressed_log = compressed_log.replace(datetime_str, "<datetime>")
        compressed_log = compressed_log.replace(pid, "<pid>")
        compressed_log = compressed_log.replace(script, "<script>")
        compressed_log = compressed_log.replace(ip_address, "<ip_address>")

        # Build JSON output
        output = {
            "original_log": log_line,
            "compressed_log": compressed_log,
            "extracted_info": {
                "datetime": datetime_str,
                "pid": pid,
                "script": script,
                "ip_address": ip_address
            }
        }
        
        return json.dumps(output, indent=4)  # Return as JSON-formatted string
    else:
        return json.dumps({"error": "No match found"})

# Example log line with both IPv4 and IPv6 example
log_line = "[Fri Sep 27 07:32:32.228793 2024] [core:notice] [pid 183991:tid 183991] AH00113: /var/www/html/.htaccess:45 cannot use a full URL in a 401 ErrorDocument directive --- ignoring!  xmlrpc.php[183991]: 'xmlrpc.php' executed by 2602:80d:1006::15."

# Compress the log line and print the JSON output
compressed_json = compress_log_line(log_line)
print(compressed_json)

