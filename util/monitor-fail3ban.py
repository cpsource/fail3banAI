#!/usr/bin/env python3

import os
import sys

#
# Up front, handle detach if requested from command line
#
PID_FILE = '/tmp/monitor-fail3ban.pid'
def save_pid(pid_file=PID_FILE):
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
save_pid()
   
#import subprocess
import tempfile
#import re
import ipaddress
from dotenv import load_dotenv
import subprocess
import signal
import threading
import ipaddress; is_ipv6 = lambda addr: isinstance(ipaddress.ip_address(addr), ipaddress.IPv6Address)
#import re
from datetime import datetime
import time
import logging

project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
# Add the constructed path to sys.path only if it's not already in sys.path
lib_path = os.path.join(project_root, 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
    print(f"Prepending {lib_path} to sys.path")

# Get our swiss army knife
import Swan
swan = Swan.Swan()
logger = swan.get_logger()
logger.debug(sys.path)
swan.set_os_path()
swan.load_dotenv()
# Setup Checkpoint - now done by swan

from PreviousJournalctl import PreviousJournalctl

# get HashedSet
import f3b_HashedSet

# get database
import Maria_DB

# get GlobalShutdown
from GlobalShutdown import GlobalShutdown

# get our work manager
import WorkManager

# get our message manager
import MessageManager

# our blacklist
import BlackList

# database pool
import zMariaDBConnectionPool

#
# Tasklets, be sure to add to message_manager
#
# a thread to handle zdrops
import Tasklet_ZDrop
# tasklet Console
import Tasklet_Console
# tasklet Apache2 Access Logging
import Tasklet_apache2_access_log

import subprocess
#import re
import time

if False:
    # Function to delete temporary files created by the script
    def clean_temp_files():
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
            #print("Cleaned up temporary files.")

# Setup database pool
database_connection_pool = zMariaDBConnectionPool.MariaDBConnectionPool(logger, pool_size=10 )
# get our conn
conn = database_connection_pool.get_connection()
# Setup blacklist
bl = BlackList.BlackList(conn)
print(f"Number of blacklisted items: {len(bl.get_blacklist())}")
# and our HashedSet class
hs = f3b_HashedSet.HashedSet()
# setup database
db = Maria_DB.Maria_DB(conn, create_ban_table=True)
db.reset_hazard_level()
db.show_threats()

def remove_pid(pid_file=PID_FILE):
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

# Create a global event object to signaling threads to stop
stop_event = swan.get_stop_event()
# Register the signal handler for SIGTERM, SIGHUP, etc.
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGHUP, handle_signal)
    
# TODO - should be a Tasklet
# this guy makes sure we flush our checkpoint from time to time
worker_thread_id = None
# worker_thread flushes our checkpoint cache ever 15 seconds
def worker_thread(swan):
    checkpoint = swan.get_checkpoint()
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
thread_conn = database_connection_pool.get_connection()
work_unit = WorkManager.WorkUnit(
    function=Tasklet_ZDrop.wait_and_process,
    kwargs={'data'       : data,
            'work_controller' : work_controller,
            'stop_event'      : stop_event,
            'message_manager' : message_manager,
            'conn' : thread_conn,
            'swan' : swan
            },  # Using kwargs to pass arguments
    callback=task_callback
)
work_controller.enqueue(work_unit)

# build and run Tasklet_Console
data = "Tasklet_Console"
thread_conn = database_connection_pool.get_connection()
work_unit = WorkManager.WorkUnit(
    function=Tasklet_Console.run_tasklet_console,
    kwargs={'data'            : data,
            'stop_event'      : stop_event,
            'work_controller' : work_controller,
            'message_manager' : message_manager,
            'conn'            : thread_conn,
            'swan'            : swan
            },  # Using kwargs to pass arguments
    callback=task_callback
)
work_controller.enqueue(work_unit)

# build and run Tasklet_apache2_access_log
data = "Tasklet_apache2_access_log"
thread_conn = database_connection_pool.get_connection()
work_unit = WorkManager.WorkUnit(
    function=Tasklet_apache2_access_log.run_tasklet_apache2_access_log,
    kwargs={'data'                     : data,
            'stop_event'               : stop_event,
            'logger'                   : logger,
            'conn'                     : thread_conn,
            'work_controller'          : work_controller,
            'message_manager'          : message_manager,
            'swan'                     : swan
            },
    callback=task_callback
)
work_controller.enqueue(work_unit)

# build and run Tasklet_journalctl
import Tasklet_journalctl
data = "Tasklet_journalctl"
#thread_conn = database_connection_pool.get_connection()
# we already have a conn, so let this thread have it
thread_conn = conn
work_unit = WorkManager.WorkUnit(
    function=Tasklet_journalctl.run_tasklet_journalctl,
    kwargs={'data'                     : data,
            'stop_event'               : stop_event,
            'logger'                   : logger,
            'conn'                     : thread_conn,
            'work_controller'          : work_controller,
            'message_manager'          : message_manager,
            'swan'                     : swan
            },
    callback=task_callback
)
work_controller.enqueue(work_unit)

def handle_signal(signum, frame):
    print("Received SIGHUP signal.")
    # Add custom handling here, like reloading configuration
    # sys.exit(0) # Uncomment if you want the program to exit on SIGHUP
    stop_event.set() # Set the event, signaling all threads to stop
    if worker_thread_id is not None:
        worker_thread_id.join()
    swan.get_gs().request_shutdown()
    work_controller.shutdown()
    message_manager.shutdown()
    database_connection_pool.shutdown()
    
# Create and start worker thread
worker_thread_id = threading.Thread(target=worker_thread, args=(swan,))
worker_thread_id.start()

# Our Main Loop - hang around
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        logger.error("Script interrupted. Exiting...")
        stop_event.set() # tell others to stop
        if worker_thread_id is not None:
            worker_thread_id.join()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        break

# finish tidying  up
work_controller.shutdown()
remove_pid()
gs.cleanup()
message_manager.shutdown()
database_connection_pool.shutdown()
