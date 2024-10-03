import os
import importlib
import json

class DynamicImporter:
    def __init__(self, directory):
        self.directory = directory
        self.modules = {}

        # Scan the directory for Python files of the form Parselet_*.py and import them
        self.import_modules()

    def import_modules(self):
        # Walk through the directory and subdirectories for Python files
        print(f"Scanning directory: {self.directory}")
        for root, dirs, files in os.walk(self.directory):
            print(f"Entering directory: {root}")  # Debugging information for each directory
            for file_name in files:
                # Debugging information for each file found
                print(f"Found file: {file_name}")
                
                # Only process Python files with the form Parselet_*.py
                if file_name.startswith('Parselet_') and file_name.endswith('.py'):
                    print(f"Selected file for import: {file_name}")  # File selected for import

                    # Build the module path (relative path without '.py')
                    module_path = os.path.join(root, file_name)
                    relative_module_path = os.path.relpath(module_path, self.directory)
                    module_name = relative_module_path[:-3].replace(os.path.sep, '.')

                    # Add the top-level directory to module path for import
                    full_module_name = f"{self.directory}.{module_name}".replace(os.path.sep, '.')
                    print(f"Attempting to import module: {full_module_name}")  # Debugging info before import

                    # Import the module dynamically
                    try:
                        module = importlib.import_module(full_module_name)
                        self.modules[module_name] = module
                        print(f"Successfully imported {full_module_name}")  # Debugging info after success
                    except ImportError as e:
                        print(f"Error importing {full_module_name}: {e}")  # Debugging info for errors

    def compressed_line(self, input_string):
        # Walk through the imported modules and call compressed_line(input_string) on each
        for module_name, module in self.modules.items():
            try:
                # Call the compressed_line function in the module
                result = module.compressed_line(input_string)
                
                # Check if the response indicates an error
                if isinstance(result, dict) and result.get('error') == "No match found":
                    # Continue searching through other modules
                    continue
                else:
                    # Return the result if no error is found
                    return result
            except AttributeError:
                # Handle case where module doesn't have the compressed_line function
                print(f"Module {module_name} doesn't implement compressed_line.")
            except Exception as e:
                # Handle any other exceptions that might occur
                print(f"Error calling compressed_line in module {module_name}: {e}")

        # If no module matched, return the error response
        return json.dumps({
            "class_name": self.__class__.__name__,
            "error": "No match found"
        })

# Example usage in __main__
if __name__ == "__main__":
    # Assume the directory 'my_directory' contains the modules you want to import
    my_directory = os.getenv('FAIL3BAN_PROJECT_ROOT') + '/lib/parselets/apache2/access-log'
    my_directory = ''
    dynamic_importer = DynamicImporter(my_directory)
    
    # Test input string to be passed
    test_input = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'    
    # Call compressed_line with the test input and print the result
    result = dynamic_importer.compressed_line(test_input)
    print(f"Result: {result}")

