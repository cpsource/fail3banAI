# obsolete - TODO remove

import os
import sys

class GlobalShutdown:
    def __init__(self):
        self.shutdown_file = "/tmp/fail3ban-global-shutdown"

    def request_shutdown(self):
        """Creates the shutdown file."""
        with open(self.shutdown_file, 'a'):
            os.utime(self.shutdown_file, None)  # Touch the file

    def is_shutdown(self):
        """Returns True if the shutdown file exists, False otherwise."""
        return os.path.exists(self.shutdown_file)

    def cleanup(self):
        """Removes the shutdown file."""
        if os.path.exists(self.shutdown_file):
            os.remove(self.shutdown_file)

def print_help():
    """Prints the help message."""
    help_message = """
Usage: global_shutdown.py [command]

Commands:
  status      Check if the shutdown is requested
  shutdown    Request a global shutdown
  cleanup     Remove the shutdown request file
  -h, --help  Show this help message
"""
    print(help_message)

def main():
    shutdown = GlobalShutdown()

    # Handle command-line arguments
    if len(sys.argv) == 1:
        # No arguments: perform the default test sequence
        print("Running test sequence:")
        # Step 1: Test that is_shutdown is initially False
        print("Testing is_shutdown before requesting shutdown:")
        if shutdown.is_shutdown():
            print("Test failed: Shutdown file should not exist.")
        else:
            print("Test passed: No shutdown file initially.")

        # Step 2: Request a shutdown and verify is_shutdown is True
        shutdown.request_shutdown()
        print("Testing is_shutdown after requesting shutdown:")
        if shutdown.is_shutdown():
            print("Test passed: Shutdown file exists after request.")
        else:
            print("Test failed: Shutdown file should exist after request.")

        # Step 3: Cleanup the shutdown file and verify is_shutdown is False
        shutdown.cleanup()
        print("Testing is_shutdown after cleanup:")
        if shutdown.is_shutdown():
            print("Test failed: Shutdown file should not exist after cleanup.")
        else:
            print("Test passed: Shutdown file was successfully removed.")

    elif len(sys.argv) == 2:
        # One argument: handle specific commands
        command = sys.argv[1].lower()

        if command == "status":
            if shutdown.is_shutdown():
                print("Shutdown is active (file exists).")
            else:
                print("No shutdown requested (file does not exist).")

        elif command == "shutdown":
            shutdown.request_shutdown()
            print("Shutdown has been requested (file created).")

        elif command == "cleanup":
            shutdown.cleanup()
            print("Shutdown has been cleaned up (file removed).")

        elif command == "-h" or command == "--help":
            print_help()

        else:
            print("Error: Unrecognized command.")
            print_help()

    else:
        # More than one argument or invalid command
        print("Error: Invalid number of arguments.")
        print_help()

# Run the script
if __name__ == "__main__":
    main()

