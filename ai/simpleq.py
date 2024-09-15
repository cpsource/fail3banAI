import re

log_message = "Invalid user guest from 121.202.195.103 port 17281"
pattern = r"Invalid user (\w+) from (\d{1,3}(?:\.\d{1,3}){3})"

match = re.search(pattern, log_message)
if match:
    user = match.group(1)
    ip_address = match.group(2)
    print(f"User: {user}, IP Address: {ip_address}")
else:
    print("No match found")

