# Tasklet_notify_abuseIPDB.py

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

#
# Tasklets are small routines that are kicked off from our thread pool, because
# these guys can wait around and when they are done, just return.
#
# The thread that was running it will then go back to the thread pool and
# wait for more work
#

def Tasklet_notify_abuseIPDB(data, **kwargs):
    # get logging setup early
    logger = logging.getLogger("fail3ban")

    #
    # Load our python3 paths
    #
    # Get the FAIL3BAN_PROJECT_ROOT environment variable
    project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
    # Check if FAIL3BAN_PROJECT_ROOT is not set
    if project_root is None:
        logger.error("The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set. Exiting ...")
        sys.exit(1)  # Exit the program with an error code
    # Construct thelib path
    lib_path = os.path.join(project_root, 'lib')
    # Add the constructed path to sys.path only if it's not already in sys.path
    if lib_path not in sys.path:
        sys.path.append(lib_path)
        logger.debug(f"Added {lib_path} to the system path.")
    else:
        logger.debug(f"{lib_path} is already in the system path.")

    # This class does the actual notification work
    import AbuseIPDB
    # get an instance
    abi = AbuseIPDB.AbuseIPDB()

    # lets check our arguments, none are optional
    if 'ip_address' not in kwargs:
        logger.warn("no ip_address to report. Exiting ...")
        return "Error. No ip_address"
    else:
        ip_address = kwargs['ip_address']

    if 'categories' not in kwargs:
        logger.warn("no categories to report. Exiting ...")
        return "Error. No categories"
    else:
        categories = kwargs['categories']

    if 'comment' not in kwargs:
        logger.warn("no comment to report. Exiting ...")
        return "Error. No comment"
    else:
        comment = kwargs['comment']

    if 'timestamp' not in kwargs:
        logger.warn("no timestamp to report. Exiting ...")
        return "Error. No timestamp"
    else:
        timestamp = kwargs['timestamp']

    if False:
        if 'data' in kwargs:
            print(f"data is {kwargs['data']}")
        if 'test-string' in kwargs:
            print(f"test-string is {kwargs['test-string']}")

    if True:
        # for debug, lets display these
        for key, value in kwargs.items():
            logger.debug(f"{key} = {value}")
        
    logger.info("Notifying AbuseIPDB ...")

    # uncomment to do it for real
    #abi.report_endpoint(ip_address, categories, comment, timestamp)

    logger.info("Notifying AbuseIPDB Complete")

    if False:
        sleep_time = int(random.uniform(2,5))
        print(f"{data} Sleeping for {sleep_time} seconds ...")
        time.sleep(sleep_time)

    print(f"{data} Done")
