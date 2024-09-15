import re

def scan_invalid_user_log(log_entry):
    # Regex pattern to match both IPv4 and IPv6 addresses and capture the invalid user
    regex = (
        r'(?P<date>\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})'  # Date
        r'\s+ip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\s+'      # Skip the "ip-" part
        r'(?P<jail>[a-z]+)\['                          # Jail (only alphabetic characters)
        r'\d+\]:'                                      # Skip the digits inside the brackets
        r'\s+Invalid\s+user\s+(?P<user>\w+)\s+from\s+'  # Capture "Invalid user <user>"
        r'(?P<host>'                                   # Start capturing host IP
        r'(?P<ipv4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IPv4 address
        r'|(?P<ipv6>[a-fA-F0-9:]+))\s+port'              # or IPv6 address
        r'\s+\d{1,5}'                                   # Port number (1 to 5 digits)
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
    
    # Replace the IP with '<HOST>' in the original string
    updated_log = log_entry.replace(host, '<HOST>')
    
    return {
        'date': match.group('date'),
        'jail': match.group('jail'),
        'user': match.group('user'),
        'host': '<HOST>',
        'ip_type': ip_type,
        'log': updated_log
    }

# Example usage
log_entries = [
    "Sep 11 10:25:42 ip-172-26-10-222 sshd[134387]: Invalid user postgres from 116.132.42.170 port 33348",
    "Sep 11 10:26:58 ip-172-26-10-222 sshd[134403]: Invalid user operator from 58.42.84.143 port 56433",
    "Sep 11 10:34:57 ip-172-26-10-222 sshd[134433]: Invalid user blank from 112.26.99.92 port 57715"
]

for log in log_entries:
    result = scan_invalid_user_log(log)
    if result:
        print(result)
    else:
        print("No IP address found.")

