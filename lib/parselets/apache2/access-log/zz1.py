import re
import ipaddress

def parse_ipaddress(string, starting_position):
    # Define the regex pattern for IPv4 and IPv6 addresses
    pattern = r"((?:\d{1,3}\.){3}\d{1,3}|(?:[a-fA-F0-9:]+:+[a-fA-F0-9:]*))"
    
    # Extract the substring starting from the given position
    substring = string[starting_position:]
    
    # Use re.search to find the first occurrence of an IP address in the substring
    match = re.search(pattern, substring)
    
    if match:
        ip_candidate = match.group(0)
        try:
            # Validate the found IP address
            ipaddress.ip_address(ip_candidate)
            
            # Adjust the start and end positions relative to the full string
            start = starting_position + match.start() - 1
            end = starting_position + match.end()

            print(start, end)
            
            # Replace the IP address in the original string at the specific position
            modified_string = string[:start] + "<ip-address>" + string[end:]
            
            return True, ip_candidate, modified_string  # Return True, IP, and modified string
        except ValueError:
            return False, None, string  # Return False if invalid IP and the original string
    else:
        return False, None, string  # No IP found, return the original string

# Example usage:
string = "1.1.1.1 Here is an IPv4 address: 192.168.1.1 and an IPv6 address: 2001:0db8:85a3::8a2e:0370:7334 <- and then some"

# Parse the IPv4 address
ipv4_position = 1
ipv4_result = parse_ipaddress(string, ipv4_position)
print(f"IPv4 parse result: {ipv4_result}")  
# Should output: (True, '192.168.1.1', 'Here is an IPv4 address: <ip-address> and an IPv6 address: 2001:0db8:85a3::8a2e:0370:7334')

# Parse the IPv6 address (starting position after IPv4 address)
ipv6_position = 54 + 8
ipv6_result = parse_ipaddress(string, ipv6_position)
print(f"IPv6 parse result: {ipv6_result}")  
# Should output: (True, '2001:0db8:85a3::8a2e:0370:7334', 'Here is an IPv4 address: 192.168.1.1 and an IPv6 address: <ip-address>')

