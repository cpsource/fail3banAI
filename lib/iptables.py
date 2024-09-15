import subprocess
import sys
import time

class iptables:
    def __init__(self, debug=False):
        self.debug = debug

    def debug_print(self, message):
        """Helper method to print debug messages only if debug is True."""
        if self.debug:
            print(f"Debug: {message}")

    def run_command(self, command):
        """Helper function to run subprocess commands with error handling."""
        try:
            self.debug_print(f"Executing command: {' '.join(command)}")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr}")
            return None

    def is_in_chain(self, ip_address):
        """Check if the IP address is already in iptables."""
        try:
            # Check if the IP exists in the INPUT chain or any fail3ban chain
            result = self.run_command(['sudo', 'iptables', '-L', 'INPUT', '-n'])
            if ip_address in result:
                self.debug_print(f"IP {ip_address} is already in the INPUT chain.")
                return True
            
            # Check custom fail3ban chains
            custom_chains = self.run_command(['sudo', 'iptables', '-L', '-n'])
            if ip_address in custom_chains:
                self.debug_print(f"IP {ip_address} is in a custom fail3ban chain.")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error checking if IP {ip_address} is in chain: {e}")
        return False

    def remove_chain(self, chain_name, rule_num):
        """Remove all rules from a chain, unlink it from INPUT, and then delete the chain."""
        unlink_command = ['sudo', 'iptables', '-D', 'INPUT', rule_num]
        self.debug_print(f"Unlinking chain {chain_name} from INPUT. Executing command: {' '.join(unlink_command)}")
        self.run_command(unlink_command)  # Unlink the chain from INPUT

        flush_command = ['sudo', 'iptables', '-F', chain_name]
        self.debug_print(f"Removing all rules from chain {chain_name}. Executing command: {' '.join(flush_command)}")
        self.run_command(flush_command)  # Flush all rules in the chain

        delete_command = ['sudo', 'iptables', '-X', chain_name]
        self.debug_print(f"Deleting chain {chain_name}. Executing command: {' '.join(delete_command)}")
        self.run_command(delete_command)

    def remove_rule(self, chain, rule_num):
        """Remove a specific rule from a chain by its rule number."""
        delete_rule_command = ['sudo', 'iptables', '-D', chain, str(rule_num)]
        self.debug_print(f"Removing rule number {rule_num} from chain {chain}. Executing command: {' '.join(delete_rule_command)}")
        self.run_command(delete_rule_command)

    def add_chain_to_INPUT(self, ip_address, jail_name):
        """Add IP to a custom chain with the jail name, and create the chain if it doesn't exist."""
        chain_name = f"f3b-{jail_name}"

        try:
            # Ensure the chain exists
            result = self.run_command(['sudo', 'iptables', '-L', chain_name, '-n'])
            if not result or "No chain" in result:
                self.debug_print(f"Chain {chain_name} does not exist. Creating it.")
                self.run_command(['sudo', 'iptables', '-N', chain_name])

            # Link chain to INPUT
            result = self.run_command(['sudo', 'iptables', '-L', 'INPUT', '-n'])
            if chain_name not in result:
                self.debug_print(f"Linking chain {chain_name} to INPUT.")
                self.run_command(['sudo', 'iptables', '-A', 'INPUT', '-j', chain_name, '-m', 'comment', '--comment', 'fail3ban'])

            # Add the reject rule to the custom chain
            if ip_address not in result:
                self.debug_print(f"Adding ban for IP {ip_address} to chain {chain_name}.")
                self.run_command(['sudo', 'iptables', '-A', chain_name, '-s', ip_address, '-j', 'REJECT', '--reject-with', 'icmp-port-unreachable', '-m', 'comment', '--comment', 'fail3ban'])
            else:
                self.debug_print(f"IP {ip_address} already exists in chain {chain_name}.")

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
                        self.debug_print(f"Found chain {chain_name} with comment 'fail3ban'.")
                        chains_to_remove.append((chain_name, rule_num))
                    else:
                        self.debug_print(f"Found rule with comment 'fail3ban', rule number {rule_num}.")
                        rules_to_remove.append(rule_num)

            for chain_name, rule_num in reversed(chains_to_remove):
                self.debug_print(f"Removing chain {chain_name}.")
                self.remove_chain(chain_name, rule_num)

            for rule_num in reversed(rules_to_remove):
                self.remove_rule('INPUT', rule_num)

# Command-line interface
if __name__ == "__main__":
    ipt = Iptables(debug=True)

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

