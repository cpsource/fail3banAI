import requests
import json
import os

def load_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    return api_key

# Your OpenAI API key
API_KEY = load_api_key()

# The URL for the OpenAI API
url = "https://api.openai.com/v1/chat/completions"

# The journalctl entry you want to analyze
#journalctl_entry = "Sep 17 10:20:41 ip-172-26-10-222 sudo-special[238085]: pam_unix(sudo:session): session opened for user root(uid=0) by ubuntu(uid=1000)"
journalctl_entry = "Sep 19 15:28:58 ip-172-26-10-222 sshd[4254]: Invalid user  from 64.62.156.33 port 45647"

# The payload to send to the API
payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "system",
            "content": "You are a security expert. I will provide journalctl logs, and your task is to analyze whether a given log entry is a security threat."
        },
        {
            "role": "user",
            "content": f"Journalctl entry: {journalctl_entry}. Is this journalctl entry a security threat? Give me a one line answer."
        }
    ]
}

# The headers required by the OpenAI API
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Send the POST request to the OpenAI API
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Print the response from the API
if response.status_code == 200:
    api_response = response.json()
    print("Response:", api_response['choices'][0]['message']['content'])
else:
    print(f"Failed to get a valid response, status code: {response.status_code}")
    print(response.text)
