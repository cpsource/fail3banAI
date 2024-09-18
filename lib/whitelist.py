# whitelist.py

# handle everything from whitelist.ctl

#import sys
#sys.path.append('/home/pagec/openai/lib/python3.10/site-packages')

# Makie an internet request for a url
import requests
# Used to inspect our class stack
import inspect
# Configure logging
import logging
# Handle regex
import re
import os
import sys
import atexit

if __name__ != "__main__":
    # Handle iptables
    import f3b_iptables

# Extracted constants for log file name and format
LOG_FILE_NAME = "fail3ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

# some garbase ip address
TEST_IP = "192.168.211.34"
# localhost is always good to have in the whitelist
LOCAL_IP = "127.0.0.1"

class WhiteList:
    configData = None

    def __init__(self, configData=None, logger_id=LOG_ID):
        # Initialize an empty array to store whitelisted IPs
        self.whitelist = []
        # Keep a pointer to our configuration dictionary
        self.configData = configData
        # Obtain logger
        self.logger = logging.getLogger(logger_id)
        # And show logger for debugging
        #print(f"__init__: logger = {self.logger}")
        # register a cleanup
        atexit.register(self.cleanup)
        
    # Initialize the class by reading whitlist.ctl into a dictionary
    def whitelist_init(self):
        # We need iptables for many operations
        self.ipt = f3b_iptables.Iptables()
        # Open the whitelist.ctl file
        WHITELIST_FILE = self.get_whitelist_path()
        try:
            with open(WHITELIST_FILE, 'r') as file:
                for line in file:
                    # Remove any comment after # and strip whitespace
                    clean_line = line.split('#')[0].strip()
                    
                    # If the line contains an IP address, add it to the whitelist
                    if clean_line:
                        self.whitelist.append(clean_line)
        except FileNotFoundError:
            self.logger.error("whitelist.ctl file not found.")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            self.logger.debug(f"whitelist = {self.whitelist}")

        # get how we are seen from the outside world
        tmp_var = self.get_my_public_ip()
        # add us to whitelist if not there
        if not self.is_whitelisted(tmp_var):
            self.whitelist.append(tmp_var)
        # and add LOCAL_IP 
        self.whitelist.append(LOCAL_IP)
       
        # lets add TEST_IP for testing if called from main
        if self.called_from_main() and not self.is_whitelisted(TEST_IP):
            self.whitelist.append(TEST_IP)

    def called_from_main(self):
        # Check if the method is being called from the main program
        return __name__ == "__main__"
    
    # fetch the whitelist ptr from the class
    def get_whitelist(self):
        # Return the list of whitelisted IPs
        return self.whitelist

    def is_whitelisted(self, ip_address):
        # Return True if the ip_address is in the whitelist, False otherwise
        return ip_address in self.whitelist

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
    
    def get_whitelist_path(self):
        path = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/" + "whitelist.ctl"
        if path is None:
            path = "whitelist.ctl"
        return path
        
    # a utility class
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

    # add whitelisted elements to iptables
    def add_whitelist_to_iptables(self,extra="whitelist"):
        for ip_address in self.whitelist:
            self.ipt.add_allow_ip_to_front_of_input_chain(ip_address,extra)

    # show iptables
    def show_iptables(self):
        self.ipt.show_input_chain()

    # remove our ip's from INPUT
    def remove_iptables_from_input(self,extra="whitelist"):
        for ip_address in self.whitelist:
            # delete it
            self.ipt.remove_ip_from_input_chain(ip_address,extra)

    def cleanup(self):
        try:
            self.remove_iptables_from_input("server")
        except Exception as e:
            self.logger.error(f"Exception during cleanup: {e}")
            
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

    # Handle iptables
    import f3b_iptables

    # setup logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)
    # And show logger for debugging
    print(f"__main__: logger = {logger}")

    # onward to test class
    wl = WhiteList()
    wl.whitelist_init()
    print("Whitelisted IPs:", wl.get_whitelist())

    # put them into INPUT table
    wl.add_whitelist_to_iptables()

    # show
    wl.show_iptables()
    
    # remove them
    wl.remove_iptables_from_input()

    # show again
    wl.show_iptables()

    # done for now
    sys.exit(0)
    
    # Example of checking if an IP is whitelisted
    fail_flag = False

    test_ip = TEST_IP
    status = "whitelisted" if wl.is_whitelisted(test_ip) else "not whitelisted"
    print(f"{test_ip} is {status}.")
    if not status == "whitelisted":
        fail_flag = True
    test_ip = LOCAL_IP
    status = "whitelisted" if wl.is_whitelisted(test_ip) else "not whitelisted"
    print(f"{test_ip} is {status}.")
    if not status == "whitelisted":
        fail_flag = True
    test_ip = "211.211.211.211"
    status = "whitelisted" if wl.is_whitelisted(test_ip) else "not whitelisted"
    print(f"{test_ip} is {status}.")
    if not status == "not whitelisted":
        fail_flag = True
        
    # test summary
    if not fail_flag:
        print("Test OK")
    else:
        print("Test FAILED")
