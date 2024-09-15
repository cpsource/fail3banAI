import os
import glob
import inspect

class Ruleset:
    def __init__(self, debug=False):
        # Initialize an empty array to store filename, enabled flag, and associated regex rules
        self.rulesets = []
        self.debug = debug  # Set the debug flag

        # Process each *.conf file in the filter.d/ directory
        conf_files = glob.glob('filter.d/*.conf')  # Look for .conf files in filter.d directory
        for filename in conf_files:
            self.debug_print(f"Processing file {filename}")
            self.process_file(filename)

    def debug_print(self, message, error_info=None):
        """Helper method to print debug messages.
        If error_info is provided as [error_string, file, line], display them first.
        Otherwise, get the file and line number from the caller's stack frame."""
    
        if self.debug:
            if error_info and len(error_info) == 3:
                error_string, file, line = error_info
                print(f"Error: {error_string}, File: {file}, Line: {line}")
            else:
                # Get the caller's file and line number using inspect
                caller_frame = inspect.currentframe().f_back  # Get the caller's frame
                file = caller_frame.f_code.co_filename  # Get the caller's file name
                line = caller_frame.f_lineno  # Get the caller's line number
                print(f"Program: {file}, Line: {line}")
        
            # Print the main debug message
            print(f"Debug: {message}")
            
    def contains_host(self, string):
        """Returns True if the string contains '<HOST>', else False."""
        return '<HOST>' in string
            
    def process_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.debug_print(f"Opened file {filename}")
                inside_definition = False
                regexes = []
                enabled = False  # Default enabled flag to False

                for line in file:
                    # Strip whitespace from the line
                    line = line.strip()

                    # Debug: Show the current line
                    self.debug_print(f"Reading line: {line}")

                    # Detect the start of the [Definition] section
                    if line == "[Definition]":
                        inside_definition = True
                        self.debug_print("Entered [Definition] section")
                        continue

                    # If we are inside the [Definition] section, process the file
                    if inside_definition:
                        # Check for the enabled flag
                        if "enabled" in line:
                            if "true" in line.lower():
                                enabled = True
                                self.debug_print("Enabled flag set to True")
                            elif "false" in line.lower():
                                enabled = False
                                self.debug_print("Enabled flag set to False")

                        # If a new section starts, stop processing
                        if line.startswith('[') and line.endswith(']'):
                            self.debug_print(f"Found new section {line}, stopping regex collection")
                            break

                        # Look for the failregex and subsequent lines
                        if line.startswith("failregex"):
                            # Grab the failregex line and subsequent lines
                            regex_part = line.split('=')[1].strip()  # Extract the regex part
                            regex_part = self.adjust_regex(regex_part)

                            # The string must contain a <HOST>
                            if self.contains_host(regex_part):
                                # Append to our list
                                regexes.append(regex_part)
                                self.debug_print(f"Found failregex: {regex_part}")
                            else:
                                self.debug_print(f"  *** Ignoring.\n  *** regex_part = {regex_part}",
                                                 [
                                                     'Error: missing <HOST>',
                                                     __file__,
                                                     inspect.currentframe().f_lineno
                                                 ])

                        elif line.startswith("^") or line.startswith(" "):  # Subsequent regex lines
                            regex_part = self.adjust_regex(line.strip())
                            regexes.append(regex_part)
                            self.debug_print(f"Found subsequent regex: {regex_part}")

                # Add the filename (minus extension), enabled flag, and regexes to the ruleset
                if regexes:
                    self.debug_print(f"Appending ruleset for {filename}")
                    self.rulesets.append([os.path.splitext(os.path.basename(filename))[0], enabled, regexes])
                else:
                    self.debug_print(f"No regexes found in {filename}")
        except FileNotFoundError:
            print(f"Error: {filename} file not found.")
        except Exception as e:
            print(f"An error occurred while processing {filename}: {e}")

    def adjust_regex(self, regex):
        # Replace ^ or ^ followed by spaces with \s* to skip 0 or more spaces
        if regex.startswith("^"):
            return r"\s*" + regex[1:].lstrip()  # Replace ^ and trim any leading spaces after it
        return regex

    def get_rulesets(self):
        # Return the list of all rulesets
        return self.rulesets

    def get_ruleset_by_filename(self, filename):
        # Return the ruleset for a specific filename (without .conf extension)
        for ruleset in self.rulesets:
            if ruleset[0] == filename:
                return ruleset  # Return the [filename, enabled, regexes] for the given filename
        return None  # Return None if the filename doesn't exist

# Example usage
if __name__ == "__main__":
    # Initialize with debug=True to enable debug prints
    rs = Ruleset(debug=True)
    print(rs.get_rulesets())

    # Example of retrieving a specific ruleset by filename (without .conf)
    specific_ruleset = rs.get_ruleset_by_filename('kerio')
    if specific_ruleset:
        print(f"Ruleset for 'kerio': {specific_ruleset}")
    else:
        print("Ruleset not found for 'kerio'")

