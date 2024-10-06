from datetime import datetime

# Original date string
date_str = 'Fri Sep 27 13:18:10.775263 2024'

# Parse the date string into a datetime object
dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S.%f %Y')

# Convert to Zulu time (UTC) in ISO 8601 format, without fractional seconds
zulu_time_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

print(zulu_time_str)

