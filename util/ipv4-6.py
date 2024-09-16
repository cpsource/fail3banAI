import socket

def ipv4_to_aaaa(ipv4_address):
    try:
        # Perform a reverse DNS lookup to get the domain name from the IPv4 address
        domain_name = socket.gethostbyaddr(ipv4_address)[0]

        # Perform a forward lookup for the AAAA (IPv6) record of the domain name
        ipv6_address = socket.getaddrinfo(domain_name, None, socket.AF_INET6)

        # Return the IPv6 address from the AAAA record
        return [result[4][0] for result in ipv6_address]
    
    except socket.gaierror as e:
        print(f"Error resolving {ipv4_address}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
ipv6_addresses = ipv4_to_aaaa("8.8.8.8")
print("IPv6 addresses:", ipv6_addresses)

def ipv6_to_a(ipv6_address):
    try:
        # Perform a reverse DNS lookup to get the domain name from the IPv6 address
        domain_name = socket.gethostbyaddr(ipv6_address)[0]

        # Perform a forward lookup for the A (IPv4) record of the domain name
        ipv4_address = socket.getaddrinfo(domain_name, None, socket.AF_INET)

        # Return the IPv4 address from the A record
        return [result[4][0] for result in ipv4_address]

    except socket.gaierror as e:
        print(f"Error resolving {ipv6_address}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
ipv4_addresses = ipv6_to_a("2001:4860:4860::8888")
print("IPv4 addresses:", ipv4_addresses)

