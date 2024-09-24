# PreviousJournalctl.py

# we keep track of the last N journalctl entires, and combine them into one to present for further processing

import re
import logging

class PreviousJournalctl:
    def __init__(self, radix=6):
        self.radix = radix
        self.next_free_idx: int = 0
        self.free_list = [None] * radix
        # Obtain logger
        self.logger = logging.getLogger("fail3ban")

    def get_logger(self):
        return self.logger

    def add_entry(self, string):
        # Regex to match the required components (jail, pid, ip-address)
        pattern = r"\S+\s+\S+\s+\S+\s+ip-\d+-\d+-\d+-\d+\s+(\S+)\[(\d+)\]:.*"
        match = re.search(pattern, string)

        string = string.strip()
        
        if match:
            jail = match.group(1)
            pid = match.group(2)
            end = match.end(2)+3 # save for later if we have to combine, the 3 skips '\]: '
            
            #ip_address = match.group(3) if match.group(3) else None
            ip_address = self.find_ipaddress(string[end:])
            # Store the extracted values as a tuple (jail, pid, ip-address or None)
            self.free_list[self.next_free_idx] = (jail, pid, ip_address, end, string)
        else:
            pass
            #self.logger.debug(f"No match in add_entry for {string}")

            # ip_address ??? or not
            ip_address = self.find_ipaddress(string)
            
            # just try for pid
            
            pattern = r"\s+(\S+)\[(\d+)\]:"
            match = re.search(pattern, string)
            if match:
                jail = match.group(1)
                pid = match.group(2)
                end = match.end(2)+3 # save for later if we have to combine, the 3 skips the space after the '\]: '
                self.free_list[self.next_free_idx] = (jail, pid, ip_address, end, string)
            else:
                self.free_list[self.next_free_idx] = (None, None, ip_address, None, string)                

        # Update next_free_idx using modulus to wrap around
        self.next_free_idx = (self.next_free_idx + 1) % self.radix

    # on the way out ???
    if False:
        def get_top_ip_address(self):
            # Initialize top_idx to next_free_idx - 1 modulus radix
            top_idx = (self.next_free_idx - 1) % self.radix
            if self.free_list[top_idx] is not None:
                # Extract tmp_jail and tmp_pid from the entry at prev_idx
                _, _, ip_address, _ = self.free_list[top_idx]
                if ip_address is not None:
                    return ip_address
                else:
                    return None
            else:
                return None

    def combine(self):
        ''' check to see if we can combine the top with prevs and return that or else just the top '''
        # Initialize prev_idx to next_free_idx - 1 modulus radix
        prev_idx = (self.next_free_idx - 1) % self.radix
        top_idx = prev_idx
        matches = ()
        
        # Is there a top at all ???
        if self.free_list[top_idx] is None:
            #self.logger.debug("there is no top at all ???")
            return None

        # Yes, extract pid from top
        _, top_pid, _, _, _ = self.free_list[top_idx]

        #self.logger.debug(f"top_pid = {top_pid}")
        
        # add to matches
        matches = matches + (top_idx,)

        #self.logger.debug(f"matches now {matches}")
        
        # Loop through the list looking for a pid match building up matches
        while True:
            # Decrement prev_idx by 1 modulus radix
            prev_idx = (prev_idx - 1) % self.radix

            # Is there an entry ???
            if self.free_list[prev_idx] is None:
                # No
                break
            
            # If prev_idx equals next_free_idx, done searching
            if prev_idx == self.next_free_idx:
                # No
                break

            # do pids match ???
            _, tmp_pid, _, _, _ = self.free_list[prev_idx]
            if top_pid is not None and tmp_pid is not None:
                if tmp_pid == top_pid:
                    # add to our matches
                    matches = matches + (prev_idx,)
                    continue

        # done searching prevs
        #self.logger.debug(f"after searches: matches = {matches}")
        
        # can we get out quickly
        if len(matches) == 0:
            return None
        if len(matches) == 1:
            _, _, _, _, string = self.free_list[matches[0]]
            return string

        # grr , we have extra work to do. We must combine matches
        #self.logger.debug("grrr - doing combine")
        
        # we will build this string up by walking matches backwards
        resultant_string = ""
        
        # Walk backwards through the tuple
        first_flag = True
        for value in reversed(matches):
            if first_flag:
                _, _, _, _, resultant_string = self.free_list[value]
                first_flag = False
            else:
                _, _, _, pos, tmp_string = self.free_list[value]
                resultant_string = resultant_string + " " + tmp_string[pos:]

        # and done
        self.logger.debug(f"*** Combined: Matches:{matches} Str: {resultant_string}")
        return resultant_string
    
    def show_entries(self):
        self.logger.info("Current entries in free_list (from newest to oldest):")
        if all(tmp_entry is None for tmp_entry in self.free_list):
            self.logger.info("No entries in free_list.")
            return
        
        idx = (self.next_free_idx - 1) % self.radix  # Start from the last the_entry
        count = 0
        
        while True:
            the_entry = self.free_list[idx]
            if the_entry is not None:
                self.logger.info(f"Index {idx}: {the_entry}")
            else:
                break  # Stop when an empty (None) the_entry is encountered
            
            idx = (idx - 1) % self.radix
            count += 1
            if count >= self.radix:  # Ensure not to loop indefinitely
                break

    # Ha, try building this monster pattern by hand !
    def find_ipaddress(self, str):
        pattern = r"\s+((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)|(\s+(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}|[A-Fa-f0-9]{1,4}:(?::[A-Fa-f0-9]{1,4}){1,6}|:(?::[A-Fa-f0-9]{1,4}){1,7}|::)\s+)"
        match = re.search(pattern, str)
        if match:
            ip_address = match.group(1)
            return ip_address
        return None

    def __del__(self):
        self.free_list = None

# Main entry point for testing
if __name__ == "__main__":
    # Create an instance of PreviousJournalctl
    log_monitor = PreviousJournalctl(radix=6)
    
    # Test strings (six entries, with the last matching one of the earlier ones)
    test_entries = [
        "Sep 13 23:50:09 ip-172-26-10-222 sshd[12345]: 'sshd' executed by 192.168.1.1",
        "Sep 13 23:55:15 ip-172-26-10-222 apache2[67890]: 'apache2' executed by 10.0.0.5",
        "Sep 13 23:57:32 ip-172-26-10-222 nginx[98765]: 'nginx' executed by 172.16.0.7",
        "Sep 13 23:59:50 ip-172-26-10-222 mysql[45678]: 'mysql' executed by 192.168.2.2",
        "Sep 13 23:51:09 ip-172-26-10-222 xmlrpc.php[162826]: 'xmlrpc.php' executed by 118.193.57.62",
        # The last entry will match the fourth entry (mysql process)
        "Sep 14 00:01:12 ip-172-26-10-222 mysql[45678]: 'mysql' executed by 192.168.2.2"
    ]
    
    # Add each entry to the log monitor
    for entry in test_entries:
        log_monitor.add_entry(entry)
    
    # Show entries in free_list for debugging
    log_monitor.show_entries()
    
    # Now, call prev_entry and check if it returns the correct match
    result = log_monitor.prev_entry()
    
    # Print result
    if result[0]:
        log_monitor.get_logger().info(f"Match found: {result[1]}")
    else:
        log_monitor.get_logger().info("No match found")
    
    # Verify if it matches the fourth entry
    expected_result = ('mysql', '45678', '192.168.2.2', "Sep 13 23:59:50 ip-172-26-10-222 mysql[45678]: 'mysql' executed by 192.168.2.2")
    if result[1] == expected_result:
        log_monitor.get_logger().info("Test passed! Correct match returned.")
    else:
        log_monitor.get_logger().info("Test failed! Incorrect result.")

