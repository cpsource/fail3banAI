import os
import subprocess
#import sys

class IpSet6:
    def __init__(self, ipsetname='ufw-blocklist6-ipsum'):
        # Set self.after.init based on the environment variable FAIL3BAN_PROJECT_ROOT
        project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
        if not project_root:
            raise EnvironmentError("Environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
        self.ipset = "/usr/sbin/ipset"
        self.after_init = os.path.join(project_root, 'ufw-blocklist', 'after.init')
        self.ipsetname = ipsetname  # Set ipsetname with the optional argument

        # Check if after.init exists and is executable
        if not os.path.exists(self.after_init):
            raise FileNotFoundError(f"Error: {self.after_init} does not exist.")
        
        if not os.access(self.after_init, os.X_OK):
            raise PermissionError(f"Error: {self.after_init} is not executable.")

        # Try to run 'ipset -h' and handle errors if 'ipset' is not found
        try:
            result = subprocess.run([self.ipset, '-h'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("IpSet6 initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: ipset command failed with error code: {e.returncode}")
        except FileNotFoundError:
            print("Error: Command 'ipset' not found. You can install it with 'sudo apt install ipset'.")

    def start(self):
        """Starts the ipset using after.init start"""
        try:
            subprocess.run([self.after_init, 'start'], check=True)
            print(f"{self.after_init} started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to start {self.after_init}. Exit code: {e.returncode}")
        except Exception as e:
            print(f"Unexpected error occurred while starting {self.after_init}: {e}")

    def stop(self):
        """Stops the ipset using after.init stop"""
        try:
            subprocess.run([self.after_init, 'stop'], check=True)
            print(f"{self.after_init} stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to stop {self.after_init}. Exit code: {e.returncode}")
        except Exception as e:
            print(f"Unexpected error occurred while stopping {self.after_init}: {e}")

    def add(self, ip_address):
        """Adds an IPv6 address to the ipset"""
        #print(f"cmd: ipset add {self.ipsetname} {ip_address}")
        try:
            # Run the ipset add command
            subprocess.run([self.ipset, 'add', self.ipsetname, ip_address], check=True)
            #print(f"IPv6 address {ip_address} added to ipset {self.ipsetname} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to add IPv6 address {ip_address} to ipset {self.ipsetname}. Exit code: {e.returncode}")
        except Exception as e:
            print(f"Unexpected error occurred while adding IPv6 address {ip_address}: {e}")

    def delete(self, ip_address):
        """Deletes an IPv6 address from the ipset"""
        try:
            # Run the ipset del command
            subprocess.run([self.ipset, 'del', self.ipsetname, ip_address], check=True)
            #print(f"IPv6 address {ip_address} deleted from ipset {self.ipsetname} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to delete IPv6 address {ip_address} from ipset {self.ipsetname}. Exit code: {e.returncode}")
        except Exception as e:
            print(f"Unexpected error occurred while deleting IPv6 address {ip_address}: {e}")

    def test(self, ip_address):
        """Tests if an IPv6 address is present in the ipset"""
        try:
            # Run the ipset test command
            subprocess.run([self.ipset, 'test', self.ipsetname, ip_address], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #print(f"IPv6 address {ip_address} is present in ipset {self.ipsetname}.")
            return True
        except subprocess.CalledProcessError:
            #print(f"IPv6 address {ip_address} is not present in ipset {self.ipsetname}.")
            return False
        except Exception as e:
            print(f"Unexpected error occurred while testing IPv6 address {ip_address}: {e}")
            return False

# Example of using the IpSet6 class
if __name__ == "__main__":
    try:
        # Initialize IpSet6 with a custom ipsetname (optional)
        ipset_manager = IpSet6()
        print(f"after_init set to: {ipset_manager.after_init}")
        print(f"ipsetname set to: {ipset_manager.ipsetname}")
        print(f"ipsetname ipset to: {ipset_manager.ipset}")

        # Start the ipset
        ipset_manager.start()

        # Add an IPv6 address to the ipset
        ipset_manager.add("2001:0db8::ff00:42:8329")

        # Test if an IPv6 address is present in the ipset
        if ipset_manager.test("2001:0db8::ff00:42:8329"):
            print("Test passed: IPv6 is present.")
        else:
            print("Test failed: IPv6 is not present.")

        # Delete the IPv6 address from the ipset
        ipset_manager.delete("2001:0db8::ff00:42:8329")

        # Stop the ipset
        ipset_manager.stop()

    except Exception as e:
        print(f"Initialization failed: {e}")

