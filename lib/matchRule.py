import re
import sys
from datetime import datetime

class MatchRule:
    def __init__(self):
        self.compiled_regex = None

    def match_rule(self, log_line, jail_regex):
        """Preprocess and match a log line using the jail_regex."""
        # Preprocess the jail_regex to replace <HOST> with the host-matching regex
        jail_regex = jail_regex.replace("<HOST>", r'(?P<host>(?:\d{1,3}\.){3}\d{1,3}|[a-fA-F0-9:]+)')
        
        # Compile the regex if not already compiled
        if self.compiled_regex is None:
            regex_pattern = (
                r'(?P<date>\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})'  # Date part
                r'(\s*)'                                        # Skip 0 or more spaces
                r'[^ ]+'                                        # Skipping ip-<address>
                r'(\s*)'                                        # Skip 0 or more spaces
                r'(?P<jail>\w+)'                                # Jail extraction
                r'\[\d+\]:'                                     # Skip to the colon after the jail
                r'\s+' + jail_regex                             # Apply the provided jail_regex
            )
            self.compiled_regex = re.compile(regex_pattern)
        
        # Match the compiled regex to the log line
        match = self.compiled_regex.match(log_line)

        if match:
            # Safely extract the date group or set to 'n/a' if not found
            date_str = match.group('date') if 'date' in match.groupdict() and match.group('date') else 'n/a'
            print(f"Debug: Extracted date_str = {date_str}")  # Debugging output

            if date_str != 'n/a':
                date_obj = datetime.strptime(date_str, "%b %d %H:%M:%S").replace(year=datetime.now().year)

            # Safely extract the jail group or set to 'n/a' if not found
            jail = match.group('jail') if 'jail' in match.groupdict() and match.group('jail') else 'n/a'
            
            # Safely extract the host group or set to 'n/a' if not found
            host = match.group('host') if 'host' in match.groupdict() and match.group('host') else 'n/a'

            # Determine if the host is IPv4 or IPv6 (if applicable)
            host_flag = 'n/a'
            if host != 'n/a':
                host_flag = "IPv6" if ":" in host else "IPv4"

            # Return flag as True, extracted values, and the compiled regex
            return [True, [date_str, jail, host, host_flag, self.compiled_regex]]
        else:
            # Return flag as False, default 'n/a' values, and the compiled regex
            return [False, ['n/a', 'n/a', 'n/a', 'n/a', self.compiled_regex]]

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 match_rule.py '<log_line>' '<jail_regex>'")
        sys.exit(1)

    # Get log_line and jail_regex from the command-line arguments
    log_line = sys.argv[1]
    jail_regex = sys.argv[2]
    log_line = "Sep 07 07:43:48 ip-172-26-10-222 sshd[53517]: Connection reset by 198.235.24.150 port 57610 [preauth]"
    jail_regex = "Connection reset by <HOST>.*\[preauth\]"

    # Instantiate the MatchRule class
    matcher = MatchRule()

    # Call the match_rule method and print the results
    result = matcher.match_rule(log_line, jail_regex)

    # Output the flag, values, and the compiled regex
    print(f"Match found: {result[0]}")
    print(f"Extracted Data: {result[1][:4]}")  # Print the first four elements of the list (excluding the regex object)
    print(f"Compiled Regex: {result[1][4]}")  # Print the compiled regex object

    log_line = "Sep 07 07:43:48 ip-172-26-10-222 sshd[53517]: Connection reset by 14:22 port 57610 [preauth]"
    jail_regex = "Connection reset by <HOST>.*\[preauth\]"

    # Call the match_rule method and print the results
    result = matcher.match_rule(log_line, jail_regex)

    # Output the flag, values, and the compiled regex
    print(f"Match found: {result[0]}")
    print(f"Extracted Data: {result[1][:4]}")  # Print the first four elements of the list (excluding the regex object)
    print(f"Compiled Regex: {result[1][4]}")  # Print the compiled regex object

if __name__ == "__main__":
    main()

