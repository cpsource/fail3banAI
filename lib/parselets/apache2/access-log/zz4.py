import re

log_entry = '65.49.1.73 - - [03/Oct/2024:14:35:17 +0000] "\\x16\\x03\\x01" 400 488 "-" "-"'

# Regular expression pattern
pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]*)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"'

# Match the log entry against the pattern
match = re.match(pattern, log_entry)

if match:
    for i, group in enumerate(match.groups(), 1):
        print(f"Group {i}: {group}")
else:
    print("No match found.")
