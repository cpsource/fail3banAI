import sys

def unimport_module(module_name):
    if module_name in sys.modules:
        del sys.modules[module_name]
        print(f"Module '{module_name}' has been unimported.")
    else:
        print(f"Module '{module_name}' is not imported.")

# Example usage
import math  # Import math module

# Check if math works
print(math.sqrt(16))  # Output: 4.0

# Unimport the math module
unimport_module('math')

# Now, if you try to access math, it should raise an error
try:
    print(math.sqrt(16))  # This will raise a NameError since math is "unimported"
except NameError as e:
    print(e)

