import re

def scan_journalctl_log(log_entry):
    # Regex pattern to match both IPv4 and IPv6 addresses and capture the user if present
    regex = (
        r'(?P<date>\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})'  # Date
        r'\s+ip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\s+'      # Skip the "ip-" part
        r'(?P<jail>[a-z]+)\['                          # Jail (only alphabetic characters)
        r'\d+\]:'                                      # Skip the digits inside the brackets
        r'\s+.*?by\s+(?P<host>'                        # Match the "by" part, start capturing host IP
        r'(?P<ipv4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IPv4 address
        r'|(?P<ipv6>[a-fA-F0-9:]+))\s+port'              # or IPv6 address (matches colons and hex)
        r'\s+\d{1,5}'                                   # Port number (1 to 5 digits)
        r'(\s+\[preauth\])?'                            # Optional [preauth] at the end
        r'(?:\s+user\s+(?P<user>\w+))?'                 # Optional user field (e.g., user johndoe)
    )
    
    match = re.search(regex, log_entry)
    
    if not match:
        return False
    
    # Determine whether the matched address is IPv4 or IPv6
    if match.group('ipv4'):
        ip_type = 'IPv4'
        host = match.group('ipv4')
    elif match.group('ipv6'):
        ip_type = 'IPv6'
        host = match.group('ipv6')
    
    # Extract user if present
    user = match.group('user') if match.group('user') else 'Unknown'
    
    # Replace the IP with '<HOST>' in the original string
    updated_log = log_entry.replace(host, '<HOST>')
    
    return {
        'date': match.group('date'),
        'jail': match.group('jail'),
        'host': '<HOST>',
        'ip_type': ip_type,
        'user': user,
        'log': updated_log
    }

# Example usage
log_entries = [
    "Sep 11 10:09:42 ip-172-26-10-222 sshd[133885]: Connection closed by 152.32.252.94 port 34538 [preauth]",
    "Sep 11 10:15:57 ip-172-26-10-222 sshd[134279]: Connection reset by 147.185.132.19 port 65008 [preauth]",
    "Sep 11 10:17:00 ip-172-26-10-222 sshd[134500]: Connection closed by 2001:0db8:85a3:0000:0000:8a2e:0370:7334 port 12345 [preauth]",
    "Sep 11 10:20:00 ip-172-26-10-222 sshd[134501]: Connection closed by 192.168.0.1 port 22 user johndoe"
]

for log in log_entries:
    result = scan_journalctl_log(log)
    if result:
        print(result)
    else:
        print("No IP address found.")

