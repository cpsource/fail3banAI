import re

def extract_log_details(log_entry):
    # Define the regex pattern to extract date, jail, and IP address
    regex = (
        r'(?P<date>\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})'   # Match and capture the date
        r'\s+ip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\s+'     # Skip the ip-<digits> token
        r'(?P<jail>\w+)\[\d+\]:'                        # Match and capture the jail name followed by [digits]:
        r'.*'                                       # Skip until we reach the actual IP address
        r'(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-fA-F0-9:]+))'  # Capture the IPv4 or IPv6 address
    )

    # Search for the pattern in the log entry
    match = re.search(regex, log_entry)

    # If a match is found, extract the date, jail, and IP
    if match:
        return {
            'date': match.group('date'),
            'jail': match.group('jail'),
            'ip': match.group('ip')
        }
    else:
        return None

# Example usage
log_entries = [
    "Sep 11 10:09:42 ip-172-26-10-222 sshd[133885]: Connection closed by 152.32.252.94 port 34538 [preauth]",
    "Sep 11 10:25:42 ip-172-26-10-222 sshd[134387]: Invalid user postgres from 116.132.42.170 port 33348",
]

for log in log_entries:
    result = extract_log_details(log)
    print(f"Log: {log}\nExtracted Details: {result}\n")

