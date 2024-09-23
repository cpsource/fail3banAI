import os

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


# Main function for testing
def main():
    shutdown = GlobalShutdown()

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

# Run the test
if __name__ == "__main__":
    main()

