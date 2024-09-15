class ScanClass:
    def __init__(self):
        # Initialize an empty list to hold method entry points
        self.methods = []

    # Method to add entry points to the list
    def add_method(self, method):
        self.methods.append(method)

    # Method to walk the list and execute each method in turn
    def execute_methods(self, log_entry):
        for method in self.methods:
            result = method(log_entry)
            if result:
                print(result)

# Example functions to be added to the class

def scan_invalid_user_log(log_entry):
    # This is a simplified placeholder for the invalid user log scanner
    if "Invalid user" in log_entry:
        return "Invalid user found"
    return False

def scan_journalctl_log(log_entry):
    # This is a simplified placeholder for the journalctl log scanner
    if "Connection closed" in log_entry:
        return "Connection closed found"
    return False

# Example usage
if __name__ == "__main__":
    # Create an instance of ScanClass
    scanner = ScanClass()

    # Add both scanning methods to the class
    scanner.add_method(scan_invalid_user_log)
    scanner.add_method(scan_journalctl_log)

    # Example log entries
    log_entries = [
        "Sep 11 10:25:42 ip-172-26-10-222 sshd[134387]: Invalid user postgres from 116.132.42.170 port 33348",
        "Sep 11 10:09:42 ip-172-26-10-222 sshd[133885]: Connection closed by 152.32.252.94 port 34538 [preauth]"
    ]

    # Walk through each log entry and execute the methods
    for log in log_entries:
        scanner.execute_methods(log)

