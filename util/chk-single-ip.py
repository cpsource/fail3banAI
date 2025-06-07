import os
import sys
import requests
import json
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Check IP address against AbuseIPDB.")
parser.add_argument('ip_address', type=str, help='IP address to check')
args = parser.parse_args()

# Defining the API endpoint
url = 'https://api.abuseipdb.com/api/v2/check'

# Set up headers for the request
headers = {
    'Accept': 'application/json',
    'Key': os.getenv('ABUSEIPDB_KEY')
}

# The IP address to check comes from the command line
ip_address = args.ip_address

querystring = {
    'ipAddress': f'{ip_address}',
    'maxAgeInDays': '90'
}

# Send the request to AbuseIPDB
response = requests.request(method='GET', url=url, headers=headers, params=querystring)
# type(response) = <class 'requests.models.Response'>
print(f"Ip Address: {ip_address}")

# Formatted output
decodedResponse = json.loads(response.text)
print (json.dumps(decodedResponse, sort_keys=True, indent=4))

# Decode and print the response
#decodedResponse = json.loads(response.text)
#decodedResponse = json.dumps(decodedResponse, sort_keys=True, indent=4)

# Check if the response is successful
if response.status_code == 200:
    # Parse the response into a Python dictionary
    decodedResponse = response.json()  # Correct parsing of JSON response

    # Extract relevant fields into a dictionary
    ip_info = {
        "ipAddress": decodedResponse["data"].get("ipAddress"),
        "abuseConfidenceScore": decodedResponse["data"].get("abuseConfidenceScore"),
        "countryCode": decodedResponse["data"].get("countryCode"),
        "domain": decodedResponse["data"].get("domain"),
        "hostnames": decodedResponse["data"].get("hostnames"),
        "ipVersion": decodedResponse["data"].get("ipVersion"),
        "isPublic": decodedResponse["data"].get("isPublic"),
        "isTor": decodedResponse["data"].get("isTor"),
        "isWhitelisted": decodedResponse["data"].get("isWhitelisted"),
        "isp": decodedResponse["data"].get("isp"),
        "lastReportedAt": decodedResponse["data"].get("lastReportedAt"),
        "numDistinctUsers": decodedResponse["data"].get("numDistinctUsers"),
        "totalReports": decodedResponse["data"].get("totalReports"),
        "usageType": decodedResponse["data"].get("usageType")
    }

    # Print the extracted fields
    # Loop through the dictionary and print each key-value pair
    for key, value in ip_info.items():
        print(f"{key}: {value}")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    
#print(f"ip info = {ip_info}")

#
# schema to store all this
#
# CREATE TABLE ip_responses (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     ip_address VARCHAR(45) NOT NULL UNIQUE,  -- Unique IP address
#     response TEXT NOT NULL,                  -- Response data (JSON or plain text)
#     ref_cnt INT DEFAULT 1,                   -- Reference count, initialized to 1
#     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
# );

# # for speed, do this too
# CREATE INDEX idx_ip_address ON ip_responses (ip_address);
#
# see update_ip_info.py for example usage
