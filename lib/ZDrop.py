import re
from datetime import datetime, timedelta, timezone

#
# We'll get lines of this sort from journalctl.
#

# Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=110.175.220.250 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0

class ZDrop:
    def __init__(self):
        pass
    
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
        pattern = r"^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})"
        match = re.search(pattern, input_str)
        if not match:
            # sombody elses problem
            return False
        else:
            timestamp = match.group(1) # input, output, forward
            pos = match.end(1)
            tmp_str = input_str[pos:]
            
        # we need SRC=<ip_address> - 4 and 6, set a six flag for later
        pattern = r"\sSRC=((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)|(\s+(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}|[A-Fa-f0-9]{1,4}:(?::[A-Fa-f0-9]{1,4}){1,6}|:(?::[A-Fa-f0-9]{1,4}){1,7}|::)\s+)"
        match = re.search(pattern, tmp_str)
        if not match:
            # sombody elses problem
            return False
        else:
            ip_address = match.group(1) # input, output, forward
            pos = match.end(1)
            tmp_str = tmp_str[pos:]

        # set ipv6_flag to True if ip_address is of type IPv6, else False
        ipv6_flag = ':' in ip_address
        
        # we need PROTO=(TCP/UDP/???) - protocol
        pattern = r"\sPROTO=([A-Za-z0-9\.]+)\s"
        match = re.search(pattern, tmp_str)
        if not match:
            # sombody elses problem
            return False
        else:
            protocol = match.group(1) # TCP, UDP, etc
            pos = match.end(1)
            tmp_str = tmp_str[pos:]
        
        # we need DPT=<port> - the destination port
        pattern = r"\sDPORT=([0-9]+)\s"
        match = re.search(pattern, tmp_str)
        if not match:
            # sombody elses problem
            return False
        else:
            port = match.group(1) # 22, 80, 443, etc
            pos = match.end(1)
            tmp_str = tmp_str[pos:]


        # convert the date/time to ISO/GMT
        # Parse the string into a datetime object, ignoring the milliseconds part
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
        # Convert to ISO 8601 format with UTC 'Z' (ignoring milliseconds)
        iso_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        # we need to estimate categories. See https://www.abuseipdb.com/categories for details
        if port == 22:
            categories = "18,20,22"
        else:
            if port = 80 or port = 443:
                categories = "10,18"
            else:
                if port = 3606:
                    categories = "16"
                else:
                    categories = "14"

        # get comment
        comment  = f"iptables detected banned {protocol} traffic on port {port}"

        #
        # lets display for now
        #
        
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
        found = zdro.is_zdrop(input_str)
        print("-" * 50)
