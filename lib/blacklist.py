class Blacklist:
    def __init__(self):
        # Initialize an empty array to store blacklisted IPs
        self.blacklist = []

    def blacklist_init(self):
        # Open the blacklist.ctl file
        try:
            with open('blacklist.ctl', 'r') as file:
                for line in file:
                    # Remove any comment after # and strip whitespace
                    clean_line = line.split('#')[0].strip()
                    
                    # If the line contains an IP address, add it to the blacklist
                    if clean_line:
                        self.blacklist.append(clean_line)
        except FileNotFoundError:
            print("Error: blacklist.ctl file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_blacklist(self):
        # Return the list of blacklisted IPs
        return self.blacklist

    def is_blacklisted(self, ip_address):
        # Return True if the ip_address is in the blacklist, False otherwise
        return ip_address in self.blacklist

# Example usage
if __name__ == "__main__":
    bl = Blacklist()
    bl.blacklist_init()
    print("Blacklisted IPs:", bl.get_blacklist())

    # Example of checking if an IP is blacklisted
    test_ip = '198.51.100.1'
    if bl.is_blacklisted(test_ip):
        print(f"{test_ip} is blacklisted.")
    else:
        print(f"{test_ip} is not blacklisted.")

