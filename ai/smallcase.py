import re

def extract_ip(log_entry):
    # Define the regex pattern to extract the IP address
    regex = r'by\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    # Search for the pattern in the log entry
    match = re.search(regex, log_entry)

    # If a match is found, return the extracted IP address
    if match:
        return match.group('ip')
    else:
        return None

# Example test case
log_entry = 'Connection closed by 1.2.3.4'
ip_address = extract_ip(log_entry)

print(f"Log Entry: {log_entry}")
print(f"Extracted IP Address: {ip_address}")

