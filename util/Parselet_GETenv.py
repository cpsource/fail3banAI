import re
import json

class Parselet_GETenv:
    def __init__(self):
        pass

    def compress_line(self, log_line):
        # Regex pattern to extract IP address, timestamp, HTTP method, requested file, response code, bytes sent, and user agent
        pattern = r'(\d{1,3}(?:\.\d{1,3}){3}) - - \[(.*?)\] "(GET) (/.+?) HTTP/\d\.\d" (\d{3}) (\d+) ".*?" "(.*?)"'

        match = re.search(pattern, log_line)
        
        if match:
            ip_address = match.group(1)        # Extract IP address
            timestamp = match.group(2)         # Extract timestamp
            http_method = match.group(3)       # Extract HTTP method (GET)
            requested_file = match.group(4)    # Extract requested file (.env)
            response_code = match.group(5)     # Extract response code (302)
            bytes_sent = match.group(6)        # Extract bytes sent (841)
            user_agent = match.group(7)        # Extract user agent (Go-http-client/1.1)

            # Create the compressed string by replacing the extracted parts with placeholders
            compressed_log = log_line
            compressed_log = compressed_log.replace(ip_address, "<ip_address>")
            compressed_log = compressed_log.replace(timestamp, "<timestamp>")
            compressed_log = compressed_log.replace(http_method, "<http_method>")
            compressed_log = compressed_log.replace(requested_file, "<requested_file>")
            compressed_log = compressed_log.replace(response_code, "<response_code>")
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
    # Example log line from access.log
    log_line = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'

    # Create an instance of the Parselet_GETen class
    compressor = Parselet_GETenv()

    # Compress the log line and print the JSON output
    compressed_json = compressor.compress_line(log_line)
    print(compressed_json)

