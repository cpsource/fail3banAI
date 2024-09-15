import inspect

class Example:
    def __init__(self):
        self.debug = True
        self.system_log_level = "WARN"  # Set the current system log level (WARN or above)

    def debug_print(self, message, error_level="DEBUG", error_info=None):
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
                print(f"[{error_level}] ErrStr: {error_string}, File: {file}, Line: {line}")
            else:
                # Get the caller's file and line number using inspect
                caller_frame = inspect.currentframe().f_back  # Get the caller's frame
                file = caller_frame.f_code.co_filename  # Get the caller's file name
                line = caller_frame.f_lineno  # Get the caller's line number
                print(f"[{error_level}] Pgm: {file}, Line: {line}")
            
            # Print the main debug message with the error level
            print(f"[{error_level}] {message}")

# Test the debug_print method with a main function

def main():
    example = Example()

    print("Testing with system_log_level = WARN\n")

    # Testing with various log levels
    example.debug_print("This is an INFO message.", error_level="INFO")   # Will not print due to system_log_level
    example.debug_print("This is a DEBUG message.", error_level="DEBUG") # Will not print due to system_log_level
    example.debug_print("This is a WARN message.", error_level="WARN")   # Will print
    example.debug_print("This is an ERROR message.", error_level="ERROR") # Will print

    # Testing with an error_info list
    example.debug_print(
        "This is an ERROR message with error_info.",
        error_level="ERROR",
        error_info=["Custom error occurred", __file__, inspect.currentframe().f_lineno]
    )

if __name__ == "__main__":
    main()

