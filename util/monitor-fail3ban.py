#!/usr/bin/env python3

import os
import sys

def save_pid(pid_file):
    pid = os.getpid()  # Get the current process ID (PID)
    
    # Save the PID to the specified file
    try:
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        print(f"PID {pid} saved to {pid_file}")
    except PermissionError:
        print(f"Permission denied: Unable to write to {pid_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def daemonize(log_file="/dev/null"):
    try:
        # First fork to create a background process
        pid = os.fork()
        if pid > 0:
            # Parent process, exit
            return "parent"
        
        # Detach from parent environment
        os.setsid()

        # Second fork to prevent acquiring a terminal again
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        with open(log_file, 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())

        # Child process continues as daemon
        return "child"

    except OSError as e:
        sys.stderr.write(f"fork failed: {e.errno} ({e.strerror})\n")
        sys.exit(1)

# Check if there are command line arguments
status = None
if '--daemonize' in sys.argv:
    status = daemonize('/tmp/monitor-fail3ban.log')
    
if status is not None and status == 'parent':
    sys.exit(0)
# Save our pid - must be done after a possible daemonize
pid_file = '/tmp/monitor-fail3ban.pid'
save_pid(pid_file)
   
#import subprocess
import tempfile
#import re
import ipaddress
from dotenv import load_dotenv
import subprocess
import signal
import threading
import ipaddress; is_ipv6 = lambda addr: isinstance(ipaddress.ip_address(addr), ipaddress.IPv6Address)
import re
from datetime import datetime
import time

# Configure logging
import logging
# and some magic numbers for logging
FLAG_CRITICAL = 50
FLAG_ERROR = 40
FLAG_WARNING = 30
FLAG_INFO = 20
FLAG_DEBUG = 10
FLAG_NOSET = 0

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

# load dotenv
try:
    # Attempt to load dotenv file using the environment variable
    dotenv_config = load_dotenv(f"{os.getenv('HOME')}/.env")
    logger.info("dotenv file loaded successfully.")
except Exception as e:
    # Handle any exceptions that may occur
    logger.error(f"An error occurred while loading dotenv: {e}")

#
# Load our python3 paths
#
# Get the FAIL3BAN_PROJECT_ROOT environment variable

# Step 1: Get the FAIL3BAN_PROJECT_ROOT environment variable

project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
# Check if FAIL3BAN_PROJECT_ROOT is not set
if project_root is None:
    print("Error: The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
    sys.exit(1)  # Exit the program with an error code
# Construct the lib path

# Example of loading startup code at the beginning of any script
#startup_file = os.path.join(os.getenv('FAIL3BAN_PROJECT_ROOT', ''), 'lib', 'startup.py')
#if os.path.exists(startup_file):
#    exec(open(startup_file).read())
# Continue with the rest of your script
#print("Script is running")

# Add the constructed path to sys.path only if it's not already in sys.path
# Step 2: Construct the paths for lib and parselets
lib_path = os.path.join(project_root, 'lib')
parselets_path = os.path.join(project_root, 'lib/parselets')
tasklets_path = os.path.join(project_root, 'lib/tasklets')

# Step 3: Check if parselets_path is already in sys.path, if not, prepend it
if parselets_path not in sys.path:
    sys.path.insert(0, parselets_path)
    print(f"Prepending {parselets_path} to sys.path")

# Step 4: Check if tasklets_path is already in sys.path, if not, prepend it
if tasklets_path not in sys.path:
    sys.path.insert(0, tasklets_path)
    print(f"Prepending {tasklets_path} to sys.path")

# Step 5: Check if lib_path is already in sys.path, if not, prepend it
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
    print(f"Prepending {lib_path} to sys.path")

    
print(sys.path)

# Get the absolute path of the current directory (the directory containing this script)
#current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the subdirectory to the system path
#subdirectory_path = os.path.join(current_dir, '../lib')
#sys.path.append(subdirectory_path)

# Setup Checkpoint
from Checkpoint import Checkpoint
CHECKPOINT_PATH = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/checkpoint.ctl"
checkpoint = Checkpoint(CHECKPOINT_PATH)

from PreviousJournalctl import PreviousJournalctl

# get HashedSet
import f3b_HashedSet

# get CountryCode
import CountryCodes

# get ShortenJournalString
import ShortenJournalString

# get database
import Maria_DB

# get whitelist
import WhiteList

# get GlobalShutdown
from GlobalShutdown import GlobalShutdown

# get our work manager
import WorkManager

# get our message manager
import MessageManager

# our blacklist
import BlackList

# database pool
import MariaDBConnectionPool

#
# Tasklets, be sure to add to message_manager
#
# a thread to handle zdrops
import Tasklet_ZDrop
# tasklet Console
import Tasklet_Console
# tasklet Apache2 Access Logging
import Tasklet_apache2_access_log

# 
#
# Here's a double line that needs to be combined
# into one line, so we can process it effectively.
# I suggest we keep track of the previous line and
# combine them if the [digits] and [jail] are the same.
#

#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: error: kex_exchange_identification: Connection closed by remote host
#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: Connection closed by 104.152.52.121 port 51587

# Path to the temporary file in /tmp
#temp_file = tempfile.NamedTemporaryFile(delete=False, dir='/tmp', mode='w', prefix='journal_', suffix='.log')

import subprocess
import re
import time

def find_country(ip_address_string):
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
                tmp_country_code = cc.get_country(tmp_country).strip()
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


# Function to delete temporary files created by the script
def clean_temp_files():
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)
    #print("Cleaned up temporary files.")

# Function to check if a jail is enabled by searching for 'enabled = true' or 'enabled = false'
import re

# If we have a valid checkpoint, we must tell journalctl
since_time = checkpoint.get()
if since_time is None:
    command = ['journalctl', '-f']
else:
    command = ['journalctl', '-f', f'--since={since_time}']
#print(f"command = {command}")

# Start journalctl
journalctl_proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Setup database pool
database_connection_pool = MariaDBConnectionPool.MariaDBConnectionPool(logger, pool_size=10 )

# Setup blacklist
bl = BlackList.BlackList(database_connection_pool)
print(f"Number of blacklisted items: {len(bl.get_blacklist())}")

# use new PreviousJournalctl class
prevs = PreviousJournalctl()
# and our HashedSet class
hs = f3b_HashedSet.HashedSet()
# and our country codes class
cc = CountryCodes.CountryCodes()
# and our ShortenJournalString
sjs = ShortenJournalString.ShortenJournalString()
# setup database
db = Maria_DB.Maria_DB(database_connection_pool)
db.reset_hazard_level()
db.show_threats()
# and GlobalShutdown
gs = GlobalShutdown()
# get rid of stale control flag
gs.cleanup()

# our whitelist
wl = WhiteList.WhiteList()

def remove_pid(pid_file):
    # Check if the PID file exists
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)  # Remove the PID file
            print(f"PID file {pid_file} removed successfully.")
        except PermissionError:
            print(f"Permission denied: Unable to remove {pid_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"PID file {pid_file} does not exist.")

#
# signaling
#

# Create a global event object to signaling threads to stop
stop_event = threading.Event()

# this guy makes sure we flush our checkpoint from time to time
worker_thread_id = None
# worker_thread flushes our checkpoint cache ever 15 seconds
def worker_thread():
    #print("Thread started.")
    while not stop_event.is_set():
        #print("Thread worker_thread is working...")
        checkpoint.flush_cache()
        # Instead of a long sleep, break it into shorter intervals
        for _ in range(10*3):  # Total sleep time = 10 * 3 * 0.5 = 15 seconds
            if stop_event.is_set():
                break

            time.sleep(0.5)  # Sleep in shorter intervals to check the event frequently
    print("worker_thread (checkpoint) is stopping.")

work_controller = WorkManager.WorkController(num_workers=10)
message_manager = MessageManager.MessageManager(("Default",
                                                 "Tasklet_ZDrop",
                                                 "Tasklet_Console",
                                                 "Tasklet_apache2_access_log",
                                                 ))
def task_callback(msg):
    print(f"task_callback: {msg}")

#
# Start various tasklets
#

# build and run Tasklet_ZDrop
data = "Tasklet_ZDrop"
work_unit = WorkManager.WorkUnit(
    function=Tasklet_ZDrop.wait_and_process,
    kwargs={'data'       : data,
            'work_controller' : work_controller,
            'message_manager' : message_manager,
            'database_connection_pool' : database_connection_pool
            },  # Using kwargs to pass arguments
    callback=task_callback
)
work_controller.enqueue(work_unit)

# build and run Tasklet_Console
data = "Tasklet_Console"
work_unit = WorkManager.WorkUnit(
    function=Tasklet_Console.run_tasklet_console,
    kwargs={'data'       : data,
            'work_controller' : work_controller,
            'message_manager' : message_manager,
            'database_connection_pool' : database_connection_pool
            },  # Using kwargs to pass arguments
    callback=task_callback
)
work_controller.enqueue(work_unit)

# build and run Tasklet_apache2_access_log
data = "Tasklet_apache2_access_log"
work_unit = WorkManager.WorkUnit(
    function=Tasklet_apache2_access_log.run_tasklet_apache2_access_log,
    kwargs={'data'                     : data,
            'stop_event'               : stop_event,
            'logger'                   : logger,
            'database_connection_pool' : database_connection_pool,
            'work_controller'          : work_controller,
            'message_manager'          : message_manager,
            },
    callback=task_callback
)
work_controller.enqueue(work_unit)

# Get a ZDROP instance
#zdr = ZDrop.ZDrop(work_controller, message_manager)

def handle_signal(signum, frame):
    print("Received SIGHUP signal.")
    # Add custom handling here, like reloading configuration
    # sys.exit(0) # Uncomment if you want the program to exit on SIGHUP
    stop_event.set() # Set the event, signaling all threads to stop
    if worker_thread_id is not None:
        worker_thread_id.join()
    gs.request_shutdown()
    work_controller.shutdown()
    message_manager.shutdown()
    database_connection_pool.shutdown()
    
# Register the signal handler for SIGTERM, SIGHUP, etc.
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGHUP, handle_signal)

# Create and start worker thread
worker_thread_id = threading.Thread(target=worker_thread)
worker_thread_id.start()

# run a test one time
tst = False

# Our Main Loop - TODO: belongs as a Tasklet/Parselet
try:
    while not stop_event.is_set() and not gs.is_shutdown():
        # Process each line from journalctl -f
        for line in journalctl_proc.stdout:
            # Clean up previous temporary files
            #clean_temp_files()

            # should we exit ???
            if gs.is_shutdown():
                # yes
                break

            line = line.strip()

            # Lets skip audit lines for now
            is_audit_present = ' audit[' in line
            if is_audit_present is False:
                is_audit_present = ' audit: ' in line                
            if is_audit_present is True:
                continue
            
            print(f"mainloop: line = <{line}>")

            tmp_date = sjs.get_datetime(line)
            if tmp_date is not None:
                print(f"Updating Checkpoint with date {tmp_date}")
                checkpoint.set(tmp_date)

            if tst is True:
                line = "Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=127.0.0.1 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0"
                tst = False
                print("tst enqueue line")
                msg = message_manager.enqueue(line)
                time.sleep(10)
                sys.exit(0)
                
            # zDROP check, make a copy of the line before we pass it in
            if 'zDROP' in line:
                # send a message to Tasker_ZDROP
                print(f"enqueue line <{line}>")
                msg = message_manager.enqueue(line)
                time.sleep(.01) # priority scheduling in Python3 - What a joke.
                continue
            
            # Now save on our previous entries list
            line_copy = line[:]
            prevs.add_entry(line_copy)

            # combine
            result = prevs.combine()
            if result is not None:
                result = result.strip()
            else:
                logger.fatal("result can't be None")
                sys.exit(0)

            print(f"combine_result: {result}")
            
            # is there an ip address in result ???
            result_copy = result[:]
            found_dict, shortened_str = sjs.shorten_string(result_copy)

            # debug

            logger.debug(f"shortened_str = {shortened_str}")
            
            if 'ip_address' in found_dict:
                ip_address = found_dict['ip_address']
                # debgging info
                #logging.debug(f"ip_address found by shorten_string is {ip_address}")
            else:
                # debgging info
                #logging.debug(f"no ip_address found, skipping line")
                # we are done if there is not ip_address, on to the next line
                continue

            # get country and bad_dude_status
            country = None
            bad_dude_status = "n/a"
            if ip_address is not None:
                country = find_country(ip_address)
                # is this ip address in HashedSet
                if hs.is_ip_in_set(ip_address) :
                    # yep, a really bad dude
                    bad_dude_status = True
                else:
                    # nope, but a bad dude anyway
                    bad_dude_status = False

            #  is ip_address in our whitelist ???
            ip_address_in_whitelist = None
            if ip_address is not None:
                # check that this ip is not in the whitelist
                if wl.is_whitelisted(ip_address) is True:
                    ip_address_in_whitelist = True
                else:
                    ip_address_in_whitelist = False                    

            # check hazard level from table threat_table in database
            hazard_level = "unk"
            tmp_flag, tmp_hazard_level = db.fetch_threat_level(shortened_str)
            # was the record found in the database ???
            if tmp_flag is True:
                # yes
                hazard_level = tmp_hazard_level
            else:
                pass

            # format message to be displayed
            formatted_string = (
                f"Line      : {result if result is not None else 'n/a'}\n"
                f"Dictionary: {found_dict if found_dict is not None else 'n/a'}\n"
                f"Shortened : {shortened_str if shortened_str is not None else 'n/a'}\n"
                f"BadDude   : {True if bad_dude_status else 'False'}\n"            
                f"Country   : {country if country is not None else 'n/a'}"
                f"InWhiteLst: {ip_address_in_whitelist if ip_address_in_whitelist is not None else 'n/a'}"
                f"InDB      : In DB: {tmp_flag} Hazard Level: {hazard_level}"
            )
            # and display it
            print(formatted_string)
            print("-" * 50)
        
            if False:
                # if we are debugging,
                if logger.getEffectiveLevel() <= FLAG_DEBUG :
                    # at this point, we'd want to check with ChatGPT to ascertain the hazard_level level
                    # then add to our threat database
                    db.insert_or_update_threat(shortened_str, 1, hazard_level)

            # done processing this line
            continue
        else:
            continue
        
except KeyboardInterrupt:
    logging.error("Script interrupted. Exiting...")
    stop_event.set()
    if worker_thread_id is not None:
        worker_thread_id.join()
finally:
    work_controller.shutdown()
    remove_pid(pid_file)
    gs.cleanup()
    message_manager.shutdown()
    database_connection_pool.shutdown()
