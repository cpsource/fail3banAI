import importlib
import sys
import inspect

def print_module_methods(module_name):
    try:
        # Dynamically import the module using importlib
        module = importlib.import_module(module_name)
        
        # Get the methods in the module using inspect
        methods = inspect.getmembers(module, inspect.isfunction)
        
        print(f"Methods in module '{module_name}':")
        for name, func in methods:
            print(f" - {name}")
    
    except ModuleNotFoundError:
        print(f"Module '{module_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <module_name>")
    else:
        # Get the module name from the command line argument
        module_name = sys.argv[1]
        print_module_methods(module_name)

