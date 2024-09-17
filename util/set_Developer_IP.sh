#!/bin/bash

# Define the path to the Python script
script_path="$HOME/fail3banAI/util/who-am-i.py"

# Check if the file exists and is readable
if [ ! -x "$script_path" ]; then
    echo "Script not executable: $script_path"
    exit 1
fi

# Check if the file is executable
if [ -x "$script_path" ]; then
    echo "Script is executable, running it..."
    # Run the script and capture the output
    script_output=$("$script_path")
else
    echo "Script is not executable: $script_path. Attempting to run with Python..."

    # Try running the script with Python directly
    if command -v python3 &> /dev/null; then
        script_output=$(python3 "$script_path")
    elif command -v python &> /dev/null; then
        script_output=$(python "$script_path")
    else
        echo "Python is not installed or not found in the PATH."
        exit 1
    fi
fi

# Extract the IP address from the output (assuming it follows the format 'Your public IP address is: <ip>')
ip_address=$(echo "$script_output" | grep -oP '\d+\.\d+\.\d+\.\d+')

if [ -n "$ip_address" ]; then
    # Export the IP address as Developer_IP
    export Developer_IP="$ip_address"
    echo "Developer_IP has been set to $Developer_IP"
    
    # If Developer_IP is set, perform SSH with SendEnv
    echo "Initiating SSH with Developer_IP..."
    ssh -o SendEnv=Developer_IP ubuntu@natdem.org '~/fail3banAI/util/open-developer-port.sh'
else
    echo "No IP address found in the script output."
fi

