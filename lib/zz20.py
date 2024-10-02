import re

def sanitize_filename(input_str):
    # Define valid Ubuntu file name characters (alphanumeric, dot, dash, underscore)
    valid_chars = re.compile(r'[a-zA-Z0-9._-]')
    
    # Create a sanitized filename by replacing invalid characters with 'x'
    sanitized = ''.join(char if valid_chars.match(char) else '_' for char in input_str)
    
    # Return the sanitized string truncated to 16 characters
    return sanitized[:16]

# Example usage:
test_str = "Hello! This:File@Name#"
result = sanitize_filename(test_str)
print(result)
