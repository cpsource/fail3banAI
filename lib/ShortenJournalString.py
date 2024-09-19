import re

class ShortenJournalString:
    def __init__(self):
        # Regex patterns for the optional fields
        self.patterns = {
            "datetime": r"^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})",
            "destination_ip": r"(\bip-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\b)",
            "task_name_pid": r"(\w+)\[(\d+)\]",
            "user": r"user ((\w+\(uid=\d+\))|(\w+))",
            "by": r"by (\w+\(uid=\d+\)+)",

            #"ip_address": r".*" + r"\w+\[\d+\]:" + r".*" + r"(((\d{1,3}\.){3}\d{1,3})|([a-fA-F0-9:]+:+[a-fA-F0-9]+))",  # IPv4/6 address
            "ip_address" : r"\s+((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)|(\s+(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}|[A-Fa-f0-9]{1,4}:(?::[A-Fa-f0-9]{1,4}){1,6}|:(?::[A-Fa-f0-9]{1,4}){1,7}|::)\s+)",

            "port": r"port\s+([1-9][0-9]{0,4}(:\d+)?)\b",
            "ecdsa": r"\b(ECDSA\s*SHA256:[a-zA-Z0-9_/]*)"
        }

    def shorten_string(self, input_str):
        found_items = {}

        # Extract datetime, destination-ip, and task-name[pid] from the front
        datetime_match = re.search(self.patterns["datetime"], input_str)
        if datetime_match:
            found_items["datetime"] = datetime_match.group(1)
            input_str = input_str.replace(found_items["datetime"], "<date-time>")

        dest_ip_match = re.search(self.patterns["destination_ip"], input_str)
        if dest_ip_match:
            found_items["destination_ip"] = dest_ip_match.group(1)
            input_str = input_str.replace(found_items["destination_ip"], "<destination-ip>")

        task_name_pid_match = re.search(self.patterns["task_name_pid"], input_str)
        if task_name_pid_match:
            found_items["task_name"] = task_name_pid_match.group(1)
            found_items["pid"] = task_name_pid_match.group(2)
            input_str = input_str.replace(found_items["pid"], "<pid>")
            input_str = input_str.replace(found_items["task_name"], "<task-name>")

        # Check for optional fields
        user_match = re.search(self.patterns["user"], input_str)
        if user_match:
            found_items["user"] = user_match.group(1)  # Extract value
            input_str = input_str.replace(f"user {found_items['user']}", "<user>")

        by_match = re.search(self.patterns["by"], input_str)
        if by_match:
            found_items["by"] = by_match.group(1).strip()  # Extract value
            input_str = input_str.replace(f"by {found_items['by']}", "<by>")

        ip_match = re.search(self.patterns["ip_address"], input_str)
        if ip_match:
            #print(f"ip address found {ip_match.group(0)}")
            found_items["ip_address"] = ip_match.group(0).strip()
            input_str = input_str.replace(found_items["ip_address"], "<ip-address>")

        port_match = re.search(self.patterns["port"], input_str)
        if port_match:
            found_items["port"] = port_match.group(1).strip()
            input_str = input_str.replace(f"port {found_items['port']}", "<port>")
            found_items["port"] = found_items["port"].split(':')[0]

        ecdsa_match = re.search(self.patterns["ecdsa"], input_str)
        if port_match:
            found_items["ecdsa"] = port_match.group(1).strip()
            input_str = input_str.replace(f"{found_items['ecdsa']}", "<ecdsa>")
            found_items["port"] = found_items["port"].split(':')[0]
            
        return found_items, input_str


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

