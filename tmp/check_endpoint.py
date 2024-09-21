#gives back  isWhiteListed: true, false, null
import os
import requests
import json
import sys
from dotenv import load_dotenv

#from dotenv import dotenv_values
#from dotenv load load_dotenv

class CheckEndpoint:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = 'https://api.abuseipdb.com/api/v2/check'

    def check_ip(self, ip_address, max_age_in_days=90):
        """Check the details of the provided IP address using AbuseIPDB API"""
        querystring = {
            'ipAddress': ip_address,
            'maxAgeInDays': str(max_age_in_days)
        }

        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }

        response = requests.request(method='GET', url=self.url, headers=headers, params=querystring)
        
        # Check if the response was successful
        if response.status_code == 200:
            # Return the parsed JSON response
            return json.loads(response.text)
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

def main(): 
    # Get the FAIL3BAN_PROJECT_ROOT environment variable
    home = os.getenv('HOME')
    project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
    # load dotenv
    try:
        # Attempt to load dotenv file using the environment variable
        file = f"{home}/.env"
        dotenv_config = load_dotenv(file)
        print("dotenv file loaded successfully.")
    except Exception as e:
        # Handle any exceptions that may occur
        print(f"An error occurred while loading dotenv: {e}")

    # Get API key from environment variable
    api_key = os.getenv('ABUSEIPDB_KEY')
    
    if not api_key:
        print("Error: ABUSEIPDB_KEY environment variable is not set.")
        sys.exit(1)

    # Ensure an IP address is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python check_endpoint.py <ip-address>")
        sys.exit(1)

    ip_address = sys.argv[1]

    # Create an instance of CheckEndpoint with the provided API key
    checker = CheckEndpoint(api_key)

    try:
        # Perform the IP address check
        result = checker.check_ip(ip_address)
        
        # Print formatted output
        print(json.dumps(result, sort_keys=True, indent=4))
    
    except Exception as e:
        print(f"Error: {e}")

# Run main function if this script is executed directly
if __name__ == "__main__":
    main()

