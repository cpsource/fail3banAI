import subprocess

# Function to list iptables rules with line numbers for a specific chain
def get_iptables_rules(chain):
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-L", chain, "--line-numbers", "-n"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error listing iptables rules for {chain}: {e}")
        return []

# Function to remove an iptables rule by its line number from a specific chain
def remove_iptables_rule_by_number(chain, rule_number):
    try:
        command = ["sudo", "iptables", "-D", chain, rule_number]
        print(f"Removing rule number {rule_number} from {chain}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove rule number {rule_number} from {chain}: {e}")

# Function to delete a chain if it's empty
def delete_chain(chain):
    try:
        command = ["sudo", "iptables", "-X", chain]
        print(f"Deleting empty chain {chain}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete chain {chain}: {e}")

# Read the iptables log file
file_path = 'z.log'  # Replace with the actual path to your iptables log file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Chains to process
chains = ["INPUT", "FORWARD", "OUTPUT"]

# Process all standard chains (INPUT, FORWARD, OUTPUT)
for chain in chains:
    iptables_rules = get_iptables_rules(chain)
    rules_to_remove = []

    # Iterate through the log and match relevant iptables rules for removal
    for line in lines:
        if line.startswith("Chain") or line.startswith("target") or line.strip() == "":
            continue
        
        rule = line.strip()
        
        # Try to find this rule in the currently active iptables rules
        for iptables_rule in iptables_rules:
            if rule in iptables_rule:
                rule_number = iptables_rule.split()[0]
                rules_to_remove.append(rule_number)
                break

    # Sort the rule numbers in reverse order to avoid index shifting
    rules_to_remove.sort(reverse=True)

    # Remove the rules in reverse order
    for rule_number in rules_to_remove:
        remove_iptables_rule_by_number(chain, rule_number)

# Process any chains starting with ufw-
for line in lines:
    if line.startswith("Chain ufw-"):
        chain_name = line.split()[1]
        iptables_rules = get_iptables_rules(chain_name)
        rules_to_remove = []

        # Match and remove rules for ufw- chains
        for rule in iptables_rules:
            if not rule.strip() or rule.startswith("Chain") or rule.startswith("target"):
                continue
            rule_number = rule.split()[0]
            rules_to_remove.append(rule_number)

        # Sort and remove rules in reverse order
        rules_to_remove.sort(reverse=True)
        for rule_number in rules_to_remove:
            remove_iptables_rule_by_number(chain_name, rule_number)

        # Check if the ufw- chain is now empty, and if so, delete it
        remaining_rules = get_iptables_rules(chain_name)
        if len(remaining_rules) <= 2:  # Only headers and no actual rules
            delete_chain(chain_name)

