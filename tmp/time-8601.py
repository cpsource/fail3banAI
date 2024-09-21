2023-10-18T11:25:11-04:00

from datetime import datetime, timezone

# Get the current time (UTC) and convert it to the local time zone
current_time = datetime.now(timezone.utc)

# Format the datetime object in ISO 8601 format
iso_timestamp = current_time.isoformat()

print(iso_timestamp)


from datetime import datetime, timedelta, timezone

# Define a timezone with a UTC offset of -04:00
tz_offset = timezone(timedelta(hours=-4))

# Get the current time in the specified time zone
current_time_with_offset = datetime.now(tz_offset)

# Output the timestamp in ISO 8601 format
iso_timestamp_with_offset = current_time_with_offset.isoformat()

print(iso_timestamp_with_offset)

