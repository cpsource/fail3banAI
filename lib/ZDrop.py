import re

#
# We'll get lines of this sort from journalctl.
#

# Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=110.175.220.250 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0

class ZDrop:
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
            "COMMAND" : r"(COMMAND\=[A-Za-z\/\.]+)",
        }

    # take a quick look at the input_str. If it contains zDROP ..., we'll handle it
    # then return True, else we return False
    def is_zdrop(self, input_str):
        # look for this: " zDROP ufw-blocklist-XXX: "
        pattern = r"\szDROP\sufw-blocklist-([A-Za-z]+):\s"
        match = re.search(pattern, input_str)
        if not match:
            # sombody elses problem
            return False
        else:
            chain = match.group(1) # input, output, forward

        # we need the date and time
        # we need SRC=<ip_address> - 4 and 6, set a six flag for later
        # we need PROTO=(TCP/UDP/???) - protocol
        # we need DPT=<port> - the destination port

        # we should come up with a comment
        # convert the date/time to ISO/GMT
        # we need to estimate categories
        # comment = "iptables detected banned TCP traffic on port 22" ???

        # say we handled it for the caller
        return True
        
if __name__ == "__main__":
    # Input strings
    input_strings = [
        "Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=110.175.220.250 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0"
    ]

    # Create an instance of the class
    zdro = ZDrop()

    # Process each input string and display the results
    for input_str in input_strings:
        found, shortened_str = sjs.shorten_string(input_str)
        print(f"Original: {input_str}")
        print(f"Found Items: {found}")
        print(f"Shortened: {shortened_str}")
        print("-" * 50)
