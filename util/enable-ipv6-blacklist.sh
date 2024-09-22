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

# Construct the path to Manage6.py
MANAGE6_PY="$FAIL3BAN_PROJECT_ROOT/lib/ManageIpset6.py"

# Check if the Manage6.py file exists
if [[ ! -f "$MANAGE6_PY" ]]; then
    echo "The script $MANAGE6_PY does not exist." >&2
    exit 1
fi

# Run the Manage6.py stop command
echo "Stopping IPv6 blacklist service..."
sudo -E python3 "$MANAGE6_PY" stop
if [[ $? -ne 0 ]]; then
    echo "Failed to stop the IPv6 blacklist service." >&2
    exit 1
fi

# Run the Manage6.py start command
echo "Starting IPv6 blacklist service..."
sudo -E python3 "$MANAGE6_PY" start
if [[ $? -ne 0 ]]; then
    echo "Failed to start the IPv6 blacklist service." >&2
    exit 1
fi

echo "IPv6 blacklist service has been successfully restarted."

