#!/bin/bash

# Set the database file name
DB_NAME="bans.db"

# Check if the database file exists
if [[ ! -f "$DB_NAME" ]]; then
    echo "Error: Database file '$DB_NAME' not found."
    exit 1
fi

# Display the schema for ban_table
echo "Schema of ban_table:"
sqlite3 "$DB_NAME" "PRAGMA table_info(ban_table);"

echo ""

# n the sqlite3 command to display the contents of the ban_table
echo "Contents of ban_table:"
sqlite3 "$DB_NAME" "SELECT * FROM ban_table;"

# Exit with success
exit 0

