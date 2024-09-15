class Fail3banInit:
    def __init__(self, init_file='init.ctl'):
        # Initialize an empty dictionary to store the variables
        self.variables = {}

        # Read the initialization file
        self.read_init_file(init_file)

    def read_init_file(self, init_file):
        try:
            with open(init_file, 'r') as file:
                for line in file:
                    # Strip whitespace and skip comment lines
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse lines in the format: python-variable = variable-value
                    if '=' in line:
                        key, value = line.split('=', 1)  # Split only at the first '='
                        key = key.strip()
                        value = value.strip()
                        self.variables[key] = value  # Store the variable in the dictionary

        except FileNotFoundError:
            print(f"Error: {init_file} not found.")
        except Exception as e:
            print(f"An error occurred while reading {init_file}: {e}")

    def get_variable(self, variable_name):
        # Return the value of the requested variable, or None if it doesn't exist
        return self.variables.get(variable_name, None)

# Example usage
if __name__ == "__main__":
    # Create an instance of the class and read the init.ctl file
    fail3ban_init = Fail3banInit()

    # Example of retrieving a variable's value by name
    variable_name = 'bantime'
    value = fail3ban_init.get_variable(variable_name)
    
    if value:
        print(f"Value for '{variable_name}': {value}")
    else:
        print(f"Variable '{variable_name}' not found.")

