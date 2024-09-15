import inspect

class DebugPrint:
    def __init__(self, config):
        """Initialize DebugPrint and get the system_log_level from the config."""

        # Retrieve system_log_level from the config class
        self.system_log_level = config.get_value("system_log_level")

        # Default to "DEBUG" if system_log_level is not set
        if self.system_log_level not in ["ERROR", "WARN", "INFO", "DEBUG"]:
            self.system_log_level = "DEBUG"

    def print(self, message, error_level=self.system_log_level, error_info=None):
        """Helper method to print debug messages with different error levels.
        If error_info is provided as [error_string, file, line], display them first.
        Only print messages based on system_log_level.
        """

        # Valid error levels
        valid_levels = ["ERROR", "WARN", "INFO", "DEBUG"]

        # Check if error_level is valid, else default to DEBUG
        if error_level not in valid_levels:
            error_level = "DEBUG"

        # Determine if the message should be printed based on system_log_level
        log_priority = valid_levels.index(error_level)
        system_priority = valid_levels.index(self.system_log_level)

        if log_priority > system_priority:
            return  # Don't print the message if it's below the system_log_level

        if self.debug:
            if error_info and len(error_info) == 3:
                error_string, file, line = error_info
                print(f"[{error_level}] Error: {error_string}, File: {file}, Line: {line}")
            else:
                # Get the caller's file and line number using inspect
                caller_frame = inspect.currentframe().f_back  # Get the caller's frame
                file = caller_frame.f_code.co_filename  # Get the caller's file name
                line = caller_frame.f_lineno  # Get the caller's line number
                print(f"[{error_level}] Program: {file}, Line: {line}")
            
            # Print the main debug message with the error level
            print(f"[{error_level}] Debug: {message}")

# Test the DebugPrint class with the system_log_level from config

def main():

    import os
    import sys
    
    #
    # Allow our foundation classes to be loaded
    #
    # Get the absolute path of the current directory (the directory containing this script)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Add the subdirectory to the system path
    subdirectory_path = os.path.join(current_dir, 'lib')
    sys.path.append(subdirectory_path)

    import f3b_config

    # Load the config from config.ctl
    config = f3b_config.Config('config.ctl')

    # Initialize the DebugPrint class using the config
    debug_printer = DebugPrint(config)

    print("Testing with system_log_level from config\n")

    # Testing with various log levels
    debug_printer.print("This is an INFO message.", error_level="INFO")
    debug_printer.print("This is a DEBUG message.", error_level="DEBUG")
    debug_printer.print("This is a WARN message.", error_level="WARN")
    debug_printer.print("This is an ERROR message.", error_level="ERROR")

    # Testing with an error_info list
    debug_printer.print(
        "This is an ERROR message with error_info.",
        error_level="ERROR",
        error_info=["Custom error occurred", __file__, inspect.currentframe().f_lineno]
    )

if __name__ == "__main__":
    main()

