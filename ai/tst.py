import re

def print_string_after_match(log_entry, start):
    # Print the remaining string starting from the given position
    print(f"Remaining string after position {start}: '{log_entry[start:]}'")

def debug_extract_log_details(log_entry):
    # Step-by-step breakdown of regex parts
    regex_parts = [
        ("date", r'(?P<date>\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})'),  # Match and capture the date
        ("ip-skip", r'\s+ip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\s+'),  # Skip the ip-<digits>-<digits>-<digits>-<digits>
        ("jail", r'(?P<jail>\w+)\[\d+\]:'),                        # Match and capture the jail name followed by [digits]:
        ("skip-to-ip", r'(.*?\s+by\s+|.*?\s+from\s+)'),             # Skip until we reach "by" or "from" before the IP address
        ("ip-address", r'(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-fA-F0-9:]+))')  # Match the IP address
    ]
    
    start = 0  # Start position for matching
    extracted_details = {}

    # Step through each regex part and match it
    for part_name, regex in regex_parts:
        match = re.search(regex, log_entry[start:])
        if match:
            print(f"Matched {part_name} at position {start + match.start()} - {start + match.end()}: '{match.group()}'")
            
            # Extract named groups (date, jail, ip) if they exist in this part
            if 'date' in match.groupdict():
                extracted_details['date'] = match.group('date')
            if 'jail' in match.groupdict():
                extracted_details['jail'] = match.group('jail')
            if 'ip' in match.groupdict():
                extracted_details['ip'] = match.group('ip')

            # Move the starting point to after the current match
            start += match.end()

            # Print the remaining string after the current match
            print_string_after_match(log_entry, start)
        else:
            print(f"Failed to match {part_name} after position {start}.")
            break

    return extracted_details if extracted_details else None

# Example usage
log_entries = [
    "Sep 11 10:09:42 ip-172-26-10-222 sshd[133885]: Connection closed by 152.32.252.94 port 34538 [preauth]",
    "Sep 11 10:25:42 ip-172-26-10-222 sshd[134387]: Invalid user postgres from 116.132.42.170 port 33348",
]

for log in log_entries:
    result = debug_extract_log_details(log)
    print(f"Log: {log}\nExtracted Details: {result}\n")

