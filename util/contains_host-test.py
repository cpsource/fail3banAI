def contains_host(string):
    """Returns True if the string contains '<HOST>', else False."""
    return '<HOST>' in string

# Example usage:
test_string_1 = "This is a test with <HOST> in it."
test_string_2 = "This string does not contain the special word."

print(contains_host(test_string_1))  # True
print(contains_host(test_string_2))  # False
