#process = subprocess.Popen(['journalctl', '-f', '-u', 'sshd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

import re

def extract_log_details(log_entry):
    """
    Extracts user name, IP address, and port number from a log entry.

    Parameters:
        log_entry (str): The log entry string to be parsed.

    Returns:
        dict or None: A dictionary containing 'user_name', 'ip_address',
                      and 'port_number' if the log entry matches the pattern.
                      Returns None if no match is found.
    """
    # Define the regex pattern with named capturing groups
    pattern = re.compile(
        r"Invalid\s+"
        r"user\s+(?P<user_name>\S+)\s+"
        r"from\s+(?P<ip_address>\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"port\s+(?P<port_number>\d+)\."
    )

    # Search for a match in the log entry
    match = pattern.search(log_entry)

    if match:
        # Extract the named groups into a dictionary
        return {
            'user_name': match.group('user_name'),
            'ip_address': match.group('ip_address'),
            'port_number': match.group('port_number')
        }
    else:
        # Return None if no match is found
        return None

def main():
    # Example log entry
    log_entry = "Invalid user user1 from 85.159.164.28 port 40567."

    # Extract details from the log entry
    details = extract_log_details(log_entry)

    if details:
        print(f"User Name : {details['user_name']}")
        print(f"IP Address: {details['ip_address']}")
        print(f"Port Number: {details['port_number']}")
    else:
        print("No match found.")

if __name__ == "__main__":
    main()

