import re
import os
import atexit
import logging
from logging import getLogger

log_id = 'fail3ban'
logger = logging.getLogger(log_id)

class Config:
    def __init__(self, config_file='config.ctl'):
        self.config_data = {}
        self.load_config(config_file)
        self.log_id = 'fail3ban'
        self.logger = getLogger(log_id)
        # register a cleanup
        atexit.register(self.cleanup)

    @staticmethod
    def get_ctl_path(control_file_name):
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Check if the current directory ends with '/lib'
        if re.search(r'.*/lib\Z', current_dir):
            # Return path for lib context
            return os.path.join('..', 'control', control_file_name)
        # Check if the current directory ends with '/fail3banAI'
        elif re.search(r'.*/fail3banAI\Z', current_dir):
            # Return path for fail3banAI context
            return os.path.join('control', control_file_name)
        else:
            # Handle other cases (optional)
            return None
        
    def get_config_data(self):
        return self.config_data
    
    def load_config(self, config_file):
        """Read the config.ctl file and store variable-value pairs."""
        # Open the config.ctl file
        control_file = Config.get_ctl_path(config_file)
        if not control_file:
            control_file = 'fail3ban'
        try:
            with open(control_file, 'r') as file:
                for line in file:
                    # Strip whitespace and skip comments and empty lines
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split the line into variable and value
                    if '=' in line:
                        variable, value = map(str.strip, line.split('=', 1))
                        # Check if the variable is 'default_ban_time'
                        if variable == 'default_ban_time':
                            # Define a regex to match <digits>[ \t]*[h, d, w, m, y]
                            match = re.match(r'(\d+)[ \t]*([hdwmy])', value)
                            if match:
                                # Extract the numeric part and the time unit
                                num_value = int(match.group(1))
                                time_unit = match.group(2)
                                # Define the time multipliers
                                multipliers = {'h': 60, 'd': 1440, 'w': 10080, 'm': 302400, 'y': 3628800}
                                # Multiply the value by the corresponding multiplier
                                value = num_value * multipliers[time_unit]
                        self.config_data[variable] = value

        except FileNotFoundError:
            print(f"Error: {control_file} not found.")
        except Exception as e:
            print(f"An error occurred while reading {control_file}: {e}")

        # return this dictionary
        return self.config_data
    
    def get_value(self, variable_name):
        """Retrieve the value of the specified variable."""
        return self.config_data.get(variable_name, None)

    def cleanup(self):
        try:
            self.config_data = None
        except Exception as e:
            self.logger.error(f"Exception during cleanup: {e}")

if __name__ == "__main__":
    # Create a Config instance and load the config.ctl file
    config = Config('config.ctl')

    # Test getting values
    test_variable = 'debug'
    result = config.get_value(test_variable)

    if result is not None:
        print(f"The value for '{test_variable}' is: {result}")
    else:
        print(f"'{test_variable}' not found in config.ctl")

