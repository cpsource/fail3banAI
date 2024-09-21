import requests
import json

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/report'

# String holding parameters to pass in json format
params = {
    'ip':'180.126.219.126',
    'categories':'18,20',
    'comment':'SSH login attempts with user root.'
    'timestamp':'2023-10-18T11:25:11-04:00'
}

headers = {
    'Accept': 'application/json',
    'Key': 'YOUR_OWN_API_KEY'
}

response = requests.request(method='POST', url=url, headers=headers, params=params)

# Formatted output
decodedResponse = json.loads(response.text)
print json.dumps(decodedResponse, sort_keys=True, indent=4)
