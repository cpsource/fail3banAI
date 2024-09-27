import re

class ShortenJournalString:
    def __init__(self):
        # Regex patterns for the optional fields
        # The order is important. More complex rules should come first. For example,
        # for-user should come before user
        self.patterns = {
            "task-name*pid": r"([A-Za-z\-\.]+)\[(\d+)\]",
            "destination-ip": r"(\bip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\b)",
            "by": r"by (\w+\(uid=\d+\)+)",
            "ip-address" : r"\s+((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)|(\s+(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}|[A-Fa-f0-9]{1,4}:(?::[A-Fa-f0-9]{1,4}){1,6}|:(?::[A-Fa-f0-9]{1,4}){1,7}|::)\s+)",
            "port": r"port\s+([1-9][0-9]{0,4}(:\d+)?)\b",
            "ecdsa": r"(ECDSA SHA256:[a-zA-Z0-9_/]*)",
            "for-user": r".+\sfor\suser\s+([a-zA-Z0-9-_]+)",
            "user": r"user ((\w+\(uid=\d+\))|(\w+))",
            "COMMAND" : r'\s(COMMAND=[^\s]+ .*?)\s',
            "PWD" : r'\s(PWD=[^\s]+)\s',
            "TTY" : r'\s(TTY=[^\s]+)\s',
        }
        #  COMMAND=/home/ubuntu/openai/bin/python3 ./monitor-fail3ban.py
        
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
                    # fufu for IPv6 address matches
                    if match.group(1) is None:
                        str = match.group(0)
                    else:
                        str = match.group(1)
                    str = str.strip()
                    #for i, group in enumerate(match.groups(), 1):
                    #    print(f"Group {i}: {group}")
                    #print(f"str = {str}")
                    found_items[key] = str
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
        # managing date should have a special place in heck in Python3
        date_time = self.getdatetime(condensed_str)
        if date_time is not None:
            found_items['datetime'] = date_time
            condensed_str = condensed_str.replace(date_time, "<datetime>>")

        # return
        return found_items, condensed_str

    # Sep 27 07:41:16 - etc
    # Returns date as a <str>
    def get_datetime(s):
        pattern = r"^([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
        match = re.search(pattern, s)
        if match:
            m = match.group(1)
            #print(f"get_datetime, m = {m}")
        
            # Get the current year and append it to the date string
            current_year = datetime.now().year
            full_date_str = f"{current_year} {m}"
        
            # Parse the date string with the year included
            parsed_date = datetime.strptime(full_date_str, '%Y %b %d %H:%M:%S')
        
            # Convert the datetime object back to a string
            res = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            #print(f"get_datetime, match, {res}")
        else:
            #print(f"get_datetime, no match, {s}")
            res = None
    return res
    
if __name__ == "__main__":
    # Input strings
    input_strings = [
        "Sep 26 03:01:27 ip-172-26-10-222 sshd[165207]: Invalid user  from 2001:470:1:c84::17 port 55680",
        "Sep 17 10:18:36 ip-172-26-10-222 sshd[237963]: Disconnected from user ubuntu 98.97.20.85 port 49305",
        "Sep 17 10:18:36 ip-172-26-10-222 systemd[1]: session-2011.scope: Deactivated successfully.",
        "Sep 17 10:20:27 ip-172-26-10-222 sshd[237998]: Accepted publickey for ubuntu from 98.97.20.85 port 4067",
        "Sep 17 10:20:41 ip-172-26-10-222 sudo-special[238085]: pam_unix(sudo:session): session opened for user root(uid=0) by ubuntu(uid=1000)",
        "Sep 26 03:41:45 ip-172-26-10-222 sudo[165717]:   ubuntu : TTY=pts/0 ; PWD=/home/ubuntu/fail3banAI/util ; USER=root ; COMMAND=/home/ubuntu/openai/bin/python3 ./monitor-fail3ban.py pam_unix(sudo:session): session opened for user root(uid=0) by ubuntu(uid=1000)",
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
