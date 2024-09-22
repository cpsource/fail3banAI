# build-blacklist-4.py

# lets build control/blacklist-4.ctl from AbuseIPDB

import os
import sys
import json
import logging
# and some magic numbers from logging showing their log levels
FLAG_CRITICAL = 50
FLAG_ERROR = 40
FLAG_WARNING = 30
FLAG_INFO = 20
FLAG_DEBUG = 10
FLAG_NOSET = 0
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone

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

import f3b_AbuseIPDB

#
# Set up logger
#
# Extracted function to set up logging configuration
def setup_logging(LOG_FORMAT, LOG_FILE_NAME):
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE_NAME),
            logging.StreamHandler()
        ]
    )

# Extracted constants for log file name and format
LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
# Set up the logging format to include file name and line number
LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
# do the deed
setup_logging(LOG_FORMAT, LOG_FILE_NAME)
# Create a named logger consistent with the log file name
logger = logging.getLogger("fail3ban")

# Initialize the class
abuse_ipdb = f3b_AbuseIPDB.AbuseIPDB()

# Build the output file name
OUTPUT_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/" + "blacklist-4.ctl"

item_count = 0
# Get blacklist_endpoints for IPv6
try:
    response = abuse_ipdb.blacklist_endpoint(ip_version="4")
    if response is not None:
        try:
            # Open the file in write mode
            with open(OUTPUT_FILE_NAME, 'w') as output_file:
                # Loop through the 'data' array and write each ipAddress to the file
                for entry in response['data']:
                    output_file.write(f"{entry['ipAddress']}\n")  # Write IP address followed by a newline
                    item_count += 1
            # The file will be automatically closed after the 'with' block
        except IOError as file_error:
            # Handle file I/O errors (e.g., file not found, permission denied)
            logger.error(f"Error writing to file {OUTPUT_FILE_NAME}: {file_error}")
    else:
        logger.error("Failed to retrieve blacklist_endpoint report")
except Exception as e:
    # Handle any other errors from the blacklist_endpoint request
    logger.error(f"An error occurred while fetching the blacklist: {e}")

logger.info(f"Wrote {item_count} items.")
