# blacklist.py

# Handle everything from blacklist.ctl

import requests
import inspect
import logging
import re
import os
import sys
import atexit
import f3b_iptables

# Constants for log file name and format
LOG_FILE_NAME = "fail3ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

TEST_IP = "192.168.211.34"
#LOCAL_IP = "127.0.0.1"

class BlackList:
    configData = None

    def __init__(self, configData=None, logger_id=LOG_ID):
        # Initialize an empty list to store blacklisted IPs
        self.blacklist = []
        # Keep a pointer to our configuration dictionary
        self.configData = configData
        # Obtain logger
        self.logger = logging.getLogger(logger_id)
        # We need iptables
        self.ipt = f3b_iptables.Iptables()
        # Get our public IP address
        self.my_public_ip = self.get_my_public_ip()
        # register a cleanup
        atexit.register(self.cleanup)
        
    # Initialize the class by reading blacklist.ctl into a list
    def blacklist_init(self):
        # Open the blacklist.ctl file
        BLACKLIST_FILE = self.get_blacklist_path()
        try:
            with open(BLACKLIST_FILE, 'r') as file:
                for line in file:
                    # Remove any comment after # and strip whitespace
                    clean_line = line.split('#')[0].strip()

                    # If the line contains an IP address, add it to the blacklist
                    if clean_line:
                        # Do not add our own IP address
                        if clean_line == self.my_public_ip:
                            self.logger.info(f"Skipping own IP address {clean_line} in blacklist.")
                            continue
                        self.blacklist.append(clean_line)
        except FileNotFoundError:
            self.logger.error("blacklist.ctl file not found.")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            self.logger.debug(f"blacklist = {self.blacklist}")

        # Add LOCAL_IP if not already in blacklist
        #if LOCAL_IP not in self.blacklist:
            #self.blacklist.append(LOCAL_IP)

        # Add TEST_IP for testing if called from main
        if self.called_from_main() and TEST_IP not in self.blacklist:
            self.blacklist.append(TEST_IP)

        # Test of scope (obsolete form)
        if self.configData is not None:
            debug = self.configData.get('debug')
            if debug:
                self.logger.debug(f"At blacklist_init, debug = {debug}")
        else:
            debug = False

    def called_from_main(self):
        # Check if the method is being called from the main program
        return __name__ == "__main__"

    # Fetch the blacklist list from the class
    def get_blacklist(self):
        # Return the list of blacklisted IPs
        return self.blacklist

    def is_blacklisted(self, ip_address):
        # Return True if the ip_address is in the blacklist, False otherwise
        return ip_address in self.blacklist

    def get_my_public_ip(self):
        if not self._is_called_within_class():
            self.logger.warning("get_my_public_ip called from outside the class")

        url = 'https://api.ipify.org?format=json'
        max_retries = 3
        timeout = 5  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Fetch the public IP using a public API with timeout
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()  # Raise an error for bad status codes
                ip_info = response.json()
                ip_address = ip_info['ip']
                self.logger.debug(f"Attempt {attempt}: Obtained public IP address {ip_address}")
                return ip_address

            except requests.Timeout:
                self.logger.warning(f"Attempt {attempt}: Timeout occurred after {timeout} seconds.")
            except requests.RequestException as e:
                self.logger.error(f"Attempt {attempt}: Error fetching IP address: {e}")

        self.logger.error(f"Failed to get public IP address after {max_retries} attempts.")
        return None
    
    def get_blacklist_path(self):
        # Get the current working directory
        current_dir = os.getcwd()

        # Check if the current directory ends with '/lib'
        if re.search(r'.*/lib\Z', current_dir):
            # Return path for lib context
            return os.path.join('..', 'control', 'blacklist.ctl')
        # Check if the current directory ends with '/fail3banAI'
        elif re.search(r'.*/fail3banAI\Z', current_dir):
            # Return path for fail3banAI context
            return os.path.join('control', 'blacklist.ctl')
        else:
            # Handle other cases (optional)
            return None

    # A utility method
    def _is_called_within_class(self):
        """Check the call stack to see if the caller is from within the class."""
        # Get the current call stack
        stack = inspect.stack()
        # The frame at index 2 should be the caller
        caller_frame = stack[2]
        # Get the class (if any) of the caller
        caller_class = caller_frame.frame.f_locals.get('self', None)
        # Return True if the caller is from the same instance
        return isinstance(caller_class, self.__class__)

    # Add blacklisted IPs to iptables
    def add_blacklist_to_iptables(self, extra="blacklist"):
        for ip_address in self.blacklist:
            if ip_address == self.my_public_ip:
                self.logger.info(f"Skipping own IP address {ip_address} in blacklist.")
                continue
            self.ipt.add_deny_ip_to_back_of_input_chain(ip_address, extra)

    # Show iptables
    def show_iptables(self):
        self.ipt.show_input_chain()

    # Remove blacklisted IPs from INPUT chain
    def remove_blacklisted_ip_tables_from_input(self, extra="blacklist"):
        for ip_address in self.blacklist:
            # Delete it
            self.ipt.remove_ip_from_input_chain(ip_address, extra)

    def cleanup(self):
        try:
            self.remove_blacklisted_ip_tables_from_input()
        except Exception as e:
            self.logger.error(f"Exception during cleanup: {e}")
            
#    def __del__(self):
#        try:
#            # Destructor to clean up iptables rules
#            self.remove_blacklisted_ip_tables_from_input()
#        except Exception as e:
#            # Attempt to log the exception if logger is available
#            try:
#                self.logger.error(f"Exception in __del__: {e}")
#            except Exception:
#                # If logger is not available, silently pass
#                pass
            
# Extracted function to set up logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE_NAME),
            logging.StreamHandler()
        ]
    )

# Example usage
if __name__ == "__main__":

    # Setup logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)
    # And show logger for debugging
    print(f"__main__: logger = {logger}")

    # Instantiate the BlackList class
    bl = BlackList()
    bl.blacklist_init()
    print("Blacklisted IPs:", bl.get_blacklist())

    # Add them into INPUT table
    bl.add_blacklist_to_iptables()

    # Show iptables
    bl.show_iptables()

    # Remove them
    bl.remove_blacklisted_ip_tables_from_input()

    # Show iptables again
    bl.show_iptables()

    # Done for now
    sys.exit(0)
