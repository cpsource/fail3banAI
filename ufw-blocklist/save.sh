#!/bin/bash

set -e

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "You must run this script as root."
    exit 1
fi

export ipsetname=ufw-blocklist-ipsum
export IPSET_EXE=$(which ipset)

# Check if ipset exists and is executable
if [ ! -x "$IPSET_EXE" ]; then
    echo "$IPSET_EXE is not executable"
    exit 1
fi

# save to stdout
$IPSET_EXE save "$ipsetname"
