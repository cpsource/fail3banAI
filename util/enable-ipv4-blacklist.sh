#!/bin/bash

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root." >&2
   exit 1
fi

# Check if the environment variable FAIL3BAN_PROJECT_ROOT is defined
if [[ -z "$FAIL3BAN_PROJECT_ROOT" ]]; then
    echo "The environment variable FAIL3BAN_PROJECT_ROOT is not set." >&2
    exit 1
fi

# Construct the path to Manage4.py
MANAGE4_PY="$FAIL3BAN_PROJECT_ROOT/lib/ManageIpset4.py"

# Check if the Manage4.py file exists
if [[ ! -f "$MANAGE4_PY" ]]; then
    echo "The script $MANAGE4_PY does not exist." >&2
    exit 1
fi

# Run the Manage4.py stop command
echo "Stopping IPv4 blacklist service..."
sudo -E python3 "$MANAGE4_PY" stop
if [[ $? -ne 0 ]]; then
    echo "Failed to stop the IPv4 blacklist service." >&2
    exit 1
fi

# Run the Manage4.py start command
echo "Starting IPv4 blacklist service..."
sudo -E python3 "$MANAGE4_PY" start
if [[ $? -ne 0 ]]; then
    echo "Failed to start the IPv4 blacklist service." >&2
    exit 1
fi

echo "IPv4 blacklist service has been successfully restarted."

