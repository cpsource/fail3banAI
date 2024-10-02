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
import json
import traceback

project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
# Add the constructed path to sys.path only if it's not already in sys.path
# Step 2: Construct the paths for lib and parselets
p = f"{project_root}" + "/lib"
if p not in sys.path:
    sys.path.insert(0, p)
p = f"{project_root}" + "/lib/parselets"
if p not in sys.path:
    sys.path.insert(1,p)
p = f"{project_root}" + "/lib/tasklets"
if p not in sys.path:
    sys.path.insert(2,p)

print(sys.path)

# database pool
import SQLiteConnectionPool
# This class does the actual notification work
import AbuseIPDB
# And a database guy
from ManageBanActivityDatabase import ManageBanActivityDatabase
# our parselet
import Parselet_GETenv
# determine if a GET is invalid
import BadGets
# our WhiteList
import WhiteList
# manage ban activity deatabase
from ManageBanActivityDatabase import ManageBanActivityDatabase
# tasklet that notifies AbuseIPDB
from Tasklet_notify_abuseIPDB import Tasklet_notify_abuseIPDB
# work manager
import WorkManager

LOG_ID = "fail3ban"

class Tasklet_apache2_access_log:
    def __init__(self, database_connection_pool, parselet, work_controller, log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        self.wctlr = work_controller
        self.abi = AbuseIPDB.AbuseIPDB()  # AbuseIPDB instance for reporting
        self.mba = ManageBanActivityDatabase(database_connection_pool,LOG_ID) # TODO - two loggers?
        self.parselet = parselet
        self.badgets = BadGets.BadGets()

        # whitelist
        self.white_list = WhiteList.WhiteList()

        # and a ManageBanActivityDatabase - manages 
        self.mba = ManageBanActivityDatabase(database_connection_pool)

        # Register cleanup function to close the database connection
        atexit.register(self.cleanup)

    def cleanup(self):
        pass

    def is_error_response(self, parsed_res):
        """Check if the given response contains an error."""
        if "error" in parsed_res:
            return True
        return False

    def truncate_string(self,input_str):
        if len(input_str) > 80:
            return input_str[:80] + ' ...'
        return input_str

    def task_callback(self, status):
        print(f"at task_callback, status = {status}")
    
    def process_line(self, line):
        """Process a single log line, parse it, and report violations."""
        #print(f"* Processing line: {line}")
        
        # Well, we are going to cheat and not use the parselet mgr
        res = self.parselet.compress_line(line)

        print(f"compressed line = {res}")

        parsed_res = json.loads(res)
        
        # errors look like this {"class_name": "Parselet_GETenv", "error": "No match found"}
        if self.is_error_response(parsed_res):
            err = parsed_res.get('error')
            print(f"Error returned = {err} for line {line}")
            return

        try:
            # Extract info
            ip_address     = parsed_res.get('extracted_info', {}).get('ip_address')
            requested_file = parsed_res.get('extracted_info', {}).get('requested_file')
            timestamp      = parsed_res.get('extracted_info', {}).get('timestamp')
        except Exception as e:
            self.logger.error(f"Error extracting info: {e}")

        #
        # convert timestamp to iso_timestamp
        #
        # Parse the string using datetime.strptime
        parsed_time = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")
        # Convert to ISO 8601 format
        iso_timestamp = parsed_time.isoformat()

        print(f"requested_file = {requested_file}, ip_address = {ip_address}, iso_timestamp ={iso_timestamp}")

        # is it one of the bad GET's ???
        if not self.badgets.is_bad_get(requested_file):
            print("Not a bad GET, returning ...")
            return
        else:
            print("Is a bad get. continuing ...")
            
        #print(f"whitelist = {self.white_list.get_whitelist()}")
        
        # is the ip_address in the whitelist?
        if self.white_list.is_whitelisted(ip_address):
            print(f"IP address {ip_address} is whitelisted, returning ...")
            return
        else:
            print(f"IP address {ip_address} is NOT whitelisted")

        #
        # report to AbuseIPDB
        #

        # $$$ just for test
        if False:
            # within 15 minute window ??? - if True, then we can't send do AbuseIPDB
            window_size = 15
            # Note: This guy creates the record if not there, updates usage counts and current if needed
            window_flag = self.mba.is_in_window(ip_address,window_size)
            if window_flag is False:
                print("would report to AbuseIPDB, but we are stubbed for testing")
        else:
            window_flag = False
            
        # report to AbuseIPDB
        if window_flag is False:
            # we can report as it's not too soon
            # we need to estimate categories. See https://www.abuseipdb.com/categories for details

            # build info for report
            categories = "10,18"
            # get comment
            comment  = self.truncate_string(f"apache2 (hacking attempt) reports illegal GET = {requested_file}")

            # build a work unit
            data = f"Tasklet_apache2_access_log"
            work_unit = WorkManager.WorkUnit(
                function=Tasklet_notify_abuseIPDB,
                kwargs={'data'       : data,
                        'ip_address' : ip_address,
                        'categories' : categories,
                        'comment'    : comment,
                        'timestamp'  : iso_timestamp
                        },  # Using kwargs to pass arguments
                callback=self.task_callback
            )
            self.wctlr.enqueue(work_unit)
            # and lower our priority a bit for a bit - Cheezy Python3, hack, hack, hack !!!
            time.sleep(.01)
            
        # done for now $$$
        return True

    # TODO - dead code
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

    # We should hang here basically forever
    def monitor_log(self, file_path, stop_event):
        """Monitor the apache2 access log for new entries and process them."""
        self.logger.debug(f"Monitoring log file: {file_path}")
        
        try:
            with open(file_path, 'r') as log_file:
                # $$$
                #log_file.seek(0, os.SEEK_END)  # Go to the end of the file
                last_inode = os.stat(file_path).st_ino

                print("starting main wait loop")
                
                # main wait loop
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
                        #print("main loop, no data")
                        time.sleep(5)

        except Exception as e:
            self.logger.error(f"Error monitoring log: {e}")
            # dump the stack
            traceback.print_exc()

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

    # work controller
    work_controller = kwargs['work_controller']
    
    # Setup database pool
    #db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/fail3ban_server.db"
    #database_connection_pool = SQLiteConnectionPool.SQLiteConnectionPool(db_name=db_name, pool_size=10 )
        
    # create our main class
    taal = Tasklet_apache2_access_log(database_connection_pool, parselet, work_controller)

    # monitor this file
    file_path = "/var/log/apache2/access.log"
    # and go to it
    status = taal.monitor_log(file_path, stop_event)

    # signal to stop - somebody else sets
    #stop_event.set()

    # we are done. cleanup and exit this thread
    logger.debug(f"taal.monitor_log returns status = {status}")
    return status

if __name__ == "__main__":

    project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
    # Add the constructed path to sys.path only if it's not already in sys.path
    # Step 2: Construct the paths for lib and parselets
    lib_path = os.path.join(project_root, 'lib')
    parselets_path = os.path.join(project_root, 'lib/parselets')
    tasklets_path = os.path.join(project_root, 'lib/tasklets')

    if False:
        # database pool
        import SQLiteConnectionPool
        # This class does the actual notification work
        import AbuseIPDB
        # And a database guy
        from ManageBanActivityDatabase import ManageBanActivityDatabase
        # our parselet
        import Parselet_GETenv
    
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
    parselet = Parselet_GETenv.Parselet_GETenv()

    # Create a global event object to signaling threads to stop
    stop_event = threading.Event()
    if False:
        if stop_event is not None:
            stop_event.clear()
        else:
            print("Error, stop evet was none")
            sys.exit(0)
        
    # Setup database pool
    db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/fail3ban_server.db"
    database_connection_pool = SQLiteConnectionPool.SQLiteConnectionPool(db_name=db_name, pool_size=10 )

    # Get WorkController
    work_controller = WorkManager.WorkController()
    
    # Setup kwargs
    data = "Tasklet_apache2_error_log.py"
    kwargs={'dummy' : None,
            'stop_event' : stop_event,
            'logger'     : logger,
            'database_connection_pool' : database_connection_pool,
            'parselet'   : parselet,
            'work_controller' : work_controller,
            }

    # Create and start the thread
    tasklet_thread = threading.Thread(target=run_tasklet_apache2_access_log, kwargs=kwargs)
    tasklet_thread.start()

    # Wait for some time (simulating the main thread doing other work)
    # take a nap
    #time.sleep(60)

    # Signal the thread to stop and join
    #stop_event.set()  # This will cause the thread to exit the loop
    tasklet_thread.join()  # Wait for the tasklet thread to finish

    print("Tasklet has finished.")
