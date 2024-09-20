#!/bin/bash

#set -e

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "You must run this script as root."
    exit 1
fi

# Check if IP address is provided as the first argument
if [ -z "$1" ]; then
    echo "Error: IP address is required as a command line argument."
    exit 1
else
    ip=$1
fi

export ipsetname=ufw-blocklist-ipsum
export IPSET_EXE=$(which ipset)

# Check if ipset exists and is executable
if [ ! -x "$IPSET_EXE" ]; then
    echo "$IPSET_EXE is not executable"
    exit 1
fi

# Test if IP is in the ipset
$IPSET_EXE test "$ipsetname" "$ip"

# Capture and print the exit status of the last command
exit_status=$?
echo "The exit status of the last command is: $exit_status"

#
# Note: sample output after
#
#  sudo ./add.sh 14.103.70.21
#
#ubuntu@ip-172-26-10-222:~/fail3banAI/ufw-blocklist$ sudo ./test.sh 14.103.70.22
#14.103.70.22 is NOT in set ufw-blocklist-ipsum.
#The exit status of the last command is: 1
#
#ubuntu@ip-172-26-10-222:~/fail3banAI/ufw-blocklist$ sudo ./test.sh 14.103.70.21
#Warning: 14.103.70.21 is in set ufw-blocklist-ipsum.
#The exit status of the last command is: 0
#ubuntu@ip-172-26-10-222:~/fail3banAI/ufw-blocklist$
#
