#!/home/ubuntu/openai/bin/python3

import os
import re
import sys

def match_in_file(filepath, patterns):
    """Check if all patterns match at least once in the file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            # Check if all patterns match in the content
            return all(re.search(pattern, content) for pattern in patterns)
    except (FileNotFoundError, UnicodeDecodeError):
        # Skip files that can't be opened or decoded
        return False

def walk_tree_and_find(directory, patterns):
    """Walk the directory tree and find .py files that match all patterns."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                if match_in_file(filepath, patterns):
                    print(filepath)

def main():
    # Ensure at least 1 argument is passed
    if len(sys.argv) < 2 or len(sys.argv) > 11:
        print("Usage: finder.py <pattern1> [<pattern2> ... <pattern10>]")
        sys.exit(1)

    # Get the regex patterns from command-line arguments
    patterns = sys.argv[1:]

    start_at = os.getenv("FAIL3BAN_PROJECT_ROOT")
    # Start walking the directory tree from the current directory
    #walk_tree_and_find(os.getcwd(), patterns)
    walk_tree_and_find(start_at, patterns)

if __name__ == "__main__":
    main()

