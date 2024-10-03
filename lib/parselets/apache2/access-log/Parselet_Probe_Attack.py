import re
import json
#import ipaddress

#
# handle lines of the form 65.49.1.73 - - [03/Oct/2024:14:35:17 +0000] "\x16\x03\x01" 400 488 "-" "-"
#
# See README-probe-attack.md for details
#

class Parselet_Probe_Attack:
    def __init__(self):
        pass

    def compress_line(self, log_line):
        # Regex pattern to extract IP address, timestamp, HTTP method, requested file, response code, bytes sent, and user agent
        # Regular expression pattern
        pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]*)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"'
        # 65.49.1.73 - - [03/Oct/2024:14:35:17 +0000] "\x16\x03\x01" 400 488 "-" "-"
        
        match = re.search(pattern, log_line)

        # Group 1: 65.49.1.73
        # Group 2: -
        # Group 3: -
        # Group 4: 03/Oct/2024:14:35:17 +0000
        # Group 5: \x16\x03\x01
        # Group 6: 400
        # Group 7: 488
        # Group 8: -
        # Group 9: -

        # good for debugging
        if False:
            if match:
                for i, group in enumerate(match.groups(), 1):
                    print(f"Group {i}: {group}")
                else:
                    print("No match found.")

        if match:
            ip_address = match.group(1)        # ip address
            timestamp = match.group(4)         # Extract timestamp
            http_method = 'Probe_Attack'       # say what we think
            requested_file = match.group(5)    # Extract requested file
            response_code = None               # None
            bytes_sent = match.group(6)        # Extract bytes sent (841)
            user_agent = match.group(7)        # Extract user agent (Go-http-client/1.1)

            # Create the compressed string by replacing the extracted parts with placeholders
            compressed_log = log_line
            compressed_log = compressed_log.replace(ip_address, "<ip-address>")
            compressed_log = compressed_log.replace(timestamp, "<timestamp>")
            compressed_log = compressed_log.replace(requested_file, "<requested_file>")
            compressed_log = compressed_log.replace(bytes_sent, "<bytes_sent>")
            compressed_log = compressed_log.replace(user_agent, "<user_agent>")

            # Build JSON output
            output = {
                "class_name": self.__class__.__name__,
                "original_log": log_line,
                "compressed_log": compressed_log,
                "extracted_info": {
                    "ip_address": ip_address,
                    "timestamp": timestamp,
                    "http_method": http_method,
                    "requested_file": requested_file,
                    "response_code": response_code,
                    "bytes_sent": bytes_sent,
                    "user_agent": user_agent
                }
            }
            
            return json.dumps(output, indent=4)  # Return as JSON-formatted string
        else:
            return json.dumps({
                "class_name": self.__class__.__name__, 
                "error": "No match found"
            })

if __name__ == "__main__":
    log_lines = (
        '2602:80d:1002::18 - - [03/Oct/2024:14:13:04 +0000] "PRI * HTTP/2.0" 400 488 "-" "-"',
        '154.213.187.244 - - [03/Oct/2024:14:28:01 +0000] "CONNECT google.com:443 HTTP/1.1" 200 569 "-" "Go-http-client/1.1"',
        '154.213.187.244 - - [03/Oct/2024:14:28:01 +0000] "\x16\x03\x01" 400 488 "-" "-"'
        )

    # Create an instance of the Parselet_Probe_Attack class
    compressor = Parselet_Probe_Attack()

    for log_line in log_lines:
        # Example log line from access.log
        # Compress the log line and print the JSON output
        compressed_json = compressor.compress_line(log_line)
        print(compressed_json)

