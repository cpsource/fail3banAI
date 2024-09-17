import subprocess

# Function to list iptables rules with line numbers
def get_iptables_rules():
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-L", "INPUT", "--line-numbers", "-n"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error listing iptables rules: {e}")
        return []

# Function to remove an iptables rule by its line number
def remove_iptables_rule_by_number(rule_number):
    try:
        command = ["sudo", "iptables", "-D", "INPUT", rule_number]
        print(f"Removing rule number {rule_number}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove rule number {rule_number}: {e}")

# File path for the iptables log (z.log)
file_path = 'z.log'  # Replace with the actual path to your iptables log file

# Read the iptables log file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Get the current iptables rules with line numbers
iptables_rules = get_iptables_rules()

# Iterate through the log and match relevant iptables rules for removal
for line in lines:
    if line.startswith("Chain") or line.startswith("target") or line.strip() == "":
        continue

    # Extract source, destination, and other details from the rule
    rule = line.strip()

    # Try to find this rule in the currently active iptables rules
    for iptables_rule in iptables_rules:
        if rule in iptables_rule:
            # Extract the rule number from the beginning of the matching line
            rule_number = iptables_rule.split()[0]
            # Remove the rule by its number
            remove_iptables_rule_by_number(rule_number)
            break

