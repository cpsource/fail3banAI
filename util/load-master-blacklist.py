import os
import sys
from IpSet import IpSet

def ensure_root():
    """Check if the script is running as root"""
    if os.geteuid() != 0:
        print("Error: This script must be run as root.")
        sys.exit(1)

def load_master_blacklist():
    # Ensure the script is running as root
    ensure_root()

    # Get the project root from the environment variable
    project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
    if not project_root:
        raise EnvironmentError("Environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")

    # Path to the master-blacklist.ctl file
    blacklist_file = os.path.join(project_root, 'ufw-blocklist', 'master-blacklist.ctl')

    # Check if master-blacklist.ctl exists
    if not os.path.exists(blacklist_file):
        print(f"Error: {blacklist_file} does not exist.")
        return

    # Initialize IpSet
    ipset_manager = IpSet()

    # Counters
    already_present_count = 0
    added_count = 0
    line_no = 0  # Line number tracker

    try:
        # Open the blacklist file
        with open(blacklist_file, 'r') as file:
            for line in file:
                line_no += 1

                # Print progress for every 500 lines processed
                if line_no % 500 == 0:
                    print(f"Processing {line_no}...")

                # Strip whitespace and skip comments
                clean_line = line.split('#')[0].strip()

                # If the line contains an IP address
                if clean_line:
                    ip_address = clean_line
                    # Test if the IP address is already in the set
                    if ipset_manager.test(ip_address):
                        already_present_count += 1
                    else:
                        # Add the IP address if not present
                        ipset_manager.add(ip_address)
                        added_count += 1

        # Report results
        print(f"Processing complete.")
        print(f"IP addresses already present: {already_present_count}")
        print(f"IP addresses added: {added_count}")

    except FileNotFoundError:
        print(f"Error: {blacklist_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function when executed
if __name__ == "__main__":
    load_master_blacklist()

