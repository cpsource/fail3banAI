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
            # Get the signature (arguments and return type)
            signature = inspect.signature(func)
            
            # Print the method name and its signature
            print(f" - {name}{signature}")
            
            # Check if there's a return annotation
            if signature.return_annotation is not inspect.Signature.empty:
                print(f"    -> Returns: {signature.return_annotation}")
            else:
                print("    -> Returns: Not annotated")
    
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

