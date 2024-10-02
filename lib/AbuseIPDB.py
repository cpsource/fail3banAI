
# all things Abuse_IPDB

import os
import sys
import json
import logging
# and some magic numbers from logging showing their log levels
FLAG_CRITICAL = 50
FLAG_ERROR = 40
FLAG_WARNING = 30
FLAG_INFO = 20
FLAG_DEBUG = 10
FLAG_NOSET = 0
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone

class AbuseIPDB:
    def __init__(self):
        # Get the HOME and FAIL3BAN_PROJECT_ROOT environment variables
        self.home = os.getenv('HOME')
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')

        # Create a named logger consistent with the log file name
        self.logger = logging.getLogger("fail3ban")

        # Check that project_root exists
        if self.project_root:
            self.logger.info(f"Project root is set to: {self.project_root}")
        else:
            self.logger.error("FAIL3BAN_PROJECT_ROOT is not set.")
            sys.exit(1)
        
        # Load dotenv
        try:
            # Attempt to load the .env file from the user's home directory
            dotenv_file = f"{self.home}/.env"
            load_dotenv(dotenv_file)
            self.logger.info("dotenv file loaded successfully.")
        except Exception as e:
            # Log any exceptions that may occur
            self.logger.error(f"An error occurred while loading dotenv: {e}")
            sys.exit(1)
            
        # Get API key from environment variable
        self.api_key = os.getenv('ABUSEIPDB_KEY')

        if not self.api_key:
            self.logger.error("Error: ABUSEIPDB_KEY environment variable is not set.")
            sys.exit(1)

    def check_endpoint(self, ip_address):
        """Check an IP address with AbuseIPDB and return the abuseConfidenceScore"""
        url = 'https://api.abuseipdb.com/api/v2/check'
        
        querystring = {
            'ipAddress': ip_address,
            'maxAgeInDays': '90'
        }

        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                decoded_response = json.loads(response.text)

                print(json.dumps(decoded_response, sort_keys=True, indent=4))

                # Extract isWhitelisted
                is_whitelisted = decoded_response.get('data', {}).get('isWhitelisted')
                    
                # Extract and return the abuseConfidenceScore
                abuse_confidence_score = decoded_response.get('data', {}).get('abuseConfidenceScore')
                return is_whitelisted, abuse_confidence_score
            else:
                self.logger.error(f"Failed to fetch data for IP {ip_address}: {response.status_code}")
                return None, None
        except Exception as e:
            self.logger.error(f"An error occurred while checking IP {ip_address}: {e}")
            return None, None

    def blacklist_endpoint(self, ip_version="4", confidence_minimum=100):
        """Retrieve a blacklist of IP addresses with a minimum confidence score"""
        url = 'https://api.abuseipdb.com/api/v2/blacklist'

        querystring = {
            'confidenceMinimum': str(confidence_minimum),
            'ipVersion': f"{ip_version}"
        }

        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                decoded_response = json.loads(response.text)
                # Return the full decoded JSON response
                return decoded_response
            else:
                self.logger.error(f"Failed to fetch blacklist data: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving blacklist: {e}")
            return None

    def report_endpoint(self, ip_address, categories, comment, iso_timestamp=None):
        """Report an IP address for abusive behavior to AbuseIPDB."""
        url = 'https://api.abuseipdb.com/api/v2/report'

        # Ensure the timestamp is in ISO 8601 format

        # Prepare the parameters for the report
        params = {
            'ip':ip_address,
            'categories':categories,
            'comment':comment,
            'timestamp':iso_timestamp
        }

        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }

        #print(f"api_key = {self.api_key}")
        #print(f"params = {params}")
        
        try:
            response = requests.request(method="POST", url=url, headers=headers, params=params)

            self.logger.debug(f"status_code returned is {response.status_code}")

            decoded_response = json.loads(response.text)
            if response.status_code == 200:
                # Print formatted output
                print(json.dumps(decoded_response, sort_keys=True, indent=4))
                # Return the response data for further processing
                return response.status_code
            else:
                print(json.dumps(decoded_response, sort_keys=True, indent=4))
                self.logger.error(f"Failed to report IP {ip_address}: {response.status_code}")
                return response.status_code
        except Exception as e:
            self.logger.error(f"An error occurred while reporting IP {ip_address}: {e}")
            return None

        return response.status_code
        
def main():
    if len(sys.argv) != 2:
        print("Usage: python {sys.argv[0]} <ip-address>")
        sys.exit(1)

    # Get the IP address from command-line arguments
    ip_address = sys.argv[1]

    # Initialize the class
    abuse_ipdb = AbuseIPDB()

    # Check the IP address and get the abuse confidence score
    print("Test check_endpoint")
    is_whitelisted, abuse_confidence_score = abuse_ipdb.check_endpoint(ip_address)

    if is_whitelisted is not None:
        print(f"Whitelisted for {ip_address}: {is_whitelisted}")
    else:
        print(f"Failed to retrieve whitelist information for {ip_address}")

    if abuse_confidence_score is not None:
        print(f"Abuse Confidence Score for {ip_address}: {abuse_confidence_score}")
    else:
        print(f"Failed to retrieve abuse confidence score for {ip_address}")

    # Example usage of report_endpoint
    print("Test report_endpoint")    
    categories = "18,20"
    comment = "SSH login attempts with user root."
    timestamp = "2023-10-18T11:25:11-04:00"  # Example ISO 8601 timestamp
    report_response = abuse_ipdb.report_endpoint(ip_address, categories, comment, timestamp)
    if report_response is not None:
        print(f"IP {ip_address} reported successfully: {report_response}")
    else:
        print(f"Failed to report IP {ip_address}")        
        
    # test blacklist_endpoint
    print("Test blacklist_endpoint")
    response = abuse_ipdb.blacklist_endpoint(ip_version="6")
    if response is not None:
        print(response)
    else:
        print("Failed to retrieve blacklist_endpoint report")

# Extracted function to set up logging configuration
def setup_logging(log_format, log_file_name):
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file_name, mode='a'),
        ]
    )
        
# Run the main function if this script is executed directly
if __name__ == "__main__":
    # Set up logger
    # Extracted constants for log file name and format
    LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
    # Set up the logging format to include file name and line number
    LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
    # do the deed
    setup_logging(LOG_FORMAT, LOG_FILE_NAME)
    
    main()
