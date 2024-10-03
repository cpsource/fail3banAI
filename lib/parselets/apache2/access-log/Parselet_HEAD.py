import re
import json
import ipaddress

class Parselet_HEAD:
    def __init__(self):
        pass

    # One might wonder why I broke out the parsing of the ip_address. Well, re can't handle it.
    # This routine performs an additional check on the parsed ip address with the imported
    # module ipaddress
    
    def parse_ipaddress(self, string, starting_position=0):
        # Define the regex pattern for IPv4 and IPv6 addresses
        pattern = r"((?:\d{1,3}\.){3}\d{1,3}|(?:[a-fA-F0-9:]+:+[a-fA-F0-9:]*))"
    
        # Extract the substring starting from the given position
        substring = string[starting_position:]
    
        # Use re.search to find the first occurrence of an IP address
        match = re.search(pattern, substring)
        
        if match:
            ip_candidate = match.group(0)
            try:
                # Validate the found IP address
                ipaddress.ip_address(ip_candidate)
            
                # Calculate the actual position in the original string where the match was found
                start = starting_position + match.start()
                end = starting_position + match.end()
            
                # Replace the IP address in the original string at the specific position
                modified_string = string[:start] + "<ip-address>" + string[end:]
            
                return True, ip_candidate, modified_string  # Return True, IP, and modified string
            except ValueError:
                return False, None, string  # Return False if invalid IP and the original string
        else:
            return False, None, string  # No IP found, return the original string

    def compress_line(self, log_line):
        # Regex pattern to extract IP address, timestamp, HTTP method, requested file, response code, bytes sent, and user agent
        pattern = r' - - \[(.*?)\] "(HEAD) (/.*?) HTTP/\d\.\d" (\d{3}) (\d+) ".*?" "(.*?)"'

        flag , ip_address , compressed_string = self.parse_ipaddress(log_line,0)

        if flag is not True:
            return json.dumps({
                "class_name": self.__class__.__name__, 
                "error": "No match found"
            })

        log_line = compressed_string
        
        match = re.search(pattern, log_line)
        
        if match:
            #ip_address = match.group(2)        # Extract IP address
            timestamp = match.group(1)         # Extract timestamp
            http_method = match.group(2)       # Extract HTTP method (HEAD)
            requested_file = match.group(3)    # Extract requested file (.env)
            response_code = match.group(4)     # Extract response code (302)
            bytes_sent = match.group(5)        # Extract bytes sent (841)
            user_agent = match.group(6)        # Extract user agent (Go-http-client/1.1)

            # Create the compressed string by replacing the extracted parts with placeholders
            compressed_log = log_line
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
    log_line = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "HEAD /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'

    # Create an instance of the Parselet_HEAD class
    compressor = Parselet_HEAD()

    # Compress the log line and print the JSON output
    compressed_json = compressor.compress_line(log_line)
    print(compressed_json)

