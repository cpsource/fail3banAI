import json
import re

# Sample JSON1 data
json_data = '''
{
  "match-subs": [
    {
      "subroutine": "match_invalid_user",
      "pattern": "Invalid\\\\s+user\\\\s+(?P<user_name>\\\\S+)\\\\s+from\\\\s+(?P<ip_address>\\\\d{1,3}(?:\\\\.\\\\d{1,3}){3})\\\\s+port\\\\s+(?P<port_number>\\\\d+)\\\\."
    }
  ],
  "match-chains": [
    {
      "log_entry": "# Sep 13 08:23:51 ip-172-26-10-222 sshd[147882]: Invalid user user1 from 85.159.164.28 port 40567.",
      "subroutines": [
        "match_date",
        "match_ip",
        "match_jail",
        "match_invalid_user"
      ]
    }
  ]
}
'''

# Load the JSON data
data = json.loads(json_data)

# Function to apply subroutines
def apply_subroutines(log_entry, subroutines, match_subs):
    extracted_data = {}
    for sub in subroutines:
        if sub.startswith("match_"):
            # Find the corresponding pattern
            pattern = next((item['pattern'] for item in match_subs if item['subroutine'] == sub), None)
            if pattern:
                regex = re.compile(pattern)
                match = regex.search(log_entry)
                if match:
                    extracted_data.update(match.groupdict())
    return extracted_data

def main():
    for chain in data['match-chains']:
        log_entry = chain['log_entry']
        subroutines = chain['subroutines']
        details = apply_subroutines(log_entry, subroutines, data['match-subs'])
        print(f"Log Entry: {log_entry}")
        if details:
            print("Extracted Details:")
            for key, value in details.items():
                print(f"  {key}: {value}")
        else:
            print("No matches found.")
        print("-" * 40)

if __name__ == "__main__":
    main()

