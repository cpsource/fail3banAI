#!/bin/bash

PIDFILE="/tmp/monitor-fail3ban.pid"

if [[ -f "$PIDFILE" ]]; then
    # Read the PID from the file
    PID=$(cat "$PIDFILE")
    
    # Check if the process with that PID is running
    if kill -0 "$PID" 2>/dev/null; then
        echo "Process $PID is running, sending SIGHUP..."
        kill -SIGHUP "$PID"
    else
        echo "Process with PID $PID is not running."
    fi
else
    echo "Task is not running. PID file not found."
fi

# get rid of pid file
rm -f $PIDFILE > /dev/null 2>&1

