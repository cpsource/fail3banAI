class CheckIpsum:
    def check(self, str1, str2):
        # Dictionaries to hold the IP addresses from str1 and str2
        dict_a = {}
        dict_b = {}

        # Read file str1 and store IPs in dict_a
        with open(str1, 'r') as file1:
            for line in file1:
                ip = line.strip()
                if ip:
                    dict_a[ip] = True  # Use True as a placeholder value

        # Read file str2 and store IPs in dict_b
        with open(str2, 'r') as file2:
            for line in file2:
                ip = line.strip()
                if ip:
                    dict_b[ip] = True  # Use True as a placeholder value

        # Result dictionary to store comparison results
        res_dict = {}

        # First walk: Check if each IP in A is in B (populate first result of the tuple)
        for ip in dict_a:
            if ip in dict_b:
                res_dict[ip] = (True, None)  # Found in both; mark first as True, second as pending
            else:
                res_dict[ip] = (False, None)  # Found only in A; mark first as 'F', second as pending

        # Second walk: Check if each IP in B is in A (populate second result of the tuple)
        for ip in dict_b:
            if ip in res_dict:
                # If already checked in the first walk, update the second part of the tuple
                res_dict[ip] = (res_dict[ip][0], True)
            else:
                # If not in A, mark first as None and second as 'F'
                res_dict[ip] = (None, False)

        # Print out the result dictionary, one line per IP address
        #for ip, result in res_dict.items():
        #    print(f"{ip}: {result}")

        # Print out only the differences
        print("*** Add Set")
        for ip, result in res_dict.items():
            if result[0] is True and result[1] is True:
                continue
            print(f"{ip}: {result}")

        # Print out ones that must be removed from ipset
        print("*** Removal Set")
        for ip, result in res_dict.items():
            if result[0] is None and result[1] is False:
                print(f"{ip}: {result}")
            
# Example usage
# Assuming 'file1.txt' and 'file2.txt' contain lists of IP addresses
check_ipsum = CheckIpsum()
check_ipsum.check('ipsum.3.txt', 'ipsum.4.txt')

