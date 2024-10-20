import re
from datetime import datetime

def get_datetime(s):
    pattern = r"([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
    match = re.search(pattern, s)
    
    if match:
        m = match.group(1)
        print(f"get_datetime, m = {m}")
        
        # Get the current year and append it to the date string
        current_year = datetime.now().year
        full_date_str = f"{current_year} {m}"
        
        # Parse the date string with the year included
        parsed_date = datetime.strptime(full_date_str, '%Y %b %d %H:%M:%S')
        
        # Convert the datetime object back to a string
        res = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        print(f"get_datetime, match, {res}")
    else:
        print(f"get_datetime, no match, {s}")
        res = None

    return res

# Example usage:
log_str = "Sep 27 08:41:16(fubar - etc"
result = get_datetime(log_str)
print(f"Result: {result}")
print(f"{type(result)}")
