#!/usr/bin/env python3
import re
import json
import sys

def parse_log_entry(log_entry):
    """
    Parses a journalctl log entry and converts it into JSON1 format.
    
    Parameters:
        log_entry (str): The journalctl log entry.
    
    Returns:
        dict: JSON1 formatted dictionary with match-subs and match-chains.
    """
    # Define patterns for common log components
    date_pattern = r"^(?P<date>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})"
    host_pattern = r"\s+(?P<host>[\w\-\.]+)"
    process_pattern = r"\s+(?P<process>[\w\-]+)\[(?P<pid>\d+)\]:"
    message_pattern = r"\s+(?P<message>.+)$"

    # Combine patterns to extract different parts of the log entry
    combined_pattern = f"{date_pattern}{host_pattern}{process_pattern}{message_pattern}"
    combined_regex = re.compile(combined_pattern)

    match = combined_regex.match(log_entry)
    if not match:
        return {"error": "Log entry does not match the expected format."}

    parsed = match.groupdict()

    # Now, based on the message, determine the specific subroutine
    # Example for kex_exchange_identification error
    kex_pattern = r"error:\s+kex_exchange_identification:\s+Connection\s+closed\s+by\s+remote\s+host\s+by\s+(?P<ip>[\d:a-fA-F]+)\s+port\s+(?P<port>\d+)"
    kex_regex = re.compile(kex_pattern)

    kex_match = kex_regex.search(parsed['message'])
    if kex_match:
        subroutine = "match_kex_exchange_identification"
        pattern = kex_regex.pattern
        subs = [
            {
                "subroutine": subroutine,
                "pattern": pattern
            }
        ]
        chains = [
            {
                "log_entry": log_entry,
                "subroutines": [
                    "match_date",
                    "match_host",
                    "match_process",
                    "match_kex_exchange_identification"
                ]
            }
        ]
        return {
            "match-subs": subs,
            "match-chains": chains
        }

    # Example for invalid user
    invalid_user_pattern = r"Invalid\s+user\s+(?P<user>\S+)\s+from\s+(?P<ip_address>\d{1,3}(?:\.\d{1,3}){3})\s+port\s+(?P<port_number>\d+)\."
    invalid_user_regex = re.compile(invalid_user_pattern)

    invalid_user_match = invalid_user_regex.search(parsed['message'])
    if invalid_user_match:
        subroutine = "match_invalid_user"
        pattern = invalid_user_regex.pattern
        subs = [
            {
                "subroutine": subroutine,
                "pattern": pattern
            }
        ]
        chains = [
            {
                "log_entry": log_entry,
                "subroutines": [
                    "match_date",
                    "match_host",
                    "match_process",
                    "match_invalid_user"
                ]
            }
        ]
        return {
            "match-subs": subs,
            "match-chains": chains
        }

    # Add more patterns and subroutines as needed

    # Default response if no specific pattern matches
    return {"error": "No specific pattern matched the log entry."}

def main():
    if len(sys.argv) != 2:
        print("Usage: ./journalctl_to_json.py \"<journalctl_log_entry>\"")
        sys.exit(1)

    log_entry = sys.argv[1]
    json_output = parse_log_entry(log_entry)
    print(json.dumps(json_output, indent=2))

if __name__ == "__main__":
    main()

