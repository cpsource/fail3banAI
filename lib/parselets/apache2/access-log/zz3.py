import re
import ipaddress

def parse_ipaddress(string, starting_position=0):
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

# Example usage:

# Case where IPv4 address is at the start of the line
string_1 = "192.168.1.1 is the IP address and there is more text here."
ipv4_position = 0  # Start searching from the beginning of the string
ipv4_result = parse_ipaddress(string_1, ipv4_position)
print(f"IPv4 parse result: {ipv4_result}")

# Case where IPv6 address is at the start of the line
string_2 = "2001:0db8:85a3::8a2e:0370:7334 is the IPv6 address and more text here."
ipv6_position = 0  # Start searching from the beginning of the string
ipv6_result = parse_ipaddress(string_2, ipv6_position)
print(f"IPv6 parse result: {ipv6_result}")

# Example string with an IPv4 address at the start and another later in the string
string = "192.168.1.1 is the first IP address and here is another: 10.0.0.5."

# Case where we start scanning at position 26, which is after "192.168.1.1"
starting_position = 26  # Skipping the first IP and scanning for the next

# Call the function to scan from position 26
result = parse_ipaddress(string, starting_position)
print(f"Result: {result}")

