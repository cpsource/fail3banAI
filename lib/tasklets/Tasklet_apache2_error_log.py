# Tasklet_apache2_error_log.py

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

# This class does the actual notification work
import AbuseIPDB
abi = AbuseIPDB.AbuseIPDB()

#
# Tasklets are small routines that are kicked off from our thread pool, because
# these guys can wait around and when they are done, just return.
#
# The thread that was running it will then go back to the thread pool and
# wait for more work
#
# kwargs
#
#  'stop_event' : stop_event
#

# [Fri Sep 27 08:05:04.123227 2024] [php:error] [pid 183989:tid 183989] [client 194.233.72.140:44220] script '/var/www/csp/phpinfo.php' not found or unable to stat

# [Fri Sep 27 00:11:01.142598 2024] [core:notice] [pid 183993:tid 183993] AH00113: /var/www/html/.htaccess:45 cannot use a full URL in a 401 ErrorDocument directive --- ignoring!

def process_line(str, logger):
    #logger.debug(str)

    regex = r"^\[(.+?)\]"
    match = re.search(regex,str)
    if not match:
        return False
    datetime_str = match.group(1)

    #logger.debug(f"datetime = {datetime_str}")
    
    # Parse the date string into a datetime object
    dt = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S.%f %Y')
    # Convert to Zulu time (UTC) in ISO 8601 format, without fractional seconds
    zulu_time_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    regex = r"\[client ([\d\.]+):\d+\]"
    match = re.search(regex,str)
    if not match:
        return False
    ip_address = match.group(1)

    regex = r"script '(.+?)' not found or unable to stat$"
    match = re.search(regex,str)
    if not match:
        return False
    script = match.group(1)

    logger.debug(f"\n    datetime = {zulu_time_str}, ip_address = {ip_address}, script = {script}")

    # get ready to report
    comment = f"Apache2 script {script} not found or unable to stat"
    #ip_address - good to go
    #zulu_time_str - good to go
    categories = "10,18"

    try:
        # uncomment to do it for real, resp should be the HTTPS error code
        resp = abi.report_endpoint(ip_address, categories, comment, zulu_time_str)
        logger.debug("Notifying AbuseIPDB Complete")
    except Exception as em:
        logger.error(f"Error from abi.rport_endpoint: {em}")
    logger.debug(f"resp = {resp}")

    return True

def monitor_log(file_path, stop_event, logger):
    logger.debug(f"Monitoring {file_path}")
    try:
        # Open the log file
        log_file = open(file_path, 'r')
        # Move the cursor to the end of the file
        log_file.seek(0, os.SEEK_END)
        last_inode = os.stat(file_path).st_ino
        
        while not stop_event.is_set():
            # Check for log rotation by checking the inode of the file
            current_inode = os.stat(file_path).st_ino
            if current_inode != last_inode:
                # Inode has changed, log rotation detected
                logger.debug("Log rotation detected. Re-opening the file.")
                log_file.close()  # Close the old file
                
                # Reopen the new log file
                log_file = open(file_path, 'r')
                last_inode = current_inode

            # Read any new lines from the log file
            line = log_file.readline()
            if line:
                str = line[:]
                str = str.strip()
                process_line(str, logger)
            else:
                time.sleep(1)  # Sleep for a second if no new data

    except Exception as em:
        logger.error(f"Error while monitoring log: {em}")

def Tasklet_apache2_error_log(**kwargs):

    # get logging setup early
    logger = kwargs['logger']
    logger.debug("Starting...")

    #
    # Load our python3 paths
    #
    # Get the FAIL3BAN_PROJECT_ROOT environment variable
    project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
    # Check if FAIL3BAN_PROJECT_ROOT is not set
    if project_root is None:
        logger.error("The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set. Exiting ...")
        sys.exit(1)  # Exit the program with an error code

    # This class does the actual notification work
    import AbuseIPDB
    # get an instance
    abi = AbuseIPDB.AbuseIPDB()

    if False:
        # for debug, lets display these
        for key, value in kwargs.items():
            logger.debug(f"{key} = {value}")

    # lets check our arguments, none are optional
    if 'stop_event' not in kwargs:
        logger.warning("no stop_event. Exiting ...")
        return "Error. No stop_event"
    else:
        stop_event = kwargs['stop_event']

    # monitor file
    file_path = "/var/log/apache2/error.log"
    monitor_log(file_path, stop_event, logger)

    # take a nap
    time.sleep(15)

    # signal to stop
    stop_event.set()
    
    if False:
        logger.info("Notifying AbuseIPDB ...")

    if False:
        # one last chance to log
        logger.debug(f"ip_address: {ip_address}")
        logger.debug(f"categories: {categories}")
        logger.debug(f"comment   : {comment}")
        logger.debug(f"timestamp : {timestamp}")
    
    # uncomment to do it for real, resp should be the HTTPS error code
    #resp = abi.report_endpoint(ip_address, categories, comment, timestamp)
    #logger.info("Notifying AbuseIPDB Complete")

    if False:
        sleep_time = int(random.uniform(2,5))
        print(f"{data} Sleeping for {sleep_time} seconds ...")
        time.sleep(sleep_time)

    resp = "OK"
    logger.debug(f"resp = {resp}")
    return resp

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
    # Create a global event object to signaling threads to stop
    stop_event = threading.Event()
    # Setup kwargs
    data = "Tasklet_apache2_error_log.py"
    kwargs={'stop_event' : stop_event,
            'logger'     : logger }  # Using kwargs to pass arguments
    Tasklet_apache2_error_log(**kwargs)
