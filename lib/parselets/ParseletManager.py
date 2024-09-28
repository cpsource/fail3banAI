import os
import importlib.util
import sys
import threading
import json  # To handle JSON parsing

class ParseletManager:
    def __init__(self, root_dir='.'):
        self.root_dir = os.path.abspath(root_dir)  # Ensure root_dir is an absolute path
        self.parselets = []  # This will store information about all found parselets
        self.loaded_parselets = set()  # Track which parselets have already been loaded by name
        self.lock = threading.Lock()  # Add a lock to protect access to self.parselets
        self.load_parselets()

    def load_parselets(self):
        """
        Walk through the directory tree below root_dir and find all parselets 
        named Parselet_<name>.py, dynamically loading them.
        """
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.startswith("Parselet_") and filename.endswith(".py") and not filename.endswith(".py~"):
                    parselet_name = filename[:-3]  # Remove the .py extension
                    parselet_path = os.path.join(dirpath, filename)
                    self.load_parselet(parselet_name, parselet_path)

    def load_parselet(self, parselet_name, parselet_path):
        """
        Dynamically load a parselet from its file path and add it to the list if not already loaded.
        """
        if parselet_name in self.loaded_parselets:
            return  # Skip if already loaded

        # Create a module spec from the file
        spec = importlib.util.spec_from_file_location(parselet_name, parselet_path)
        if spec is None:
            print(f"Could not load spec for {parselet_name}")
            return

        # Create a new module from the spec
        module = importlib.util.module_from_spec(spec)

        # Load the module
        try:
            spec.loader.exec_module(module)
            # Assume the parselet class has the same name as the file without the extension
            parselet_class = getattr(module, parselet_name, None)
            if parselet_class:
                # Use a lock to safely modify self.parselets
                with self.lock:
                    self.parselets.append({
                        'name': parselet_name,
                        'path': parselet_path,
                        'module': module,
                        'class': parselet_class
                    })
                    self.loaded_parselets.add(parselet_name)  # Mark as loaded
                print(f"Loaded parselet: {parselet_name}")
            else:
                print(f"Parselet class {parselet_name} not found in {parselet_path}")
        except Exception as e:
            print(f"Error loading parselet {parselet_name}: {e}")

    def update_parselets(self):
        """
        Rescan the directory tree and load any new parselets that haven't been loaded yet.
        """
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.startswith("Parselet_") and filename.endswith(".py") and not filename.endswith(".py~"):
                    parselet_name = filename[:-3]  # Remove the .py extension
                    parselet_path = os.path.join(dirpath, filename)
                    if parselet_name not in self.loaded_parselets:
                        print(f"New parselet found: {parselet_name}, loading...")
                        self.load_parselet(parselet_name, parselet_path)

    def get_parselet_names(self):
        """
        Return a list of all loaded parselet names. Protect access with a lock.
        """
        with self.lock:
            return [parselet['name'] for parselet in self.parselets]

    def execute_parselet_method(self, parselet_name, method_name, *args, **kwargs):
        """
        Dynamically execute a method on a loaded parselet by its name. Use a lock during access.
        """
        with self.lock:
            for parselet in self.parselets:
                if parselet['name'] == parselet_name:
                    parselet_instance = parselet['class']()  # Create an instance of the parselet class
                    if hasattr(parselet_instance, method_name):
                        method = getattr(parselet_instance, method_name)
                        return method(*args, **kwargs)
                    else:
                        print(f"Method {method_name} not found in parselet {parselet_name}")
                        return None
            print(f"Parselet {parselet_name} not found")
            return None

    def find_a_match(self, str_to_match, directory_path_of_the_set_of_parselets, index=0):
        """
        Search the parselets in the given directory for a match by calling compress_line.
        Start from the given index and return the result from the first parselet that finds a match.
        Returns the index of the parselet that matched.
        """
        # Normalize the directory path and parselet paths
        normalized_dir_path = os.path.abspath(directory_path_of_the_set_of_parselets)

        # Debug: Print paths for comparison
        print(f"Root directory: {self.root_dir}")
        print(f"Target directory for search: {normalized_dir_path}")

        # Lock access to the parselets list
        with self.lock:
            print(f"Starting find_a_match at index {index} for directory {normalized_dir_path}")
            # Iterate through the loaded parselets starting from the given index
            for i, parselet in enumerate(self.parselets[index:], start=index):
                # Normalize the path of the current parselet
                normalized_parselet_path = os.path.abspath(os.path.dirname(parselet['path']))
                
                # Debug: Print current parselet info
                print(f"Checking parselet {parselet['name']} at index {i}, path: {normalized_parselet_path}")
                
                # Check if the parselet belongs to the given directory
                if normalized_parselet_path == normalized_dir_path:
                    print(f"Parselet {parselet['name']} belongs to {normalized_dir_path}")

                    parselet_instance = parselet['class']()  # Create an instance of the parselet class
                    
                    if hasattr(parselet_instance, 'compress_line'):
                        print(f"Parselet {parselet['name']} has a 'compress_line' method. Trying to compress...")
                        # Call the 'compress_line' method of the parselet
                        result = parselet_instance.compress_line(str_to_match)
                        print(f"Compress result: {result}")
                        
                        # Parse the result to check for errors in the returned JSON
                        try:
                            result_json = json.loads(result)
                            if "error" in result_json and result_json["error"] == "No match found":
                                print(f"No match found in {parselet['name']}. Continuing to next parselet.")
                            else:
                                print(f"Match found in {parselet['name']} at index {i}!")
                                return result_json, i  # Return the result and the index if a match is found
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON from {parselet['name']}")
                    else:
                        print(f"Parselet {parselet['name']} does not have a 'compress_line' method.")
                else:
                    print(f"Parselet {parselet['name']} does not belong to {normalized_dir_path}")
        
        print("No match found.")
        return None, -1  # Return None and -1 if no match is found

# Example usage:
if __name__ == "__main__":
    manager = ParseletManager()

    # List all loaded parselets
    print("Loaded Parselets:")
    print(manager.get_parselet_names())

    # Update parselets (rescan for new ones)
    print("Updating Parselets...")
    manager.update_parselets()

    # Make sure the path doesn't have an extra "parselets" in the directory structure
    correct_directory = '/home/ubuntu/fail3banAI/lib/parselets/apache2/access-log'

    log_line = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'
    # Example of searching for a match in a directory using compress_line
    result, match_index = manager.find_a_match(log_line, correct_directory)
    
    if result:
        print(f"Found a match at index {match_index}!")
        print(result)
    else:
        print("No match found.")

