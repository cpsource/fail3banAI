import re
import os
import sys
from datetime import datetime, timedelta, timezone
import logging
from http import HTTPStatus

# Define the FAIL3BAN_PROJECT_ROOT environment variable or path
fail3ban_project_root = os.getenv('FAIL3BAN_PROJECT_ROOT', '/path/to/fail3ban/project/root')
# Add FAIL3BAN_PROJECT_ROOT/lib to Python's module search path
lib_path = os.path.join(fail3ban_project_root, 'lib')
sys.path.append(lib_path)
# Add FAIL3BAN_PROJECT_ROOT/tasklets to Python's module search path
tasklet_path = os.path.join(fail3ban_project_root, 'lib/tasklets')
sys.path.append(tasklet_path)

import WorkManager
import MessageManager
from Tasklet_notify_abuseIPDB import Tasklet_notify_abuseIPDB
from ManageBanActivityDatabase import ManageBanActivityDatabase

#
# We'll get lines of this sort from journalctl.
#

# Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=110.175.220.250 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0

class Tasklet_ZDrop:
    def __init__(self, work_controller, message_manager, database_connection_pool):
        # Create a named logger consistent with the log file name
        self.logger = logging.getLogger("fail3ban")
        # and a work manager
        #self.wctlr = WorkManager.WorkController(num_workers=1)
        self.wctlr = work_controller
        # and save message_manager
        self.message_manager = message_manager
        # and save connection_pool
        self.database_connection_pool = database_connection_pool
        # a callback
        self.task_callback = lambda result: print(f"Task completed with result: {result}")
        # and a ManageBanActivityDatabase - manages 
        self.mba = ManageBanActivityDatabase(self.database_connection_pool)

    def shutdown(self):
        pass
        #self.wctlr.shutdown()
        
    # take a quick look at the input_str. If it contains zDROP ..., we'll handle it
    # then return True, else we return False
    def is_zdrop(self, input_str):
        # log our entry
        self.logger.debug(f"Entry: input_str = {input_str}")
        
        if not 'zDROP' in input_str:
            # look for this: " zDROP ufw-blocklist-XXX: "
            self.logger.warnng(f"input_str must contain zDROP: {input_str}")
            return False
        
        pattern = r"\szDROP\sufw-blocklist-([A-Za-z0-9]+):\s"
        match = re.search(pattern, input_str)
        if not match:
            # sombody elses problem
            return False
        else:
            chain = match.group(1) # input, output, forward

        # log that we've entered
        #self.logger.debug("entering is_zdrop")

        #
        # lets now collect the various bits of data from the input_str
        #
        
        # we need the date and time
        pattern = r"^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})"
        match = re.search(pattern, input_str)
        if not match:
            # sombody elses problem
            return False
        else:
            timestamp = match.group(1) # input, output, forward
            pos = match.end(1)
            tmp_str = input_str[pos:]

        # we need SRC=<ip_address> - 4 and 6, set a six flag for later
        pattern = r"\sSRC=((?P<ip>(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2}))\s+)"
        patternIPv6 = r"\sSRC=([0-9a-fA-F:]+)"
        match = re.search(pattern, tmp_str)
        if not match:
            match = re.search(patternIPv6, tmp_str)
            if not match:
                return False
        # fufu for IPv6 address matches
        if match.group(1) is None:
            print("Error")
        else:
            ystr = match.group(1)
            ystr = ystr.strip()
            ip_address = ystr

        # set ipv6_flag to True if ip_address is of type IPv6, else False
        ipv6_flag = ':' in ip_address

        # within 15 minute window ??? - if True, then we can't send do AbuseIPDB
        window_size = 15
        window_flag = self.mba.is_in_window(ip_address,window_size)

        # set time to now
        self.mba.update_time(ip_address)
        

        
        # do so after the database update
        if window_flag is True:
            self.logger.debug(f"Within {window_size} minute window, skip reporting to AbuseIPDB")
            # we are within the 15 minute reporting window for AbuseIPDB
            # say we handled the zDROP for the caller
            return True
        else:
            self.logger.debug(f"Outisde {window_size} minute window, reporting to AbuseIPDB")
            
        # update usage count
        self.mba.update_usage_count(ip_address)
        
        # we need PROTO=(TCP/UDP/???) - protocol
        pattern = r"\sPROTO=([A-Za-z0-9\.]+)\s"
        match = re.search(pattern, tmp_str)
        if not match:
            # sombody elses problem
            return False
        else:
            protocol = match.group(1) # TCP, UDP, etc
            pos = match.end(1)
            tmp_str = tmp_str[pos:]

        # we need DPT=<port> - the destination port
        pattern = r"\sDPT=([0-9]+)\s"
        match = re.search(pattern, tmp_str)
        if not match:
            # sombody elses problem
            return False
        else:
            port = match.group(1) # 22, 80, 443, etc
            pos = match.end(1)
            tmp_str = tmp_str[pos:]

        # convert the date/time to ISO/GMT
        current_year = datetime.now().year
        xpos = timestamp.find(':')
        timestamp = timestamp[:xpos-3] + ", " + str(current_year) + timestamp[xpos-3:]
        
        # Parse the string into a datetime object, ignoring the milliseconds part
        dt = datetime.strptime(timestamp, '%b %d, %Y %H:%M:%S')
        # Convert to ISO 8601 format with UTC 'Z' (ignoring milliseconds)
        iso_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        # we need to estimate categories. See https://www.abuseipdb.com/categories for details
        if port == 22:
            categories = "18,20,22"
        else:
            if port == 80 or port == 443:
                categories = "10,18"
            else:
                if port == 3606:
                    categories = "16"
                else:
                    categories = "14"

        # get comment
        comment  = f"iptables detected banned {protocol} traffic on port {port}"

        if False:
            #
            # lets display
            #
            self.logger.debug(f"Comment   : {comment}")
            self.logger.debug(f"Port      : {port}")
            self.logger.debug(f"Categories: {categories}")
            self.logger.debug(f"Protocol  : {protocol}")
            self.logger.debug(f"ip_address: {ip_address}")
            self.logger.debug(f"time      : {iso_timestamp}")
            self.logger.debug(f"IPv6      : {ipv6_flag}")

        # build a work unit
        data = f"Tasklet_notify_abuseIPDB"
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

        # say we handled the zDROP for the caller
        return True

# wait_and_process
def wait_and_process(data, **kwargs):
    # get args from kwargs
    work_controller = kwargs.get('work_controller', None)
    message_manager = kwargs.get('message_manager', None)
    database_connection_pool = kwargs.get('database_connection_pool', None)

    tasklet_zdrop = Tasklet_ZDrop(work_controller, message_manager, database_connection_pool)
    
    while True:
        message_unit = message_manager.dequeue()
        if message_unit is None: #shutdown condition
            print("Shutting down Tasklet_ZDrop")
            break
        tasklet_zdrop.is_zdrop(message_unit.get_message_string())

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Sample input strings
    input_strings = [
        "Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=110.175.220.250 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0",
        "Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=201:18::1 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0"
    ]

    # Initialize the necessary components for Tasklet_ZDrop
    work_controller = WorkManager.WorkController(num_workers=1)
    message_manager = MessageManager.MessageManager()

    # Create an instance of Tasklet_ZDrop
    tasklet_zdrop = Tasklet_ZDrop(work_controller, message_manager)

    # Enqueue the sample input strings into the message manager
    for input_str in input_strings:
        message_manager.enqueue(input_str)

    # Enqueue a special message to signal shutdown
    # - garbage from ChatGPT 4o - message_manager.enqueue(None)  # This will act as the shutdown signal
    
    # Start processing messages using Tasklet_ZDrop
    while message_manager.is_enqueued() > 0:

        print(f"is_enqueued() = {message_manager.is_enqueued()}")
        
        message_unit = message_manager.dequeue()
        if message_unit is None:  # Shutdown condition
            print("Shutting down Tasklet_ZDrop")
            break
        tasklet_zdrop.is_zdrop(message_unit.get_message_string())

    print("Broke out of loop")
    
    # Simulate shutdown (this would typically happen based on some condition)
    message_manager.shutdown()

    work_controller.initiate_shutdown()
    work_controller.wait_for_worker_threads_to_finish()

    print("Done")
