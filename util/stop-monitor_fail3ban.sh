#!/bin/bash

# Path to the PID file
PID_FILE="/tmp/monitor_fail3ban.pid"

# Check if the PID file exists
if [ -f "$PID_FILE" ]; then
    # Read the PID from the file
    PID=$(cat "$PID_FILE")
    
    # Check if the PID is a valid number
    if [[ "$PID" =~ ^[0-9]+$ ]]; then
        # Send SIGTERM to the process
        echo "Stopping monitor_fail3ban process with PID: $PID"
        sudo kill -SIGTERM "$PID"
        
        # Check if the kill command succeeded
        if [ $? -eq 0 ]; then
            echo "Process $PID terminated successfully."
        else
            echo "Failed to terminate process $PID. You may need to check manually."
        fi
    else
        echo "Invalid PID found in $PID_FILE."
    fi
else
    echo "PID file $PID_FILE does not exist. Is monitor_fail3ban running?"
fi

