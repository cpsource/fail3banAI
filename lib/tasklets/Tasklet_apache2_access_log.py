# Tasklet_apache2_accedss_log.py

#
# We get run by a thread from the thread pool. Our job is to report an IP
# violation to abuseIPDB
#
# kwargs must contain:
#
#    ip_address
#    categories
#    comment
#    timestamp
#

import time
import random
import os
import sys
import logging
import time
import threading
import re
from datetime import datetime
import atexit

project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
# Add the constructed path to sys.path only if it's not already in sys.path
# Step 2: Construct the paths for lib and parselets
lib_path = os.path.join(project_root, 'lib')
parselets_path = os.path.join(project_root, 'lib/parselets')
tasklets_path = os.path.join(project_root, 'lib/tasklets')

# database pool
import SQLiteConnectionPool
# This class does the actual notification work
import AbuseIPDB
# And a database guy
from ManageBanActivityDatabase import ManageBanActivityDatabase
# our parselet
from Parslet_GETenv import Parselet_GETenv

LOG_ID = "fail3ban"

class Tasklet_apache2_access_log:
    def __init__(self, database_connection_pool, parselet, log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        self.abi = AbuseIPDB.AbuseIPDB()  # AbuseIPDB instance for reporting
        self.mba = ManageBanActivityDatabase(database_connection_pool,LOG_ID) # TODO - two loggers?
        self.parselet = parselet
        # Register cleanup function to close the database connection
        atexit.register(self.cleanup)

    def cleanup(self):
        pass
        
    def process_line(self, line):
        """Process a single log line, parse it, and report violations."""
        self.logger.debug(f"Processing line: {line}")

        # Well, we are going to cheat and not use the parselet mgr
        res = self.parselet.compress_line(line)
        print(res)
        return
    
        # Dummy example: Assume IP extraction from the log line
        ip_address = self.extract_ip(line)
        if not ip_address:
            self.logger.debug("No IP address found in line.")
            return

        # Determine if we're in the 15-minute window and handle accordingly
        window_size = 15
        window_flag = self.mba.is_in_window(ip_address, window_size) if self.mba else False
        
        # Update the time for this IP
        self.mba.update_time(ip_address) if self.mba else None

        if window_flag:
            self.logger.debug(f"Within {window_size}-minute window, skipping AbuseIPDB report.")
            return True
        else:
            self.logger.debug(f"Outside {window_size}-minute window, reporting to AbuseIPDB.")
        
        # Update usage count and report to AbuseIPDB
        self.mba.update_usage_count(ip_address) if self.mba else None
        self.report_abuse_ipdb(ip_address)

        return True

    def extract_ip(self, line):
        """Extract the IP address from a log line."""
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')  # Basic IPv4 regex
        match = ip_pattern.search(line)
        if match:
            return match.group(0)
        return None

    def report_abuse_ipdb(self, ip_address):
        """Report IP violation to AbuseIPDB."""
        try:
            categories = "21,22"  # Example categories, adjust as needed
            comment = "Potential attack detected"
            zulu_time_str = datetime.utcnow().isoformat() + "Z"
            resp = self.abi.report_endpoint(ip_address, categories, comment, zulu_time_str)
            self.logger.debug(f"AbuseIPDB report response: {resp}")
        except Exception as e:
            self.logger.error(f"Error reporting to AbuseIPDB: {e}")

    def monitor_log(self, file_path, stop_event):
        """Monitor the apache2 access log for new entries and process them."""
        self.logger.debug(f"Monitoring log file: {file_path}")
        
        try:
            with open(file_path, 'r') as log_file:
                log_file.seek(0, os.SEEK_END)  # Go to the end of the file
                last_inode = os.stat(file_path).st_ino

                while not stop_event.is_set():
                    current_inode = os.stat(file_path).st_ino
                    if current_inode != last_inode:
                        self.logger.debug("Log rotation detected. Re-opening the log file.")
                        log_file = open(file_path, 'r')
                        last_inode = current_inode

                    line = log_file.readline()
                    if line:
                        self.process_line(line.strip())
                    else:
                        time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error monitoring log: {e}")

# Thread - Main entry point from thread pool
def run_tasklet_apache2_access_log(**kwargs):

    # get logging setup early
    logger = kwargs['logger']

    if True:
        # for debug, lets display these
        for key, value in kwargs.items():
            logger.debug(f"{key} = {value}")
    
    # database link
    database_connection_pool = kwargs['database_connection_pool']
    # lets check our arguments, none are optional
    if 'stop_event' not in kwargs:
        logger.warning("no stop_event. Exiting ...")
        return "Error. No stop_event"
    else:
        stop_event = kwargs['stop_event']

    # parselet
    parselet = kwargs['parselet']

    # Setup database pool
    db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/fail3ban_server.db"
    database_connection_pool = SQLiteConnectionPool.SQLiteConnectionPool(db_name=db_name, pool_size=10 )
        
    # create our main class
    taal = Tasklet_apache2_access_log(database_connection_pool, parselet)

    # monitor this file
    file_path = "/var/log/apache2/access.log"
    # and go to it
    status = taal.monitor_log(file_path, stop_event)

    # signal to stop - somebody else sets
    #stop_event.set()

    # we are done. cleanup and exit this thread
    logger.debug(f"status = {status}")
    return status

if __name__ == "__main__":


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

    # create our parselet
    parselet = Parslet_GETenv()

    # Create a global event object to signaling threads to stop
    stop_event = threading.Event()

    # Setup kwargs
    data = "Tasklet_apache2_error_log.py"
    kwargs={'stop_event' : stop_event,
            'logger'     : logger,
            'database_connection_pool' : database_connection_pool,
            'parselet'   : parselet,
            }

    # Create and start the thread
    tasklet_thread = threading.Thread(target=run_tasklet_apache2_access_log, kwargs=kwargs)
    tasklet_thread.start()

    # Wait for some time (simulating the main thread doing other work)
    # take a nap
    time.sleep(60)

    # Signal the thread to stop and join
    stop_event.set()  # This will cause the thread to exit the loop
    tasklet_thread.join()  # Wait for the tasklet thread to finish

    print("Tasklet has finished.")
