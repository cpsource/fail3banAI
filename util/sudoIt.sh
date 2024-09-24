#!/bin/bash

# Check if exactly one argument is provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <python_script>"
  exit 1
fi

# Get the argument (the Python script to run)
SCRIPT=$1

# Run the Python script with sudo -E
sudo -E $(which python3) "$SCRIPT"

