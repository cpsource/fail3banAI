#!/usr/bin/python3
import requests

def get_public_ip():
    try:
        # Fetch the public IP using a public API
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Raise an error for bad status codes
        ip_info = response.json()
        return ip_info['ip']
    except requests.RequestException as e:
        return f"Error fetching IP address: {e}"

if __name__ == "__main__":
    public_ip = get_public_ip()
    print(f"Your public IP address is: {public_ip}")

