import re

# Dictionary to store subroutines
subroutine_dict = {}

# Subroutine 1: Match date
def match_date(input_string):
    pattern = r"(?P<date>\w+\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 2: Match IP (e.g., 'ip-xxx-xxx-xxx-xxx')
def match_ip(input_string):
    pattern = r"[ \t]*ip-[0-9]+-[0-9]+-[0-9]+-[0-9]+[ \t]*"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, {}, match.end()
    return False, {}, 0

# Subroutine 3: Match jail (e.g., 'sshd[12345]:')
def match_jail(input_string):
    pattern = r"(?P<jail>[a-zA-Z0-9]+)\[\d+\]:\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 4a: Match 'Connection closed by invalid user' and capture user
def match_user_connection_closed(input_string):
    pattern = r"Connection\s+closed\s+by\s+invalid\s+user\s+(?P<user>\w+)"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 4b: Match 'Invalid user guest from' and capture user
def match_user_invalid_user(input_string):
    pattern = r"Invalid\s+user\s+(?P<user>\w+)\s+from\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 5: Match the IP address (e.g., '192.168.0.10')
def match_ip_address(input_string):
    pattern = r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 6: Match the port number (e.g., 'port 52222')
def match_port(input_string):
    pattern = r"port\s+(?P<port>\d+)\s*"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Function to read and parse the match-chains.ctl file
def read_ctl_file(filename):
    subroutine_chains = {}
    current_subroutine_name = None
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[subroutine:"):
                # Start a new subroutine chain
                current_subroutine_name = line.split(":")[1].strip(" ]")
                subroutine_chains[current_subroutine_name] = []
            elif current_subroutine_name and line:
                # Add subroutines to the current chain
                subroutine_chains[current_subroutine_name].append(line)
    return subroutine_chains

# Apply the subroutines dynamically based on the ctl file
def apply_dynamic_subroutines(log_entry, subroutine_type, subroutine_chains):
    if subroutine_type not in subroutine_chains:
        print(f"No subroutine chain found for type {subroutine_type}.")
        return

    subroutine_chain = subroutine_chains[subroutine_type]
    extracted_data = {}  # Hold the parsed information
    current_string = log_entry

    for subroutine_name in subroutine_chain:
        subroutine = subroutine_dict.get(subroutine_name)
        if not subroutine:
            print(f"Subroutine {subroutine_name} not found.")
            return
        
        match_found, vars_extracted, match_end = subroutine(current_string)
        
        if match_found:
            extracted_data.update(vars_extracted)
            current_string = current_string[match_end:].strip()
        else:
            print(f"Failed to match using {subroutine_name}.")
            break
    
    print("Extracted Data:", extracted_data)

# Initialize the dictionary with known subroutines
subroutine_dict = {
    "match_date": match_date,
    "match_ip": match_ip,
    "match_jail": match_jail,
    "match_user_connection_closed": match_user_connection_closed,
    "match_user_invalid_user": match_user_invalid_user,
    "match_ip_address": match_ip_address,
    "match_port": match_port
}

# Read the match-chains.ctl file
ctl_filename = "match-chains.ctl"
subroutine_chains = read_ctl_file(ctl_filename)

# Sample log entry (Invalid user scenario)
log_entry_1 = "Sep 12 09:15:45 ip-172-30-10-222 sshd[24568]: Invalid user guest from 192.168.0.10 port 52222"

# Sample log entry (Connection closed scenario)
log_entry_2 = "Sep 12 09:16:12 ip-172-30-10-222 sshd[24568]: Connection closed by invalid user guest 192.168.0.10 port 52222"

# Apply the dynamic subroutines based on the ctl file
print("\n--- Processing log_entry_1 (invalid_user) ---")
apply_dynamic_subroutines(log_entry_1, "invalid_user", subroutine_chains)

print("\n--- Processing log_entry_2 (connection_closed) ---")
apply_dynamic_subroutines(log_entry_2, "connection_closed", subroutine_chains)

