import requests
import inspect

class Whitelist:
    configData = None
    def __init__(self, configData):
        # Initialize an empty array to store whitelisted IPs
        self.whitelist = []
        self.configData = configData
        
    def whitelist_init(self):
        # Open the whitelist.ctl file
        try:
            with open('whitelist.ctl', 'r') as file:
                for line in file:
                    # Remove any comment after # and strip whitespace
                    clean_line = line.split('#')[0].strip()
                    
                    # If the line contains an IP address, add it to the whitelist
                    if clean_line:
                        self.whitelist.append(clean_line)
        except FileNotFoundError:
            print("Error: whitelist.ctl file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        # get how we are seen from the outside world
        tmp_var = self.get_my_public_ip()
        # add to whitelist if not there
        if not self.is_whitelisted(tmp_var):
            self.whitelist.append(tmp_var)

        # test of scope
        debug = self.configData.get('debug')
        if debug :
            print(f"Debug: at whitelist_init, debug = {debug}")

    def get_whitelist(self):
        # Return the list of whitelisted IPs
        return self.whitelist

    def is_whitelisted(self, ip_address):
        # Return True if the ip_address is in the whitelist, False otherwise
        return ip_address in self.whitelist

    def get_my_public_ip(self):
        if not self._is_called_within_class():
            print(f"Warning: get_my_public_ip called from outside the class")
            
        try:
            # Fetch the public IP using a public API
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()  # Raise an error for bad status codes
            ip_info = response.json()
            
            return ip_info['ip']
        except requests.RequestException as e:
            return None # f"Error fetching IP address: {e}"

    # a utility class
    def _is_called_within_class(self):
        """Check the call stack to see if the caller is from within the class."""
        # Get the current call stack
        stack = inspect.stack()
        # The frame at index 2 should be the caller
        caller_frame = stack[2]
        # Get the class (if any) of the caller
        caller_class = caller_frame.frame.f_locals.get('self', None)
        # Return True if the caller is from the same instance
        return isinstance(caller_class, self.__class__)
    
# Example usage
if __name__ == "__main__":
    wl = Whitelist()
    wl.whitelist_init()
    print("Whitelisted IPs:", wl.get_whitelist())

    # Example of checking if an IP is whitelisted
    test_ip = '192.168.1.1'
    if wl.is_whitelisted(test_ip):
        print(f"{test_ip} is whitelisted.")
    else:
        print(f"{test_ip} is not whitelisted.")

