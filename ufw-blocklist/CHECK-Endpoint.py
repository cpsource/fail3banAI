import requests
import json
import os

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/check'

querystring = {
    'ipAddress': '193.151.159.58',
    'maxAgeInDays': '90'
}

headers = {
    'Accept': 'application/json',
    'Key': f'{os.getenv("ABUSEIPDB_KEY")}'
}

response = requests.request(method='GET', url=url, headers=headers, params=querystring)
print(response.status_code, response.reason)
print(dir(response))
print(response, response.text)

# Formatted output
decodedResponse = json.loads(response.text)
print(json.dumps(decodedResponse, sort_keys=True, indent=2))
