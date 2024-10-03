# ban_bad_access.py
import Parselet_GETenv
import AbuseIPDB

import json
from datetime import datetime

import subprocess

def add_to_ipset(ip_address):
    try:
        # Run the ipset command to add the IP address to the ufw-blocklist-ipsum set
        subprocess.run(['ipset', 'add', 'ufw-blocklist-ipsum', ip_address], check=True)
        print(f"Successfully added {ip_address} to ufw-blocklist-ipsum.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding {ip_address} to ufw-blocklist-ipsum: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

abuseipdb = AbuseIPDB.AbuseIPDB()
parselet = Parselet_GETenv.Parselet_GETenv()

def convert_to_zulu_time(timestamp):
    # Convert timestamp in the format "21/Sep/2024:23:55:55 +0000" to ISO Zulu format
    try:
        dt = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")
        return dt.isoformat()
    except ValueError as e:
        print(f"Error converting timestamp: {e}")
        return None

def process_bad_access_log(file_path):
    count = 0
    try:
        with open(file_path, 'r') as file:
            for line in file:
                count += 1
                compressed_line = parselet.compress_line(line.strip())
                log_data = json.loads(compressed_line)
                
                # Skip entries with "No match found" error
                if "error" in log_data and log_data["error"] == "No match found":
                    continue
                
                # Extract necessary fields
                ip_address = log_data["extracted_info"]["ip_address"]
                timestamp = log_data["extracted_info"]["timestamp"]
                requested_file = log_data["extracted_info"]["requested_file"]
                
                # Convert timestamp to ISO Zulu time
                zulu_time = convert_to_zulu_time(timestamp)
                
                # Build the comment
                comment = f"apache2 invalid GET {requested_file}"
                
                # Display the output
                print(f"IP Address: {ip_address}")
                print(f"Timestamp (Zulu): {zulu_time}")
                print(f"Comment: {comment}")
                print(f"count: {count}")
                
                print("-" * 40)

                if False:
                    # report
                    abuseipdb.report_endpoint(ip_address, "10,18", comment, zulu_time)

                # add to ipset
                add_to_ipset(ip_address)
                
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    log_file_path = '../control/bad-access-log-entries.txt'
    process_bad_access_log(log_file_path)

