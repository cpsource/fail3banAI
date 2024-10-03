import sys
import requests

def send_options_request(url):
    try:
        response = requests.options(url)
        # Display allowed methods and status code
        allowed_methods = response.headers.get('Allow', 'No Allow header found')
        print(f"Allowed Methods: {allowed_methods}")
        print(f"Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python options_request.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    send_options_request(url)

