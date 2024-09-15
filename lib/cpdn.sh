#!/bin/bash

# Check if argument is given
if [ -z "$1" ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

src="./$1"
dest="/mnt/c/Users/pagec/Downloads/$1"

# Check if source file exists
if [ ! -f "$src" ]; then
    echo "Source file '$src' does not exist."
    exit 1
fi

# Check if target file exists
if [ -f "$dest" ]; then
    read -p "'$dest' already exists. Overwrite? [Yn]: " choice
    case "$choice" in
        [nN]*) echo "File not overwritten."; exit;;
    esac
fi

# Copy file
cp "$src" "$dest"
echo "File copied from '$src' to '$dest'."

