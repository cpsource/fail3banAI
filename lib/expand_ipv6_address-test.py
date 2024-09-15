import ipaddress

def expand_ip_address(ip_address):
    try:
        # Check if it's an IPv6 address
        ip_obj = ipaddress.ip_address(ip_address)
        
        if isinstance(ip_obj, ipaddress.IPv6Address):
            # It's an IPv6 address, expand it to the full form
            expanded_address = ip_obj.exploded
            return expanded_address
        else:
            # It's an IPv4 address, return as is
            return ip_address
    except ValueError:
        # If the input is not a valid IP address, raise an error
        return None # "Invalid IP address"

# Test the function with IPv6 and IPv4 addresses
ipv6_address = "2001:db8::1"
ipv4_address = "192.168.0.1"
invalid_ip = "invalid_ip"

print(expand_ip_address(ipv6_address))  # Output: 2001:0db8:0000:0000:0000:0000:0000:0001
print(expand_ip_address(ipv4_address))  # Output: 192.168.0.1
print(expand_ip_address(invalid_ip))    # Output: Invalid IP address

