import re

debug_flag = True  # Set this to True to enable debug output

# Subroutine 1: Match the date
def match_date(input_string):
    pattern = r"(?P<date>\w+\s+\d+\s+\d{2}:\d{2}:\d{2})\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 2: Match and consume 'ip-xxx'
def match_ip(input_string):
    pattern = r"[ \t]*ip-[0-9]+-[0-9]+-[0-9]+-[0-9]+[ \t]*"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, {}, match.end()
    return False, {}, 0

# Subroutine 3: Match the jail
def match_jail(input_string):
    pattern = r"(?P<jail>[a-zA-Z0-9]+)\[\d+\]:\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 4: Match the phrase 'Invalid user guest from' and capture the user
def match_user(input_string):
    pattern = r"Invalid\s+user\s+(?P<user>\w+)\s+from\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 5: Match the IP address
def match_ip_address(input_string):
    pattern = r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Subroutine 6: Match the port number
def match_port(input_string):
    pattern = r"port\s+(?P<port>\d+)\s*"
    match = re.match(pattern, input_string, re.VERBOSE)
    if match:
        return True, match.groupdict(), match.end()
    return False, {}, 0

# Array of function pointers for subroutines
subroutines = [
    match_date,
    match_ip,
    match_jail,
    match_user,
    match_ip_address,
    match_port
]

# Main function to apply subroutines
def apply_subroutines(input_string):
    extracted_data = {}  # Dictionary to hold extracted variables
    current_string = input_string

    for i, subroutine in enumerate(subroutines, 1):
        if debug_flag:
            print(f"\nRemainder of input before step {i}: {current_string}")
            print(f"Testing subroutine {i}: {subroutine.__name__}")

        # Apply the subroutine
        match_found, vars_extracted, match_end = subroutine(current_string)

        if match_found:
            # Update the extracted_data dictionary
            extracted_data.update(vars_extracted)

            # Print debug information only if debug_flag is enabled
            if debug_flag:
                print(f"Subroutine {i} matched: {vars_extracted}")
                print(f"Remainder of input after this match: {current_string[match_end:].strip()}")

            # Update the current string to the remainder of the input
            current_string = current_string[match_end:].strip()
        else:
            if debug_flag:
                print(f"Subroutine {i} failed")
            break

    # Return the final extracted data
    return extracted_data

# Sample input log message
log_message = "Sep 11 11:59:55 ip-172-26-10-222 sshd[137445]: Invalid user guest from 121.202.195.103 port 17284"

# Apply the subroutines and display the final extracted data
extracted_data = apply_subroutines(log_message)
print("\nFinal Extracted Data:")
print(extracted_data)

