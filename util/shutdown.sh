#!/bin/bash

# Check if exactly one argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <status|shutdown|cleanup>"
    exit 1
fi

# Pass the argument to the Python script and capture the output
result=$(python3 ../lib/GlobalShutdown.py "$1")

# Report the result
echo "$result"

