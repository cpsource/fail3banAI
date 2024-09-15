import socket
import re

def ipv6_to_ipv4(ipv6_address):
    # Check if the address is an IPv4-mapped IPv6 address (e.g., ::ffff:192.168.0.1)
    ipv4_mapped_regex = r'::ffff:(?P<ipv4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    
    match = re.match(ipv4_mapped_regex, ipv6_address)
    
    if match:
        # Extract and return the embedded IPv4 address
        return match.group('ipv4')
    
    try:
        # Attempt a reverse DNS lookup for the IPv6 address
        host_info = socket.gethostbyaddr(ipv6_address)
        ipv4_address = socket.gethostbyname(host_info[0])
        
        # Return the resolved IPv4 address if found
        return ipv4_address
    except (socket.herror, socket.gaierror):
        # If no reverse lookup is possible or failed, return None
        return None

# Example usage
ipv6_addresses = [
    '::ffff:192.168.0.1',  # IPv4-mapped IPv6 address
    '2001:0db8:85a3:0000:0000:8a2e:0370:7334',  # Standard IPv6 address
    '2600:1f18:c22:ef00:d7af:7819:8ad0:1ca0',
    '2602:80d:1000::2b',
    '98.97.16.30'
]

for ipv6 in ipv6_addresses:
    result = ipv6_to_ipv4(ipv6)
    if result:
        print(f"IPv6 address {ipv6} maps to IPv4 address: {result}")
    else:
        print(f"IPv6 address {ipv6} could not be mapped to an IPv4 address.")

