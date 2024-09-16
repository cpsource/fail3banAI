# iptables.py

# manage everything iptables

# Extracted constants for log file name and format
LOG_FILE_NAME = "fail3ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

import subprocess
import sys
import os
import time
# Configure logging
import logging

#import sys
#sys.path.append('/home/pagec/fail3ban/lib')

from whitelist import WhiteList

class Iptables:
    def __init__(self, logger_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(logger_id)

    def is_running_as_root(self):
        # Check if the current user is root (UID 0)
        return os.geteuid() == 0
    
    def run_command(self, command):
        """Helper function to run subprocess commands with error handling."""
        try:
            self.logger.debug(f"Executing command: {' '.join(command)}")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"An error occurred: {e.stderr}")
            return None

    def is_ip_in_input_chain(self, ip_address, extra="test"):
        try:
            # Run the iptables command to list the INPUT chain
            result = subprocess.run(["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers", "-x"], 
                                    capture_output=True, text=True, check=True)
            
            # Check each line in the result for the IP address and the comment "fail3ban"
            for line in result.stdout.splitlines():
                if ip_address in line and "fail3ban" in line and extra in line:
                    return True
            return False
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error occurred while checking iptables: {e}")
            return False
        
    def add_allow_ip_to_front_of_input_chain(self, ip_address, extra="test"):
        if not self.is_ip_in_input_chain(ip_address):
            try:
                # Construct the iptables command to insert the IP address at the first position in INPUT chain
                command = ["iptables", "-I", "INPUT", "1", "-s", ip_address, "-j",
                           "ACCEPT", "-m", "comment", "--comment", f"fail3ban {extra}"]
            
                # Execute the command using subprocess
                self.run_command(command)
            
                #subprocess.run(command, check=True)
                self.logger.debug(f"IP address {ip_address} successfully added to the INPUT chain.")
        
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to add IP address {ip_address} to INPUT chain: {e}")
            
    def is_in_chain(self, ip_address):
        """Check if the IP address is already in iptables."""
        try:
            # Check if the IP exists in the INPUT chain or any fail3ban chain
            result = self.run_command(['sudo', 'iptables', '-L', 'INPUT', '-n'])
            if ip_address in result:
                self.logger.debug(f"IP {ip_address} is already in the INPUT chain.")
                return True
            
            # Check custom fail3ban chains
            custom_chains = self.run_command(['sudo', 'iptables', '-L', '-n'])
            if ip_address in custom_chains:
                self.logger.debug(f"IP {ip_address} is in a custom fail3ban chain.")
                return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error checking if IP {ip_address} is in chain: {e}")
        return False

    def remove_chain(self, chain_name, rule_num):
        """Remove all rules from a chain, unlink it from INPUT, and then delete the chain."""
        unlink_command = ['sudo', 'iptables', '-D', 'INPUT', rule_num]
        self.logger.debug(f"Unlinking chain {chain_name} from INPUT. Executing command: {' '.join(unlink_command)}")
        self.run_command(unlink_command)  # Unlink the chain from INPUT

        flush_command = ['sudo', 'iptables', '-F', chain_name]
        self.logger.debug(f"Removing all rules from chain {chain_name}. Executing command: {' '.join(flush_command)}")
        self.run_command(flush_command)  # Flush all rules in the chain

        delete_command = ['sudo', 'iptables', '-X', chain_name]
        self.logger.debug(f"Deleting chain {chain_name}. Executing command: {' '.join(delete_command)}")
        self.run_command(delete_command)

    def remove_rule(self, chain, rule_num):
        """Remove a specific rule from a chain by its rule number."""
        delete_rule_command = ['sudo', 'iptables', '-D', chain, str(rule_num)]
        self.logger.debug(f"Removing rule number {rule_num} from chain {chain}. Executing command: {' '.join(delete_rule_command)}")
        self.run_command(delete_rule_command)

    def add_chain_to_INPUT(self, ip_address, jail_name):
        """Add IP to a custom chain with the jail name, and create the chain if it doesn't exist."""
        chain_name = f"f3b-{jail_name}"

        try:
            # Ensure the chain exists
            result = self.run_command(['sudo', 'iptables', '-L', chain_name, '-n'])
            if not result or "No chain" in result:
                self.logger.debug(f"Chain {chain_name} does not exist. Creating it.")
                self.run_command(['sudo', 'iptables', '-N', chain_name])

            # Link chain to INPUT
            result = self.run_command(['sudo', 'iptables', '-L', 'INPUT', '-n'])
            if chain_name not in result:
                self.logger.debug(f"Linking chain {chain_name} to INPUT.")
                self.run_command(['sudo', 'iptables', '-A', 'INPUT', '-j', chain_name, '-m', 'comment', '--comment', 'fail3ban'])

            # Add the reject rule to the custom chain
            if ip_address not in result:
                self.logger.debug(f"Adding ban for IP {ip_address} to chain {chain_name}.")
                self.run_command(['sudo', 'iptables', '-A', chain_name, '-s', ip_address, '-j', 'REJECT', '--reject-with', 'icmp-port-unreachable', '-m', 'comment', '--comment', 'fail3ban'])
            else:
                self.logger.debug(f"IP {ip_address} already exists in chain {chain_name}.")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while adding IP {ip_address}: {e}")

    def remove_all_fail3ban(self):
        """Walk through INPUT, remove all rules and chains with comment 'fail3ban'."""
        result = self.run_command(['sudo', 'iptables', '-L', 'INPUT', '-n', '--line-numbers', '-v'])
        if result:
            lines = result.splitlines()

            rules_to_remove = []
            chains_to_remove = []

            for line in lines:
                if 'fail3ban' in line:
                    parts = line.split()
                    rule_num = parts[0]

                    chain_match = [part for part in parts if part.startswith('f3b-')]
                    if chain_match:
                        chain_name = chain_match[0]
                        self.logger.debug(f"Found chain {chain_name} with comment 'fail3ban'.")
                        chains_to_remove.append((chain_name, rule_num))
                    else:
                        self.logger.debug(f"Found rule with comment 'fail3ban', rule number {rule_num}.")
                        rules_to_remove.append(rule_num)

            for chain_name, rule_num in reversed(chains_to_remove):
                self.logger.debug(f"Removing chain {chain_name}.")
                self.remove_chain(chain_name, rule_num)

            for rule_num in reversed(rules_to_remove):
                self.remove_rule('INPUT', rule_num)

    def show_input_chain(self):
        try:
            # Run the iptables command to list the INPUT chain
            result = subprocess.run(["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers"], 
                                    capture_output=True, text=True, check=True)
            
            # Print the contents of the INPUT chain
            print(result.stdout)
        
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while retrieving iptables INPUT chain: {e}")

    def remove_ip_from_input_chain(self, ip_address, extra="test"):
        try:
            # Run the iptables command to list the INPUT chain with comments
            result = subprocess.run(["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers", "-x"], 
                                    capture_output=True, text=True, check=True)

            # Iterate through each line of the result
            for line in result.stdout.splitlines():
                # Check if the line contains the IP address and the comment 'fail3ban'
                if ip_address in line and "fail3ban" in line and extra in line:
                    # Extract the rule number (first item in the line)
                    rule_number = line.split()[0]
                    
                    # Construct the iptables command to delete the rule by its number
                    delete_command = ["iptables", "-D", "INPUT", rule_number]
                    
                    # Execute the command to delete the rule
                    self.run_command(delete_command)
                    self.logger.debug(f"IP address {ip_address} with comment 'fail3ban' successfully removed from the INPUT chain.")
                    return True
            
            self.logger.debug(f"IP address {ip_address} with comment 'fail3ban' not found in the INPUT chain.")
            return False
        
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while modifying iptables: {e}")
            return False

    def remove_fail3ban_entries_from_iptables_INPUT(self):
        try:
            # Run the iptables command to list the INPUT chain with comments
            result = subprocess.run(["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers", "-x"], 
                                    capture_output=True, text=True, check=True)
            
            # Iterate through each line of the result in reverse order (to prevent rule number shift)
            for line in reversed(result.stdout.splitlines()):
                # Check if the line contains the comment 'fail3ban'
                if "fail3ban" in line:
                    # Extract the rule number (first item in the line)
                    rule_number = line.split()[0]
                    
                    # Construct the iptables command to delete the rule by its number
                    delete_command = ["iptables", "-D", "INPUT", rule_number]
                    
                    # Execute the command to delete the rule
                    subprocess.run(delete_command, check=True)
                    self.logger.debug(f"Rule with comment 'fail3ban' successfully removed (rule number {rule_number}).")
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error occurred while modifying iptables: {e}")
            
# Extracted function to set up logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE_NAME),
            logging.StreamHandler()
        ]
    )
                
# Command-line interface
if __name__ == "__main__":

    # setup logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)

    # Create our class
    ipt = Iptables()
    # must be root
    if not ipt.is_running_as_root():
        logger.error("lib/iptables.py must run as root")
        sys.exit(1)
        
    # lets add a simple ip address to INPUT
    ip_address = "192.168.98.32" # some stupid address we will never use
    ipt.add_allow_ip_to_front_of_input_chain(ip_address,"test")

    # show it
    ipt.show_input_chain()

    # it must be there
    if ipt.is_ip_in_input_chain(ip_address):
        logger.info(f"ip address {ip_address} is in INPUT chain")
    else:
        logger.error(f"ip address {ip_address} is NOT in INPUT chain")

    # delete it
    ipt.remove_ip_from_input_chain(ip_address,"test")

    # it must not be there
    if ipt.is_ip_in_input_chain(ip_address):
        logger.error(f"ip address {ip_address} is in INPUT chain")
    else:
        logger.info(f"ip address {ip_address} is NOT in INPUT chain")

    # show it
    ipt.show_input_chain()

    #
    # now lets test with whitelist
    #
    wl = WhiteList()
    wl.whitelist_init()
    whitelist = wl.get_whitelist()
    for ip_address in whitelist:
        ipt.add_allow_ip_to_front_of_input_chain(ip_address,"test")
    
    # show it
    ipt.show_input_chain()

    # delete the whitelist
    for ip_address in whitelist:
        # delete it
        ipt.remove_ip_from_input_chain(ip_address,"test")
 
    # show it
    ipt.show_input_chain()
       
    # done for now
    sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: iptables.py <a|d> [ip_address] [jail_name]")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'a':
        if len(sys.argv) != 4:
            print("Usage for adding: iptables.py a <ip_address> <jail_name>")
            sys.exit(1)
        ip_address = sys.argv[2]
        jail_name = sys.argv[3]
        ipt.add_chain_to_INPUT(ip_address, jail_name)
    elif action == 'd':
        ipt.remove_all_fail3ban()
    else:
        print("Invalid action. Use 'a' to add or 'd' to delete.")

