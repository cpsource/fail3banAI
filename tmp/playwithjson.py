import json
from datetime import datetime

def format_time_to_utc(time_str):
    """Convert ISO 8601 time string to a Python UTC datetime format"""
    try:
        parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))  # Handle ISO 8601 format
        return parsed_time.strftime("%Y-%m-%d %H:%M:%S %Z (UTC)")
    except ValueError:
        return "Invalid time format"

def display_json_data(json_file_path):
    """Display meta data and IP address data from a JSON file, formatting time fields to UTC"""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Display meta data
    if "meta" in data:
        print("Meta Information:")
        for key, value in data["meta"].items():
            if "generatedAt" in key:
                formatted_time = format_time_to_utc(value)
                print(f"{key}: {formatted_time}")
            else:
                print(f"{key}: {value}")
        print("-" * 40)  # Separator for readability
    
    # Display data entries
    if "data" in data:
        for entry in data["data"]:
            print("IP Address:", entry.get("ipAddress", "N/A"))
            print("Country Code:", entry.get("countryCode", "N/A"))
            print("Abuse Confidence Score:", entry.get("abuseConfidenceScore", "N/A"))
            
            last_reported = entry.get("lastReportedAt", "N/A")
            if last_reported != "N/A":
                formatted_reported_time = format_time_to_utc(last_reported)
                print("Last Reported At:", formatted_reported_time)
            else:
                print("Last Reported At: N/A")
                
            print("-" * 40)  # Separator for readability

# Example usage
json_file_path = 'zz1'
display_json_data(json_file_path)

