#!/usr/bin/env python3
import openai
import json
import os
import sys
import re

def load_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    return api_key

def generate_json(log_entry):
    """
    Sends the log entry to OpenAI's API and retrieves the JSON response if it's a threat.
    """
    prompt = f"""
    I have a journalctl log entry that I don't recognize. Please determine if it's a security threat. If it is, provide a JSON output with the following structure:

    {{
      "match-subs": [
        {{
          "subroutine": "<subroutine_name>",
          "pattern": "<regex_pattern>"
        }}
      ],
      "match-chains": [
        {{
          "log_entry": "<description>",
          "subroutines": [
            "match_date",
            "match_host",
            "match_process",
            "<subroutine_name>"
          ]
        }}
      ]
    }}

    The log entry is:
    {log_entry}

    Only provide the JSON output if it's a security threat. Otherwise, respond with "{{\"message\": \"No threat detected.\"}}"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts journalctl log entries into JSON configurations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        sys.exit(1)

def is_threat(json_response):
    """
    Determines if the response indicates a threat.
    """
    try:
        data = json.loads(json_response)
        if "message" in data and data["message"] == "No threat detected.":
            return False, data["message"]
        else:
            return True, data
    except json.JSONDecodeError:
        return False, "Invalid JSON response."

def save_json(json_data, config_path="config.json"):
    """
    Saves the JSON data to a configuration file.
    """
    if not os.path.exists(config_path):
        # Initialize the config file
        with open(config_path, 'w') as f:
            json.dump({"match-subs": [], "match-chains": []}, f, indent=2)

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Append new subroutines if they don't exist
    for sub in json_data.get("match-subs", []):
        if sub not in config["match-subs"]:
            config["match-subs"].append(sub)

    # Append new match-chains if they don't exist
    for chain in json_data.get("match-chains", []):
        if chain not in config["match-chains"]:
            config["match-chains"].append(chain)

    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: ./log_parser.py \"<journalctl_log_entry>\"")
        sys.exit(1)

    log_entry = sys.argv[1]
    api_key = load_api_key()
    openai.api_key = api_key

    json_response = generate_json(log_entry)
    threat, data = is_threat(json_response)

    if threat:
        print("Threat detected. JSON output:")
        print(json.dumps(data, indent=2))
        save_json(data)
    else:
        print("No threat detected.")

if __name__ == "__main__":
    main()

