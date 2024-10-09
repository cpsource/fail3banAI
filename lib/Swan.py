#
# Swan - swiss army knife of methods
#

import os
import sys

import atexit
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
# Configure logging
import logging
# and some magic numbers for logging
FLAG_CRITICAL = 50
FLAG_ERROR = 40
FLAG_WARNING = 30
FLAG_INFO = 20
FLAG_DEBUG = 10
FLAG_NOSET = 0
import mysql.connector
# get CountryCodes
import CountryCodes
import threading
from Checkpoint import Checkpoint
from GlobalShutdown import GlobalShutdown

class Swan:
    def __init__(self):
        self.logger = None
        self.stop_event = None
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
        # Check if FAIL3BAN_PROJECT_ROOT is not set
        if self.project_root is None:
            print("Error: The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set. Exiting ...")
            sys.exit(1)  # Exit the program with an error code
        # Setup Checkpoint
        CHECKPOINT_PATH = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/checkpoint.ctl"
        self.checkpoint = Checkpoint(CHECKPOINT_PATH)
        # and GlobalShutdown
        self.gs = GlobalShutdown()
        # get rid of stale gs control flag
        self.gs.cleanup()

        # Register the finisher function for cleanup at exit
        atexit.register(self.finis)

    # return checkpoint
    def get_checkpoint(self):
        return self.checkpoint
    
    # return gs
    def get_gs(self):
        return self.gs
    
    # return our checkpoint
    def get_checkpoint(self):
        return self.checkpoint
    
    # Extracted function to set up logging configuration
    def _setup_logging(self, LOG_FILE_NAME, LOG_FORMAT):
        logging.basicConfig(
            level=logging.DEBUG,
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(LOG_FILE_NAME),
                logging.StreamHandler()
            ]
        )
        
    def get_logger(self):
        if self.logger is not None:
            return self.logger
        # Extracted constants for log file name and format
        LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
        # Set up the logging format to include file name and line number
        LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
        # And our log id
        LOG_ID = "fail3ban"
        # Call the extracted function to configure logging
        self._setup_logging(LOG_FILE_NAME, LOG_FORMAT)
        # Create a named logger consistent with the log file name
        self.logger = logging.getLogger(LOG_ID)
        return self.logger

    # load dotenv
    def load_dotenv(self):
        logger = self.get_logger()
        try:
            # Attempt to load dotenv file using the environment variable
            dotenv_config = load_dotenv(f"{os.getenv('HOME')}/.env")
            logger.info("dotenv file loaded successfully.")
        except Exception as e:
            # Handle any exceptions that may occur
            logger.error(f"An error occurred while loading dotenv: {e}")

    # set important paths
    def set_os_path(self):
        if True:
            tasklets_path = os.path.join(self.project_root, 'lib/tasklets')
            if tasklets_path not in sys.path:
                sys.path.insert(1, tasklets_path)
                print(f"Prepending {tasklets_path} to sys.path")
        if False:
            parselets_path = os.path.join(self.project_root, 'lib/parselets')
            sys.path.insert(2, parselets_path)
            print(f"Prepending {parselets_path} to sys.path")

    def find_country(self, ip_address_string):
        # get country codes class
        self.cc = CountryCodes.CountryCodes()

        attempts = 3  # Number of retry attempts
        sleep_time = 0.1  # Sleep for 100 milliseconds (0.1 seconds)

        for attempt in range(attempts):
            try:
                # Execute the 'whois' command for the given IP address
                tmp_result = subprocess.run(['whois', ip_address_string], capture_output=True, text=True)

                # Check if the command ran successfully
                if tmp_result.returncode != 0:
                    raise Exception("Failed to run whois command.")

                # Search for the line starting with 'country:'
                match = re.search(r"^country:\s+(.+)$", tmp_result.stdout, re.MULTILINE | re.IGNORECASE)

                if match:
                    # Extract and return the country code (everything after 'country:')
                    tmp_country = match.group(1).strip()
                    tmp_country_code = self.cc.get_country(tmp_country).strip()
                    return tmp_country_code
                else:
                    # Return None if no country line is found
                    return None
            except Exception as e:
                if attempt < attempts - 1:  # If this isn't the last attempt, sleep and retry
                    time.sleep(sleep_time)
                else:
                    print(f"Error after {attempts} attempts: {e}")
                    return None

    def get_stop_event(self):
        if self.stop_event is not None:
            return self.stop_event
        # Create a global event object to signaling threads to stop
        self.stop_event = threading.Event()
        return self.stop_event
    
    def finis(self):
        # Add your cleanup logic here
        print("Finishing up...")

    def _hello_world(self):
        print("Bonjour le monde from Swan!")  # Hello World in French

if __name__ == '__main__':

    #
    # build a logger
    #
    
    # Extracted constants for log file name and format
    LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
    # Set up the logging format to include file name and line number
    LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
    # And our log id
    LOG_ID = "fail3ban"

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
    # Call the extracted function to configure logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)

    # Load dotenv
    try:
        # Attempt to load the .env file from the user's home directory
        load_dotenv(f"{os.getenv('HOME')}/.env")
        logger.info("dotenv file loaded successfully.")
    except Exception as e:
        # Log any exceptions that may occur
        logger.error(f"An error occurred while loading dotenv: {e}")
        sys.exit(1)

    def _create_connection(logger):
        """Create a connection to the database"""
        conn = mysql.connector.connect(
            user=os.getenv('MARIADB_USER_NAME'),
            password=os.getenv('MARIADB_USER_PASSWORD'),
            host=os.getenv('MARIADB_USER_HOST'),
            port=os.getenv('MARIADB_USER_PORT'),
            database=os.getenv('MARIADB_USER_DATABASE')
        )
        if conn is not None:
            logger.debug("Created connection ok")
        else:
            logger.debug("Failed to create connection")
        return conn

    # create a connection
    conn = _create_connection(logger)
        
    # Initialize FinalDisposer with necessary parameters
    kwargs={'logger' : logger,
            'conn' : conn }
    disposer = FinalDisposer(**kwargs)
    disposer._hello_world()
