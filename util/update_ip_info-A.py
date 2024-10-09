def lookup_ip_info(ip_address):
    # Connect to MariaDB
    conn = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    cursor = conn.cursor(dictionary=True)

    # Combined query: Increment ref_cnt and retrieve the record at the same time
    query = """
    UPDATE ip_responses
    SET ref_cnt = ref_cnt + 1, timestamp = CURRENT_TIMESTAMP
    WHERE ip_address = %s;
    
    SELECT ip_address, response, ref_cnt, timestamp 
    FROM ip_responses 
    WHERE ip_address = %s;
    """

    try:
        # Execute the query to update and retrieve the row
        cursor.execute(query, (ip_address, ip_address))
        conn.commit()

        # Fetch the result
        cursor.execute("SELECT ip_address, response, ref_cnt, timestamp FROM ip_responses WHERE ip_address = %s", (ip_address,))
        record = cursor.fetchone()

        if record:
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
