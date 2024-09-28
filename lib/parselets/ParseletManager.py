import os
import importlib.util
import sys
import threading

class ParseletManager:
    def __init__(self, root_dir='.'):
        self.root_dir = root_dir
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

# Example usage:
if __name__ == "__main__":
    manager = ParseletManager()

    # List all loaded parselets
    print("Loaded Parselets:")
    print(manager.get_parselet_names())

    # Update parselets (rescan for new ones)
    print("Updating Parselets...")
    manager.update_parselets()

    # Example of executing a method from Parselet_GETenv
    log_line = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'
    result = manager.execute_parselet_method('Parselet_GETenv', 'compress_line', log_line)
    
    if result:
        print("Result from Parselet_GETenv.compress_line:")
        print(result)

