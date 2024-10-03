#!/bin/bash

# Check if the user provided an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <file_extension>"
    exit 1
fi

# Store the file extension argument (e.g., .txt)
file_extension="$1"

# Loop through the files with the specified extension
for file in *"$file_extension"; do
    if [ -f "$file" ]; then  # Check if it's a file (not a directory or other type)
        echo "Processing file: $file"
        # Perform your operations on each file here
        # For example, you can print the contents: cat "$file"
	gunzip -c $file
    fi
done

