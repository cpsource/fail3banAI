import time
import random
import os
import sys

#
# Tasklets are small routines that are kicked off from our thread pool, because
# these guys can wait around and when they are done, just return.
#
# The thread that was running it will then go back to the thread pool and
# wait for more work

def Tasklet_hello_world(data, **kwargs):
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

    import AbuseIPDB

    # get ourselves a reporter
    abi = AbuseIPDB.AbuseIPDB()

    if 'ip_address' not in kwargs:
        print("Error, no ip_address to report. Exiting ...")
        return "Error. No ip_address"
    else:
        ip_address = kwargs['ip_address']

    if 'categories' not in kwargs:
        print("Error, no categories to report. Exiting ...")
        return "Error. No categories"
    else:
        categories = kwargs['categories']

    if 'comment' not in kwargs:
        print("Error, no comment to report. Exiting ...")
        return "Error. No comment"
    else:
        comment = kwargs['comment']

    if 'timestamp' not in kwargs:
        print("Error, no timestamp to report. Exiting ...")
        return "Error. No timestamp"
    else:
        timestamp = kwargs['timestamp']

    if False:
        if 'data' in kwargs:
            print(f"data is {kwargs['data']}")
        if 'test-string' in kwargs:
            print(f"test-string is {kwargs['test-string']}")

    # for debug, lets display these
    for key, value in kwargs.items():
        print(f"{key} = {value}")
        
    print("Ok to notify AbuseIPDB")

    sleep_time = int(random.uniform(2,5))
    print(f"{data} Sleeping for {sleep_time} seconds ...")
    time.sleep(sleep_time)

    print(f"{data} Done")
    
