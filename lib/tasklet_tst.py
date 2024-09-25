import os
import sys

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

Tasklet_hello_world()
