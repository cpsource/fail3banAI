# This program reads 'ipsum.4.txt' and generates 'hashed_set.py' with the set of IPs.

# File paths
input_file = 'ipsum.4.txt'  # Replace this with the actual path of your file
output_file = 'hashed_set.py'

# Create an empty set to store IP addresses
hashed_set = set()

# Open the input file and read it line by line
try:
    with open(input_file, 'r') as f:
        for line in f:
            # Strip the newline and spaces, and add each IP as a string to the set
            ip_address = line.strip()
            if ip_address:  # Skip any empty lines
                hashed_set.add(ip_address)
except FileNotFoundError:
    print(f"File {input_file} not found.")
    exit(1)

# Write the resulting set to the output file in Python format
with open(output_file, 'w') as f_out:
    f_out.write(f"hashed_set = {hashed_set}\n")

print(f"Hashed set written to {output_file}")

