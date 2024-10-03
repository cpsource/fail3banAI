import os
import importlib
import sys
import json
import re

class Dynamic_Importer_apache2_access_log:
    def __init__(self, directory):
        self.directory = directory
        self.modules = {}

        # Add the directory to the Python search path
        self.add_to_python_path(self.directory)

        # Get the list of files that match Parselet_*.py
        file_list = self.get_file_list(self.directory)
        print(f"file list = {file_list}")
        
        # Import the selected files
        self.import_modules(file_list)

    def print_supported_methods(self,obj):
        pass
        #methods = [method for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith("__")]
        #print("Supported methods:", methods)
    
    def extract_parselet_class(self,filepath):
        match = re.search(r'(Parselet_[A-Za-z0-9_]+)\.py', filepath)
        if match:
            return match.group(1)
        return None
        
    def add_to_python_path(self, directory_path):
        """ Adds the directory_path to the front of the Python library search path (sys.path) """
        if os.path.isdir(directory_path):
            print(f"Adding {directory_path} to Python path.")
            # Insert the directory path at the front of sys.path
            sys.path.insert(0, directory_path)
            print(f"Current Python path: {sys.path}")
        else:
            print(f"Directory {directory_path} does not exist.")

    def get_file_list(self, directory_path):
        """ Returns a list of files in directory_path that match the pattern Parselet_*.py """
        file_list = []
        print(f"Scanning directory: {directory_path}")
        for root, dirs, files in os.walk(directory_path):
            print(f"Entering directory: {root}")  # Debugging information for each directory
            for file_name in files:
                # Debugging information for each file found
                print(f"Found file: {file_name}")
                
                # Only process Python files with the form Parselet_*.py
                if file_name.startswith('Parselet_') and file_name.endswith('.py'):
                    print(f"Selected file for import: {file_name}")  # File selected for import
                    # Add full path to the file list
                    file_list.append(os.path.join(root, file_name))
                    
        return file_list

    def import_modules(self, file_list):
        """ Imports modules from the list of files passed in file_list """
        for module_path in file_list:
            module_name = self.extract_parselet_class(module_path)
            
            # Build the module path (relative path without '.py')
            #relative_module_path = os.path.relpath(module_path, self.directory)
            #module_name = relative_module_path[:-3].replace(os.path.sep, '.')

            # Add the top-level directory to module path for import
            #full_module_name = f"{self.directory}.{module_name}".replace(os.path.sep, '.')
            #print(f"Attempting to import module: {full_module_name}")  # Debugging info before import

            # Import the module dynamically
            try:
                module = importlib.import_module(module_name)
                self.modules[module_name] = module
                print(f"Successfully imported {module_name}")  # Debugging info after success
            except ImportError as e:
                print(f"Error importing {module_name}: {e}")  # Debugging info for errors

    def compress_line(self, input_string):
        #print(f"compress_line: input_string = {input_string}")

        # Walk through the imported modules and call compress_line(input_string) on each
        for module_name, module in self.modules.items():
            #print(f"compress_line: module_name = {module_name}, module={module}")
            self.print_supported_methods(module)
            try:
                # Call the compress_line function in the module
                result = module.compress_line(input_string)

                #print(f"result = {result}")
                #print(f"type of result = {type(result)})")

                # Check if the response indicates an error
                if 'No match found' in result:
                    # Continue searching through other modules
                    continue
                else:
                    # Return the result if no error is found
                    return result
            except AttributeError:
                # Handle case where module doesn't have the compress_line function
                print(f"Module {module_name} doesn't implement compress_line.")
            except Exception as e:
                # Handle any other exceptions that might occur
                print(f"Error calling compress_line in module {module_name}: {e}")

        # If no module matched, return the error response
        return json.dumps({
            "class_name": self.__class__.__name__,
            "error": "No match found"
        })

# Example usage in __main__
if __name__ == "__main__":
    # Assume the directory 'my_directory' contains the modules you want to import
    my_directory = os.getenv('FAIL3BAN_PROJECT_ROOT') + '/lib/parselets/apache2/access-log'
    dynamic_importer = Dynamic_Importer_apache2_access_log(my_directory)

    test_inputs = (
        '2602:80d:1002::18 - - [03/Oct/2024:14:13:04 +0000] "PRI * HTTP/2.0" 400 488 "-" "-"',
        '154.213.187.244 - - [03/Oct/2024:14:28:01 +0000] "CONNECT google.com:443 HTTP/1.1" 200 569 "-" "Go-http-client/1.1"',
        '154.213.187.244 - - [03/Oct/2024:14:28:01 +0000] "\x16\x03\x01" 400 488 "-" "-"',
        '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'
    )

    # Test input string to be passed
    for line in test_inputs:
        # Call compress_line with the test input and print the result
        result = dynamic_importer.compress_line(line)
        print(f"Result: {result}")
