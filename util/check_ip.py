import sys
from hashed_set import hashed_set  # Import the hashed_set from the generated file

# Check if an IP address was provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python3 check_ip.py <ip_address>")
    sys.exit(1)

# Get the IP address from the first command-line argument
ip_address = sys.argv[1]

# Check if the IP address is in the hashed_set
if ip_address in hashed_set:
    print(f"{ip_address} is in the hashed set.")
else:
    print(f"{ip_address} is NOT in the hashed set.")

