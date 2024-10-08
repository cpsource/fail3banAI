#
# FinalDisposer - We are at the end of the processing line for an ip_address. We
#                 decide what to do with it.
#

import os
import sys

import atexit
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
import logging
import mysql.connector

class FinalDisposer:
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')
        self.conn = kwargs.get('conn')
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')

        # Register the finisher function for cleanup at exit
        atexit.register(self.finis)

    def finis(self):
        # Add your cleanup logic here
        if self.logger:
            self.logger.info("Final cleanup is happening.")
        if self.conn:
            self.conn.close()
        print("Finishing up...")

    def _hello_world(self):
        print("Bonjour le monde!")  # Hello World in French

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
