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

# Extracted constants for log file name and format
LOG_FILE_NAME = "fail3ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

TEST_IP = "192.168.211.34"
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
        print(f"__init__: logger = {self.logger}")
        
    # Initialize the class by reading whitlist.ctl into a dictionary
    def whitelist_init(self):
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

        # test of scope - (obsoleted form)
        if self.configData is not None:
            debug = self.configData.get('debug')
            if debug :
                self.logger.debug(f"at whitelist_init, debug = {debug}")
        else:
            debug = False

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
            self.logger.warn(f"get_my_public_ip called from outside the class")
            
        try:
            # Fetch the public IP using a public API
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()  # Raise an error for bad status codes
            ip_info = response.json()
            ip_address = ip_info['ip']
            self.logger.debug(f"our ip address is {ip_address}")
            return ip_address

        except requests.RequestException as e:
            return None # f"Error fetching IP address: {e}"

    def get_whitelist_path(self):
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Check if the current directory ends with '/lib'
        if re.search(r'.*/lib\Z', current_dir):
            # Return path for lib context
            return os.path.join('..', 'control', 'whitelist.ctl')
        # Check if the current directory ends with '/fail3banAI'
        elif re.search(r'.*/fail3banAI\Z', current_dir):
            # Return path for fail3banAI context
            return os.path.join('control', 'whitelist.ctl')
        else:
            # Handle other cases (optional)
            return None
        
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


