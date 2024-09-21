import requests
import json
import os
from dotenv import load_dotenv

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/blacklist'

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

querystring = {
    'ipVersion': "6",
    'maxAgeInDays': '90'
}

headers = {
    'Accept': 'application/json',
    'Key': f"{api_key}"
}

response = requests.request(method='GET', url=url, headers=headers, params=querystring)

# Check if the response was successful
res = None
if response.status_code == 200:
    # Return the parsed JSON response
    res = json.loads(response.text)

print(res)

