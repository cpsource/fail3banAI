import re

# Dictionary to store subroutines
subroutine_dict = {}

# Function to read and parse the match-subs.ctl file
def read_subs_file(filename):
    subroutines = {}
    current_subroutine_name = None
    current_pattern = None
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[subroutine:"):
                # Save previous subroutine if one exists
                if current_subroutine_name and current_pattern:
                    subroutines[current_subroutine_name] = current_pattern
                # Start a new subroutine
                current_subroutine_name = line.split(":")[1].strip(" ]")
                current_pattern = ""
            elif current_subroutine_name and line:
                # Append lines to the current subroutine pattern
                current_pattern += line + "\n"
        # Add the last subroutine if needed
        if current_subroutine_name and current_pattern:
            subroutines[current_subroutine_name] = current_pattern.strip()
    return subroutines

# Function to dynamically create subroutines from the loaded patterns
def create_subroutine(name, pattern):
    def subroutine(input_string):
        match = re.match(pattern, input_string, re.VERBOSE)
        if match:
            return True, match.groupdict(), match.end()
        return False, {}, 0
    subroutine_dict[name] = subroutine

# Function to read and parse the match-chains.ctl file
def read_chains_file(filename):
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

# Read the match-subs.ctl file and create the subroutines
subs_filename = "match-subs.ctl"
subroutine_patterns = read_subs_file(subs_filename)

# Create the subroutines dynamically
for name, pattern in subroutine_patterns.items():
    create_subroutine(name, pattern)

# Read the match-chains.ctl file
chains_filename = "match-chains.ctl"
subroutine_chains = read_chains_file(chains_filename)

# Sample log entry (Invalid user scenario)
log_entry_1 = "Sep 12 09:15:45 ip-172-30-10-222 sshd[24568]: Invalid user guest from 192.168.0.10 port 52222"

# Sample log entry (Connection closed scenario)
log_entry_2 = "Sep 12 09:16:12 ip-172-30-10-222 sshd[24568]: Connection closed by invalid user guest 192.168.0.10 port 52222"

# Sample log entry (match_user_not_allowed)
log_entry_3 ="Sep 12 02:30:06 ip-172-26-10-222 sshd[147882]: User nobody from 65.20.164.43 not allowed because not listed in AllowUsers"

# Apply the dynamic subroutines based on the ctl file
print("\n--- Processing log_entry_1 (invalid_user) ---")
apply_dynamic_subroutines(log_entry_1, "invalid_user", subroutine_chains)

print("\n--- Processing log_entry_2 (connection_closed) ---")
apply_dynamic_subroutines(log_entry_2, "connection_closed", subroutine_chains)

print("\n--- Processing log_entry_3 (user_not_allowed) ---")
apply_dynamic_subroutines(log_entry_3, "block_nobody_user", subroutine_chains)


