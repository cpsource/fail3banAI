
import mysql.connector
import os
import sys
import json

class CreateIPResponseTable:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()
        self.create_index()

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ip_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL UNIQUE,  -- Unique IP address
            response TEXT NOT NULL,                  -- Response data (JSON or plain text)
            ref_cnt INT DEFAULT 1,                   -- Reference count, initialized to 1
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        cursor = self.conn.cursor()
        cursor.execute(create_table_sql)
        self.conn.commit()
        cursor.close()

    def create_index(self):
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_ip_address ON ip_responses (ip_address);
        """
        cursor = self.conn.cursor()
        cursor.execute(create_index_sql)
        self.conn.commit()
        cursor.close()

    def update_ip_info(self, ip_address, json_data):
        json_string = json.dumps(json_data)
        query = """
        INSERT INTO ip_responses (ip_address, response, ref_cnt, timestamp)
        VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE
            response = VALUES(response),
            ref_cnt = ref_cnt + 1,
            timestamp = CURRENT_TIMESTAMP;
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (ip_address, json_string))
            self.conn.commit()
            print(f"IP info for {ip_address} has been inserted/updated.")
        except mysql.connector.Error as e:
            print(f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()

    def lookup_ip_info(self, ip_address):
        query_select = """
        SELECT ip_address, response, ref_cnt, timestamp FROM ip_responses WHERE ip_address = %s;
        """
        query_update = """
        UPDATE ip_responses SET ref_cnt = ref_cnt + 1, timestamp = CURRENT_TIMESTAMP WHERE ip_address = %s;
        """
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)

            # Retrieve the IP address record
            cursor.execute(query_select, (ip_address,))
            record = cursor.fetchone()

            if record:
                # Increment the ref_cnt if the record exists
                cursor.execute(query_update, (ip_address,))
                self.conn.commit()

                # Return the JSON response stored in the database
                return json.loads(record["response"])
            else:
                print(f"No record found for IP address: {ip_address}")
                return None
        except mysql.connector.Error as e:
            print(f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_json_info(self, ip_address):
        # Defining the API endpoint
        url = 'https://api.abuseipdb.com/api/v2/check'

        # Set up headers for the request
        headers = {
            'Accept': 'application/json',
            'Key': os.getenv('ABUSEIPDB_KEY')  # Get the API key from environment variable
        }

        # Query parameters for the request
        querystring = {
            'ipAddress': ip_address,
            'maxAgeInDays': '90'
        }

        try:
            # Send the request to AbuseIPDB
            response = requests.get(url, headers=headers, params=querystring)

            # Check if the response is successful
            if response.status_code == 200:
                # Parse the response into a Python dictionary
                decoded_response = response.json()

                # Extract relevant fields into a dictionary
                ip_info = {
                    "ipAddress": decoded_response["data"].get("ipAddress"),
                    "abuseConfidenceScore": decoded_response["data"].get("abuseConfidenceScore"),
                    "countryCode": decoded_response["data"].get("countryCode"),
                    "domain": decoded_response["data"].get("domain"),
                    "hostnames": decoded_response["data"].get("hostnames"),
                    "ipVersion": decoded_response["data"].get("ipVersion"),
                    "isPublic": decoded_response["data"].get("isPublic"),
                    "isTor": decoded_response["data"].get("isTor"),
                    "isWhitelisted": decoded_response["data"].get("isWhitelisted"),
                    "isp": decoded_response["data"].get("isp"),
                    "lastReportedAt": decoded_response["data"].get("lastReportedAt"),
                    "numDistinctUsers": decoded_response["data"].get("numDistinctUsers"),
                    "totalReports": decoded_response["data"].get("totalReports"),
                    "usageType": decoded_response["data"].get("usageType")
                }

                return ip_info  # Return the extracted information

            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

def main():
    project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
    # Add the constructed path to sys.path only if it's not already in sys.path
    lib_path = os.path.join(project_root, 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
        print(f"Prepending {lib_path} to sys.path")

    # Get our swiss army knife
    import Swan
    swan = Swan.Swan()
    logger = swan.get_logger()
    logger.debug(sys.path)
    swan.set_os_path()
    swan.load_dotenv()

    # Setup MariaDB connection using mysql.connector
    conn = swan.get_new_connection()

    # Create the table and index
    table_manager = CreateIPResponseTable(conn)

    # The IP address to lookup
    ip_address = "185.234.216.122"

    # Check if the IP address is already in the database
    stored_ip_info = table_manager.lookup_ip_info(ip_address)

    if stored_ip_info:
        # If IP info is already in the database, display it
        print(f"IP info for {ip_address} found in database:")
        for key, value in stored_ip_info.items():
            print(f"{key}: {value}")
    else:
        # If IP info is not found, get it from AbuseIPDB and update the database
        print(f"IP info for {ip_address} not found in database. Fetching from AbuseIPDB...")
        ip_info = table_manager.get_json_info(ip_address)

        if ip_info:
            # Print the IP info fetched from AbuseIPDB
            print(f"Fetched IP info for {ip_address}:")
            for key, value in ip_info.items():
                print(f"{key}: {value}")

            # Update the database with the fetched IP info
            table_manager.update_ip_info(ip_address, ip_info)
        else:
            print(f"Failed to retrieve IP info from AbuseIPDB for {ip_address}.")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()

