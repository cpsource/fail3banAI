
from datetime import datetime
from datetime import timedelta

date_string = "20/Oct/2024:16:04:59 +0000"

# Define the format of the input string
input_format = "%d/%b/%Y:%H:%M:%S %z"

# Parse the string into a datetime object
datetime_object = datetime.strptime(date_string, input_format)

# Format the datetime object into a standard format (ISO 8601)
standard_datetime = datetime_object.isoformat()

# Create a timezone object for EST (Eastern Standard Time)
est_timezone = timedelta(hours=-5)  # EST is UTC-5
foo = est_timezone + datetime_object
print(foo)

# Print the standard datetime string
print(standard_datetime)

# Format the datetime object into MariaDB datetime format (YYYY-MM-DD HH:MM:SS)
mariadb_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
print(mariadb_datetime)

# Convert the MariaDB datetime string back to a datetime object
mariadb_datetime_object = datetime.strptime(mariadb_datetime, "%Y-%m-%d %H:%M:%S")
print(mariadb_datetime_object)
print(type(mariadb_datetime_object))
