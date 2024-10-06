#
# Note: To use this class, you must export DB_PASSWORD as something or the other
#

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import ipaddress
import os

class mariaDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.user_name = 'fail3ban'
        self.password = os.getenv('DB_PASSWORD')  # Get password from environment variable
        self.host = '127.0.0.1'
        self.database = 'fail3ban_db'

    def initialize(self):
        """Initialize the MariaDB connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user_name,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MariaDB")
                self.cursor = self.connection.cursor()
                self.create_ban_table()
        except Error as e:
            print(f"Error while connecting to MariaDB: {e}")
    
    def create_ban_table(self):
        """Create the ban_table if it doesn't already exist."""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS ban_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address CHAR(39),
            jail CHAR(100),
            usage_count INT,
            ban_expire_time DATETIME,
            UNIQUE (ip_address, jail)
        )
        '''
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def add_or_update_ban(self, ip_addr, jail_name, minutes_until_ban_end):
        """Add a new ban or update an existing ban based on ip_address and jail."""
        try:
            ip_obj = ipaddress.ip_address(ip_addr)
            ip_addr = ip_obj.exploded  # Use the long form of the IP address
        except ValueError:
            print(f"Invalid IP address: {ip_addr}")
            return

        ban_expire_time = datetime.now() + timedelta(minutes=minutes_until_ban_end)

        select_query = '''
        SELECT id, usage_count FROM ban_table WHERE ip_address = %s AND jail = %s
        '''
        self.cursor.execute(select_query, (ip_addr, jail_name))
        record = self.cursor.fetchone()

        if record:
            update_query = '''
            UPDATE ban_table 
            SET usage_count = usage_count + 1, ban_expire_time = %s
            WHERE ip_address = %s AND jail = %s
            '''
            self.cursor.execute(update_query, (ban_expire_time, ip_addr, jail_name))
            print(f"Updated ban for {ip_addr} in jail {jail_name}.")
        else:
            insert_query = '''
            INSERT INTO ban_table (ip_address, jail, usage_count, ban_expire_time) 
            VALUES (%s, %s, %s, %s)
            '''
            self.cursor.execute(insert_query, (ip_addr, jail_name, 1, ban_expire_time))
            print(f"Added new ban for {ip_addr} in jail {jail_name}.")

        self.connection.commit()

    def get_expired_records(self):
        """Return a list of expired records in the form [ip_addr, True-if-ipv6, else False, jail]."""
        expired_records = []
        current_time = datetime.now()

        query = '''
        SELECT ip_address, jail, ban_expire_time FROM ban_table WHERE ban_expire_time < %s
        '''
        self.cursor.execute(query, (current_time,))
        records = self.cursor.fetchall()

        for record in records:
            ip_addr, jail, ban_expire_time = record
            try:
                ip_obj = ipaddress.ip_address(ip_addr)
                is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                if is_ipv6:
                    ip_addr = ip_obj.compressed
            except ValueError:
                is_ipv6 = False

            expired_records.append([ip_addr, is_ipv6, jail])

        return expired_records

    def show_database(self):
        """Print all records in the database in a human-readable format, and show if the ban has expired."""
        current_time = datetime.now()

        query = '''
        SELECT id, ip_address, jail, usage_count, ban_expire_time FROM ban_table
        '''
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        if records:
            print(f"Found {len(records)} record(s):")
            for record in records:
                id, ip_addr, jail, usage_count, ban_expire_time = record
                try:
                    ip_obj = ipaddress.ip_address(ip_addr)
                    is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                    if is_ipv6:
                        ip_addr = ip_obj.compressed
                except ValueError:
                    is_ipv6 = False

                expired_status = "Expired" if current_time > ban_expire_time else "Active"
                print(f"ID: {id}, IP: {ip_addr}, Jail: {jail}, Usage Count: {usage_count}, "
                      f"Ban Expire Time: {ban_expire_time} ({expired_status})")
        else:
            print("No records found in the database.")

    def remove_record(self, ip_addr, jail_name):
        """Remove a record from the ban_table based on ip_address and jail_name."""
        delete_query = '''
        DELETE FROM ban_table WHERE ip_address = %s AND jail = %s
        '''
        self.cursor.execute(delete_query, (ip_addr, jail_name))
        self.connection.commit()
        print(f"Record for IP {ip_addr} in jail {jail_name} has been removed.")

    def close(self):
        """Close the database connection."""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MariaDB connection is closed.")

