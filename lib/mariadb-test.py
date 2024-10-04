import mysql.connector
import os
from dotenv import load_dotenv

# load dotenv
try:
    # Attempt to load dotenv file using the environment variable
    dotenv_config = load_dotenv(f"{os.getenv('HOME')}/.env")
    print("dotenv file loaded successfully.")
except Exception as e:
    # Handle any exceptions that may occur
    print(f"An error occurred while loading dotenv: {e}")

# Connect to MariaDB
try:
    conn = mysql.connector.connect(
        user=os.getenv('MARIADB_USER_NAME'),
        password=os.getenv('MARIADB_USER_PASSWORD'),
        host=os.getenv('MARIADB_USER_HOST'),
        port=3306,
        database=os.getenv('MARIADB_USER_DATABASE')
    )

    # Create a cursor object
    cursor = conn.cursor()

    # Execute a query
    cursor.execute("SELECT * FROM your_table")

    # Fetch and print the results
    for row in cursor:
        print(row)

except mysql.connector.Error as e:
    print(f"Error connecting to MariaDB: {e}")
finally:
    if conn:
        conn.close()
