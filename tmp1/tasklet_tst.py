import os
import sys
import threading
import time
from datetime import datetime
import WorkManager2

cmd_str = "2024-09-25 14:22:01,379 - monitor-fail3ban.py:434 - DEBUG - shortened_str = <datetime> <destination-ip> kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=200.192.212.59 DST=172.26.10.222 LEN=52 TOS=0x00 PREC=0x00 TTL=48 ID=32242 DF PROTO=TCP SPT=55308 DPT=22 WINDOW=14520 RES=0x00 SYN URGP=0"

ip_address = "104.40.75.134"
categories = "18,20"
comment    = "iptables detected a banned ip on port 22"
timestamp  = "2024-09-25 14:22:01,379"

#2023-10-18T11:25:11-04:00

if False:
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

from Tasklet_hello_world import Tasklet_hello_world

def task_callback(result):
    print(f"Task completed with result: {result}")

def worker_thread(work_manager, thread_id):
    while True:
        work_unit = work_manager.dequeue()
        if work_unit is None:
            print(f"Worker thread {thread_id} shutting down.")
            break
        work_unit.execute()

# Create a WorkManager instance
work_manager = WorkManager2.WorkManager()

# Start worker threads
num_workers = 3
workers = []
for i in range(num_workers):
    t = threading.Thread(target=worker_thread, args=(work_manager, i+1))
    t.start()
    workers.append(t)
    print(f"Worker thread {i+1} started.")

# kick off our Tasklet task
# Enqueue some WorkUnits with kwargs example
for i in range(1):
    data = f"data_{i}"
    work_unit = WorkManager2.WorkUnit(
        function=Tasklet_hello_world,
        kwargs={'data': data,
                'ip_address' : ip_address,
                'categories' : categories,
                'comment'    : comment,
                'timestamp'  : timestamp
                },  # Using kwargs to pass arguments
        callback=task_callback
    )
    work_manager.enqueue(work_unit)
    print(f"Enqueued work unit with {data}")
    time.sleep(0.5)  # Simulate time between enqueuing tasks

# Wait for all tasks to be processed
while True:
    with work_manager.condition:
        if not work_manager.queue:
            break
    time.sleep(0.1)

# Initiate shutdown
print("Initiating shutdown.")
work_manager.shutdown()

# Wait for worker threads to finish
for worker in workers:
    worker.join()
print("All worker threads have been shut down.")

# Exiting ...
print("Exiting ...")
sys.exit(0)

# try our Tasklet
# Enqueue some WorkUnits with kwargs example
for i in range(1):
    data = f"data_{i}"
    work_unit = WorkUnit(
        function=sample_task,
        kwargs={'data': data, 'test-string' : 'Hello World'},  # Using kwargs to pass arguments
        callback=task_callback
    )
    work_manager.enqueue(work_unit)
    print(f"Enqueued work unit with {data}")
    time.sleep(0.5)  # Simulate time between enqueuing tasks

# Enqueue some WorkUnits with kwargs example
for i in range(1):
    data = f"data_{i}"
    work_unit = WorkUnit(
        function=sample_task,
        kwargs={'data': data, 'test-string' : 'Hello World'},  # Using kwargs to pass arguments
        callback=task_callback
    )
    work_manager.enqueue(work_unit)
    print(f"Enqueued work unit with {data}")
    time.sleep(0.5)  # Simulate time between enqueuing tasks

    # Wait for all tasks to be processed
    while True:
        with work_manager.condition:
            if not work_manager.queue:
                break
        time.sleep(0.1)

    # Initiate shutdown
    print("Initiating shutdown.")
    work_manager.shutdown()

    # Wait for worker threads to finish
    for worker in workers:
        worker.join()
    print("All worker threads have been shut down.")

#Tasklet_hello_world()
