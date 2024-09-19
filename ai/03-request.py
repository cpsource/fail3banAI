import openai
import os

# Your OpenAI API key
def load_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    return api_key

# Your OpenAI API key
API_KEY = load_api_key()

# Set up your OpenAI API key
openai.api_key = API_KEY

# The journalctl entry you want to analyze
journalctl_entry = "Sep 17 10:20:41 ip-172-26-10-222 sudo-special[238085]: pam_unix(sudo:session): session opened for user root(uid=0) by ubuntu(uid=1000)"

# Define the prompt structure
messages = [
    {
        "role": "system",
        "content": "You are a security expert. I will provide journalctl logs, and your task is to analyze whether a given log entry is a security threat."
    },
    {
        "role": "user",
        "content": f"Journalctl entry: {journalctl_entry}. Is this journalctl entry a security threat?"
    }
]

# Call the ChatGPT API using the openai library
try:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages
        )
    
    # Access the response correctly
    response_message = response.choices[0].message['content']
    print("Response:", response_message)

except Exception as e:
    print(f"Error communicating with OpenAI API: {e}")

