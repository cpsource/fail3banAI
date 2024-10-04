import mysql.connector
import os

# Connect to MariaDB
try:
    conn = mysql.connector.connect(
        user="Ubuntu",
        password=os.getenv('MARIADB_USER_PASSWORD'),
        host="localhost",
        port=3306,
        database="fail3ban"
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
