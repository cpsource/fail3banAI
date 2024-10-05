import requests
import json
import os

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/check'
url = 'https://api.abuseipdb.com/api/v2/blacklist'

querystring = {
    'confidenceMinimum' : '90',
    'onlyCountries' : 'IR'
}

headers = {
    'Accept': 'application/json',
    'Key': f'{os.getenv("ABUSEIPDB_KEY")}'
}

response = requests.request(method='GET', url=url, headers=headers, params=querystring)

# Formatted output
decodedResponse = json.loads(response.text)
print(json.dumps(decodedResponse, sort_keys=True, indent=4))
