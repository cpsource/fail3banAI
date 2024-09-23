# blacklist.py

# Handle everything from blacklist.ctl

import requests
import inspect
import logging
import re
import os
import sys
import atexit

# Constants for log file name and format
LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
# Set up the logging format to include file name and line number
LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

#
# Load our python3 paths
#
# Get the FAIL3BAN_PROJECT_ROOT environment variable
project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
# Check if FAIL3BAN_PROJECT_ROOT is not set
if project_root is None:
    print("Error: The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
    sys.exit(1)  # Exit the program with an error code
# Construct the lib path
lib_path = os.path.join(project_root, 'lib')
# Add the constructed path to sys.path only if it's not already in sys.path
if lib_path not in sys.path:
    sys.path.append(lib_path)
    print(f"Added {lib_path} to the system path.")
else:
    print(f"{lib_path} is already in the system path.")

import f3b_whitelist

class BlackList:

    def __init__(self, configData=None, logger_id=LOG_ID):
        # ip_count
        self.ip_count_loaded = 0
        # our config data
        self.configData = None
        # init and load whitelist
        self.wl = f3b_whitelist.WhiteList()
        self.wl.whitelist_init()
        # Initialize an empty list to store blacklisted IPs
        self.blacklist = set()
        # Keep a pointer to our configuration dictionary
        self.configData = configData
        # Obtain logger
        self.logger = logging.getLogger(logger_id)
        # register a cleanup
        atexit.register(self.cleanup)

    def load_blacklist(self, filespec):
        """
            Loads IP addresses from a file and adds them to the blacklist if not already present.
    
            Args:
            filespec (str): The path to the file containing the list of IP addresses.
            blacklist (set): A set containing currently blacklisted IPs to avoid duplicates.
        """
        local_count = 0
        try:
            with open(filespec, 'r') as file:
                for line in file:
                    # Remove any comment after # and strip whitespace
                    clean_line = line.split('#')[0].strip()

                    # skip if in whitelist
                    if clean_line:
                        if not self.wl.is_whitelisted(clean_line):
                            # If the line contains an IP address and is not already blacklisted
                            if clean_line not in self.blacklist:
                                self.blacklist.add(clean_line)
                                self.ip_count_loaded += 1
                                local_count += 1
                                #print(f"Adding {clean_line} to blacklist.")
                            else:
                                pass
                        else:
                            print(f"Skipping {clean_line} as it's whitelisted")
                        
        except FileNotFoundError:
            print(f"Error: File {filespec} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        self.logger.debug(f"blacklist {filespec} loaded {local_count} new ip addresses")
                
    # Initialize the class by reading blacklist.ctl into a list
    def blacklist_init(self):

        # get a list of blacklist files
        blacklist_files = [ f"{project_root}" + "/control/blacklist.ctl",
                            f"{project_root}" + "/control/ipsum.7.ctl",
                            f"{project_root}" + "/control/blacklist-4.ctl",
                            f"{project_root}" + "/control/blacklist-6.ctl" ]
        # do the load
        for file in blacklist_files:
            self.load_blacklist(file)
            
        self.logger.debug(f"blacklists loaded {self.ip_count_loaded} ip addresses")

    # Fetch the blacklist list from the class
    def get_blacklist(self):
        # Return the list of blacklisted IPs
        return self.blacklist

    def is_blacklisted(self, ip_address):
        # Return True if the ip_address is in the blacklist, False otherwise
        return ip_address in self.blacklist

    def cleanup(self):
        pass
    
# Example usage
if __name__ == "__main__":

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

    # Setup logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)
    # And show logger for debugging
    print(f"__main__: logger = {logger}")

    # Instantiate the BlackList class
    bl = BlackList()
    # and Initialize it
    bl.blacklist_init()
    #print("Blacklisted IPs:", bl.get_blacklist())

    # Done
    sys.exit(0)
