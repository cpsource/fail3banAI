import os
import importlib.util
import sys

class TaskletManager:
    def __init__(self, root_dir='.'):
        self.root_dir = root_dir
        self.tasklets = []  # This will store information about all found tasklets
        self.load_tasklets()

    def load_tasklets(self):
        """
        Walk through the directory tree below root_dir and find all tasklets 
        named Tasklet_<name>.py, dynamically loading them.
        """
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.startswith("Tasklet_") and filename.endswith(".py"):
                    tasklet_name = filename[:-3]  # Remove the .py extension
                    tasklet_path = os.path.join(dirpath, filename)
                    self.load_tasklet(tasklet_name, tasklet_path)

    def load_tasklet(self, tasklet_name, tasklet_path):
        """
        Dynamically load a tasklet from its file path.
        """
        # Create a module spec from the file
        spec = importlib.util.spec_from_file_location(tasklet_name, tasklet_path)
        if spec is None:
            print(f"Could not load spec for {tasklet_name}")
            return

        # Create a new module from the spec
        module = importlib.util.module_from_spec(spec)

        # Load the module
        try:
            spec.loader.exec_module(module)
            # Assume the tasklet class has the same name as the file without the extension
            tasklet_class = getattr(module, tasklet_name, None)
            if tasklet_class:
                # Add the tasklet to our tasklet table (self.tasklets)
                self.tasklets.append({
                    'name': tasklet_name,
                    'path': tasklet_path,
                    'module': module,
                    'class': tasklet_class
                })
                print(f"Loaded tasklet: {tasklet_name}")
            else:
                print(f"Tasklet class {tasklet_name} not found in {tasklet_path}")
        except Exception as e:
            print(f"Error loading tasklet {tasklet_name}: {e}")

    def get_tasklet_names(self):
        """
        Return a list of all loaded tasklet names.
        """
        return [tasklet['name'] for tasklet in self.tasklets]

    def execute_tasklet_method(self, tasklet_name, method_name, *args, **kwargs):
        """
        Dynamically execute a method on a loaded tasklet by its name.
        """
        for tasklet in self.tasklets:
            if tasklet['name'] == tasklet_name:
                tasklet_instance = tasklet['class']()  # Create an instance of the tasklet class
                if hasattr(tasklet_instance, method_name):
                    method = getattr(tasklet_instance, method_name)
                    return method(*args, **kwargs)
                else:
                    print(f"Method {method_name} not found in tasklet {tasklet_name}")
                    return None
        print(f"Tasklet {tasklet_name} not found")
        return None

# Example usage:
if __name__ == "__main__":
    manager = TaskletManager()

    # List all loaded tasklets
    print("Loaded Tasklets:")
    print(manager.get_tasklet_names())

    if False:
        # Example of executing a method from Tasklet_GETen
        log_line = '64.225.75.246 - - [28/Sep/2024:00:31:27 +0000] "GET /.env HTTP/1.1" 302 841 "-" "Go-http-client/1.1"'
        result = manager.execute_tasklet_method('Tasklet_GETenv', 'compress_line', log_line)
        if result:
            print("Result from Tasklet_GETen.compress_line:")
            print(result)

