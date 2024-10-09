import mysql.connector
import json

# Function to update or insert IP info
def update_ip_info(ip_address, json_data):
    # Connect to MariaDB
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
        cursor.execute(query, (ip_address, json_string))
        conn.commit()
        print(f"IP info for {ip_address} has been inserted/updated.")
    
    except mysql.connector.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        cursor.close()
        conn.close()

# Function to lookup IP info and increment ref_cnt
def lookup_ip_info(ip_address):
    # Connect to MariaDB
    conn = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    cursor = conn.cursor(dictionary=True)

    # SQL query to retrieve the record and increment the usage count
    query_select = """
    SELECT ip_address, response, ref_cnt, timestamp FROM ip_responses WHERE ip_address = %s;
    """
    query_update = """
    UPDATE ip_responses SET ref_cnt = ref_cnt + 1, timestamp = CURRENT_TIMESTAMP WHERE ip_address = %s;
    """

    try:
        # Retrieve the IP address record
        cursor.execute(query_select, (ip_address,))
        record = cursor.fetchone()

        if record:
            # Increment the ref_cnt if the record exists
            cursor.execute(query_update, (ip_address,))
            conn.commit()

            # Return the JSON response stored in the database
            return json.loads(record["response"])
        else:
            print(f"No record found for IP address: {ip_address}")
            return None

    except mysql.connector.Error as e:
        print(f"An error occurred: {e}")

    finally:
        cursor.close()
        conn.close()

# __main__ test cases for updating and looking up IP information
if __name__ == "__main__":
    # Test data for inserting/updating
    ip_address_test = '192.168.1.1'
    json_data_test = {
        "abuseConfidenceScore": 75,
        "countryCode": "US",
        "domain": "example.com",
        "hostnames": ["host.example.com"],
        "isp": "Example ISP"
    }

    # Update the IP info (inserts if not present)
    update_ip_info(ip_address_test, json_data_test)

    # Lookup the IP info and increment the ref_cnt
    result = lookup_ip_info(ip_address_test)
    if result:
        print("Lookup Result:", json.dumps(result, indent=4))

