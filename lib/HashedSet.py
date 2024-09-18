import os

class HashedSet:
    def __init__(self, hashed_set_file='hashed_set.py'):
        self.hashed_set_file = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/util/" + hashed_set_file
        self.hashed_set = self.load_hashed_set()

    def load_hashed_set(self):
        try:
            # Dynamically import the hashed_set from the given file
            hashed_set_module = {}
            with open(self.hashed_set_file, 'r') as file:
                exec(file.read(), hashed_set_module)
            return hashed_set_module['hashed_set']
        except FileNotFoundError:
            print(f"File {self.hashed_set_file} not found.")
            return set()
        except KeyError:
            print("Error loading hashed_set from file.")
            return set()

    def is_ip_in_set(self, ip_address):
        """Check if an IP address is in the hashed set."""
        return ip_address in self.hashed_set


# Example usage (this part can be used in the 'check_ip.py' file or main code):
if __name__ == "__main__":
    import sys

    # Create an instance of HashedSet
    hashed_set_instance = HashedSet()

    # Check if an IP address was provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 check_ip.py <ip_address>")
        sys.exit(1)

    # Get the IP address from the first command-line argument
    ip_address = sys.argv[1]

    # Check if the IP address is in the hashed set
    if hashed_set_instance.is_ip_in_set(ip_address):
        print(f"{ip_address} is in the hashed set.")
    else:
        print(f"{ip_address} is NOT in the hashed set.")

    # Create another instance of HashedSet
    hashed_set_instance = None
    hashed_set_instance = HashedSet()

    # Get the IP address from the first command-line argument
    ip_address = sys.argv[1]

    # Check if the IP address is in the hashed set
    if hashed_set_instance.is_ip_in_set(ip_address):
        print(f"{ip_address} is in the reloaded hashed set.")
    else:
        print(f"{ip_address} is NOT in the reloaded hashed set.")
    
