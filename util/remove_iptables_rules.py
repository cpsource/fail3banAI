import subprocess

# File path for the iptables log (the file you uploaded)
file_path = 'z.log'  # Replace with the actual path to your iptables log file

# Function to remove an iptables rule by re-creating the command based on the rule
def remove_iptables_rule(rule_line):
    # Construct the command to remove the rule
    command = ["sudo", "iptables", "-D", "INPUT"] + rule_line.split()
    try:
        print(f"Removing rule: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove rule: {e}")

# Read the iptables log file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Iterate through the log and extract relevant iptables rules for removal
for line in lines:
    # Ignore lines that are headers or not related to actual rules
    if line.startswith("Chain") or line.startswith("target") or line.strip() == "":
        continue
    
    # Extract the rule and remove it
    # You can further refine this logic to match only rules with certain IPs or patterns
    remove_iptables_rule(line.strip())

