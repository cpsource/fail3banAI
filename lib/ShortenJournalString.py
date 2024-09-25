import re

class ShortenJournalString:
    def __init__(self):
        # Regex patterns for the optional fields
        # The order is important. More complex rules should come first. For example,
        # for-user should come before user
        self.patterns = {
            "task-name*pid": r"([A-Za-z\-\.]+)\[(\d+)\]",
            "destination-ip": r"(\bip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\b)",
            "datetime": r"^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})",
            "by": r"by (\w+\(uid=\d+\)+)",
            "ip-address" : r"\s+((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)|(\s+(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}|[A-Fa-f0-9]{1,4}:(?::[A-Fa-f0-9]{1,4}){1,6}|:(?::[A-Fa-f0-9]{1,4}){1,7}|::)\s+)",
            "port": r"port\s+([1-9][0-9]{0,4}(:\d+)?)\b",
            "ecdsa": r"(ECDSA SHA256:[a-zA-Z0-9_/]*)",
            "for-user": r".+\sfor\suser\s+([a-zA-Z0-9-_]+)",
            "user": r"user ((\w+\(uid=\d+\))|(\w+))",
        }

    def shorten_string(self, input_str):
        found_items = {}
        condensed_str = input_str
        for key in self.patterns:
            #print(f"{key}")
            #print(f"{self.patterns[key]}")

            pos = key.find("*")
            if pos < 0:
                #print("No Star")
                # Extract data
                match = re.search(self.patterns[key], condensed_str)
                if match:
                    found_items[key] = match.group(1)
                    condensed_str = condensed_str.replace(found_items[key], "<" + key + ">")
            else:
                # double the fun, TODO, support N *'s ???
                rkey = key[pos+1:]
                lkey = key[0:pos]
                # Extract data
                match = re.search(self.patterns[key], condensed_str)
                if match:
                    found_items[lkey] = match.group(1)
                    found_items[rkey] = match.group(2)
                    if True:
                        condensed_str = condensed_str.replace(found_items[lkey], "<" + lkey + ">")
                        condensed_str = condensed_str.replace(found_items[rkey], "<" + rkey + ">")
                    else:
                        found = match.group(0)
                        condensed_str = condensed_str.replace(found, "<" + key + ">")

        return found_items, condensed_str
        
if __name__ == "__main__":
    # Input strings
    input_strings = [
        "Sep 17 10:18:36 ip-172-26-10-222 sshd[237963]: Disconnected from user ubuntu 98.97.20.85 port 49305",
        "Sep 17 10:18:36 ip-172-26-10-222 systemd[1]: session-2011.scope: Deactivated successfully.",
        "Sep 17 10:20:27 ip-172-26-10-222 sshd[237998]: Accepted publickey for ubuntu from 98.97.20.85 port 4067",
        "Sep 17 10:20:41 ip-172-26-10-222 sudo-special[238085]: pam_unix(sudo:session): session opened for user root(uid=0) by ubuntu(uid=1000)"
    ]

    # Create an instance of the class
    sjs = ShortenJournalString()

    # Process each input string and display the results
    for input_str in input_strings:
        found, shortened_str = sjs.shorten_string(input_str)
        print(f"Original: {input_str}")
        print(f"Found Items: {found}")
        print(f"Shortened: {shortened_str}")
        print("-" * 50)
