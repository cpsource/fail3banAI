import mysql.connector
import json

def update_ip_info(ip_address, json_data):
    # Connect to the MariaDB database
    conn = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    cursor = conn.cursor()

    # Ensure json_data is a string
    json_string = json.dumps(json_data)

    # SQL query to insert or update the row, incrementing ref_cnt on update
    query = """
    INSERT INTO ip_responses (ip_address, response, ref_cnt, timestamp)
    VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
    ON DUPLICATE KEY UPDATE
        response = VALUES(response),
        ref_cnt = ref_cnt + 1,
        timestamp = CURRENT_TIMESTAMP;
    """

    try:
        # Execute the query with the IP address and the JSON data
        cursor.execute(query, (ip_address, json_string))

        # Commit the transaction
        conn.commit()
        print(f"IP info for {ip_address} has been inserted/updated.")
    
    except mysql.connector.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        cursor.close()
        conn.close()
