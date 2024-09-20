#!/bin/bash

set -e

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "You must run this script as root."
    exit 1

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

# Add IP to the ipset
$IPSET_EXE add "$ipsetname" "$ip"
