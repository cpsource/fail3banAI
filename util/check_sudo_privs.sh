#!/bin/bash

# Check if the script is run as root, since it requires sudo privileges to check other users
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root." 
   exit 1
fi

# Read the /etc/passwd file and extract the first column (usernames)
while IFS=: read -r username _; do
    echo "Checking sudo privileges for user: $username"
    
    # Run sudo -l -U for each user to check their sudo privileges
    sudo -l -U "$username"
    
    echo "--------------------------------------"
done < /etc/passwd

