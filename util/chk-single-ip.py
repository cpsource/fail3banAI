import os
import requests
import json

chklst = [
    '103.203.57.21',
    '141.98.11.79',
    '78.153.140.78',
    '154.213.184.15',
    '93.123.85.155',
    ]

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/check'

headers = {
    'Accept': 'application/json',
    'Key': os.getenv('ABUSEIPDB_KEY')
}

for ip_address in chklst:
    querystring = {
        'ipAddress': f'{ip_address}',
        'maxAgeInDays': '90'
    }

    response = requests.request(method='GET', url=url, headers=headers, params=querystring)

    # Formatted output
    decodedResponse = json.loads(response.text)
    print (f"Ip Address: {ip_address}")
    print (json.dumps(decodedResponse, sort_keys=True, indent=4))
