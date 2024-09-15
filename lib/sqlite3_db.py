# sqlite3_db.py

# Note

#  This code should be thread-safe, in that each thread will initialize
#  their own SQLiteDB
#

import sqlite3
from datetime import datetime, timedelta
import ipaddress
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sqlite3_db.log"),
        logging.StreamHandler()
    ]
)

class SQLiteDB:

    def __init__(self, db_name):
        """
        Initializes the database connection.

        Parameters:
            db_name (str): The name of the SQLite database file.
        """
        try:
            self.db_name = db_name
            self.connection = sqlite3.connect(db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
            # Create tables if they don't exist
            self.create_ban_table()
            logging.info(f"Connected to database '{db_name}' successfully.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while connecting to the database: {e}")
            self.connection = None
            self.cursor = None
            self.db_name = None
            raise  # Re-raise the exception to notify higher-level code

    def create_ban_table(self):
        """Create the ban_table if it doesn't already exist."""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS ban_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address CHAR(40),
            jail CHAR(100),
            usage_count INTEGER,
            ban_expire_time DATETIME,
            UNIQUE(ip_address, jail)
        )
        '''
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logging.info("ban_table created or already exists.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while creating ban_table: {e}")
            raise  # Re-raise the exception to notify higher-level code

    def add_or_update_ban(self, ip_addr, jail_name, minutes_until_ban_end):
        """Add a new ban or update an existing ban based on ip_address and jail."""
        # Parse and expand the IP address (IPv6 addresses to full form)
        try:
            ip_obj = ipaddress.ip_address(ip_addr)
            ip_addr = ip_obj.exploded  # Use the long form of the IP address
        except ValueError as e:
            logging.error(f"Invalid IP address '{ip_addr}': {e}")
            raise  # Re-raise to notify higher-level code

        # Calculate new ban expiration time
        ban_expire_time = datetime.now() + timedelta(minutes=minutes_until_ban_end)

        try:
            # Look up the existing record by ip_address and jail_name
            select_query = '''
            SELECT id, usage_count FROM ban_table WHERE ip_address = ? AND jail = ?
            '''
            self.cursor.execute(select_query, (ip_addr, jail_name))
            record = self.cursor.fetchone()

            if record:
                # If the record exists, update usage_count and ban_expire_time
                update_query = '''
                UPDATE ban_table 
                SET usage_count = usage_count + 1, ban_expire_time = ? 
                WHERE ip_address = ? AND jail = ?
                '''
                self.cursor.execute(update_query, (ban_expire_time, ip_addr, jail_name))
                self.connection.commit()
                logging.info(f"Updated ban for IP {ip_addr} in jail '{jail_name}'.")
            else:
                # If the record does not exist, insert a new record
                insert_query = '''
                INSERT INTO ban_table (ip_address, jail, usage_count, ban_expire_time) 
                VALUES (?, ?, ?, ?)
                '''
                self.cursor.execute(insert_query, (ip_addr, jail_name, 1, ban_expire_time))
                self.connection.commit()
                logging.info(f"Added new ban for IP {ip_addr} in jail '{jail_name}'.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while adding/updating ban: {e}")
            raise  # Re-raise to notify higher-level code

    def get_expired_records(self):
        """Return a list of expired records in the form [ip_addr, is_ipv6, jail]."""
        expired_records = []

        # Get the current time
        current_time = datetime.now()

        try:
            # Query for expired records (ban_expire_time < current_time)
            query = '''
            SELECT ip_address, jail, ban_expire_time FROM ban_table WHERE ban_expire_time < ?
            '''
            self.cursor.execute(query, (current_time,))
            records = self.cursor.fetchall()

            # Process each record to check if the IP is IPv6 and format the output
            for record in records:
                ip_addr, jail, ban_expire_time = record
                # Determine if the IP address is IPv6 using ipaddress module
                try:
                    ip_obj = ipaddress.ip_address(ip_addr)
                    is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)

                    # If it's IPv6, shrink it to its smallest form (compressed)
                    if is_ipv6:
                        ip_addr = ip_obj.compressed
                except ValueError:
                    # Handle any invalid IP address (if applicable)
                    is_ipv6 = False

                # Add the record in the form [ip_addr, is_ipv6, jail]
                expired_records.append([ip_addr, is_ipv6, jail])
        except sqlite3.Error as e:
            logging.error(f"An error occurred while fetching expired records: {e}")
            raise  # Re-raise to notify higher-level code

        return expired_records

    def show_bans(self, ip_addr=None, jail_name=None):
        """Show a list of records in a human-readable format for the given ip_addr and jail_name."""
        # Build the base query
        query = "SELECT id, ip_address, jail, usage_count, ban_expire_time FROM ban_table WHERE 1=1"
        params = []

        # Add filtering by ip_addr if provided
        if ip_addr:
            query += " AND ip_address = ?"
            params.append(ip_addr)

        # Add filtering by jail_name if provided
        if jail_name:
            query += " AND jail = ?"
            params.append(jail_name)

        try:
            # Execute the query
            self.cursor.execute(query, tuple(params))
            records = self.cursor.fetchall()

            # Check if records were found
            if records:
                logging.info(f"Found {len(records)} record(s):")
                for record in records:
                    ip_addr, jail = record[1], record[2]
                    try:
                        ip_obj = ipaddress.ip_address(ip_addr)
                        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                        if is_ipv6:
                            ip_addr = ip_obj.compressed  # Shrink IPv6 address to its compressed form
                    except ValueError:
                        is_ipv6 = False
                    logging.info(
                        f"ID: {record[0]}, IP: {ip_addr}, Jail: {jail}, "
                        f"Usage Count: {record[3]}, Ban Expire Time: {record[4]}"
                    )
            else:
                logging.info("No matching records found.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while showing bans: {e}")
            raise  # Re-raise to notify higher-level code

    def remove_record(self, ip_addr, jail_name):
        """Remove a record from the ban_table based on ip_address and jail_name."""
        delete_query = '''
        DELETE FROM ban_table WHERE ip_address = ? AND jail = ?
        '''
        try:
            self.cursor.execute(delete_query, (ip_addr, jail_name))
            self.connection.commit()
            logging.info(f"Record for IP {ip_addr} in jail '{jail_name}' has been removed.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while removing record: {e}")
            raise  # Re-raise to notify higher-level code

    def show_database(self):
        """Show all records in the database in a human-readable format, and show if the ban has expired."""
        # Get the current time
        current_time = datetime.now()

        try:
            # Query to select all records from the ban_table
            query = "SELECT id, ip_address, jail, usage_count, ban_expire_time FROM ban_table"
            self.cursor.execute(query)
            records = self.cursor.fetchall()

            # Check if records were found
            if records:
                logging.info(f"Found {len(records)} record(s):")
                for record in records:
                    id, ip_addr, jail, usage_count, ban_expire_time = record

                    # Determine if the IP address is IPv6 and compress it
                    try:
                        ip_obj = ipaddress.ip_address(ip_addr)
                        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                        if is_ipv6:
                            ip_addr = ip_obj.compressed  # Shrink IPv6 address to its compressed form
                    except ValueError:
                        is_ipv6 = False

                    # Check if the ban has expired
                    try:
                        ban_expire_time_dt = datetime.strptime(ban_expire_time, '%Y-%m-%d %H:%M:%S.%f')
                        if current_time > ban_expire_time_dt:
                            expired_status = "Expired"
                        else:
                            expired_status = "Active"
                    except ValueError:
                        expired_status = "Unknown"

                    # Log the record with ban status
                    logging.info(
                        f"ID: {id}, IP: {ip_addr}, Jail: {jail}, Usage Count: {usage_count}, "
                        f"Ban Expire Time: {ban_expire_time} ({expired_status})"
                    )
            else:
                logging.info("No records found in the database.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while showing the database: {e}")
            raise  # Re-raise to notify higher-level code

    def close(self):
        """Close the database connection and cursor."""
        if self.cursor:
            try:
                self.cursor.close()
                logging.info("Database cursor closed.")
                self.cursor = None  # Prevent further use
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the cursor: {e}")
                raise
        
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logging.info("Database connection closed.")
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the database connection: {e}")
                raise  # Re-raise to notify higher-level code

    def __del__(self):
        """
        Destructor method to close the database connection when the object is destroyed.
        """
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.close()
                logging.info("Database connection closed.")
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the database connection: {e}")

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the connection and cursor."""
        self.close()

# sqlite3_db.py

# Note

#  This code should be thread-safe, in that each thread will initialize
#  their own SQLiteDB
#

import sqlite3
from datetime import datetime, timedelta
import ipaddress
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sqlite3_db.log"),
        logging.StreamHandler()
    ]
)

class SQLiteDB:
    def __init__(self, db_name):
        """
        Initializes the database connection.

        Parameters:
            db_name (str): The name of the SQLite database file.
        """
        try:
            self.db_name = db_name
            self.connection = sqlite3.connect(db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
            # Create tables if they don't exist
            self.create_ban_table()
            logging.info(f"Connected to database '{db_name}' successfully.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while connecting to the database: {e}")
            self.connection = None
            self.cursor = None
            self.db_name = None
            raise  # Re-raise the exception to notify higher-level code

    def create_ban_table(self):
        """Create the ban_table if it doesn't already exist."""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS ban_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address CHAR(40),
            jail CHAR(100),
            usage_count INTEGER,
            ban_expire_time DATETIME,
            UNIQUE(ip_address, jail)
        )
        '''
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logging.info("ban_table created or already exists.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while creating ban_table: {e}")
            raise  # Re-raise the exception to notify higher-level code

    def add_or_update_ban(self, ip_addr, jail_name, minutes_until_ban_end):
        """Add a new ban or update an existing ban based on ip_address and jail."""
        # Parse and expand the IP address (IPv6 addresses to full form)
        try:
            ip_obj = ipaddress.ip_address(ip_addr)
            ip_addr = ip_obj.exploded  # Use the long form of the IP address
        except ValueError as e:
            logging.error(f"Invalid IP address '{ip_addr}': {e}")
            raise  # Re-raise to notify higher-level code

        # Calculate new ban expiration time
        ban_expire_time = datetime.now() + timedelta(minutes=minutes_until_ban_end)

        try:
            # Look up the existing record by ip_address and jail_name
            select_query = '''
            SELECT id, usage_count FROM ban_table WHERE ip_address = ? AND jail = ?
            '''
            self.cursor.execute(select_query, (ip_addr, jail_name))
            record = self.cursor.fetchone()

            if record:
                # If the record exists, update usage_count and ban_expire_time
                update_query = '''
                UPDATE ban_table 
                SET usage_count = usage_count + 1, ban_expire_time = ? 
                WHERE ip_address = ? AND jail = ?
                '''
                self.cursor.execute(update_query, (ban_expire_time, ip_addr, jail_name))
                self.connection.commit()
                logging.info(f"Updated ban for IP {ip_addr} in jail '{jail_name}'.")
            else:
                # If the record does not exist, insert a new record
                insert_query = '''
                INSERT INTO ban_table (ip_address, jail, usage_count, ban_expire_time) 
                VALUES (?, ?, ?, ?)
                '''
                self.cursor.execute(insert_query, (ip_addr, jail_name, 1, ban_expire_time))
                self.connection.commit()
                logging.info(f"Added new ban for IP {ip_addr} in jail '{jail_name}'.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while adding/updating ban: {e}")
            raise  # Re-raise to notify higher-level code

    def get_expired_records(self):
        """Return a list of expired records in the form [ip_addr, is_ipv6, jail]."""
        expired_records = []

        # Get the current time
        current_time = datetime.now()

        try:
            # Query for expired records (ban_expire_time < current_time)
            query = '''
            SELECT ip_address, jail, ban_expire_time FROM ban_table WHERE ban_expire_time < ?
            '''
            self.cursor.execute(query, (current_time,))
            records = self.cursor.fetchall()

            # Process each record to check if the IP is IPv6 and format the output
            for record in records:
                ip_addr, jail, ban_expire_time = record
                # Determine if the IP address is IPv6 using ipaddress module
                try:
                    ip_obj = ipaddress.ip_address(ip_addr)
                    is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)

                    # If it's IPv6, shrink it to its smallest form (compressed)
                    if is_ipv6:
                        ip_addr = ip_obj.compressed
                except ValueError:
                    # Handle any invalid IP address (if applicable)
                    is_ipv6 = False

                # Add the record in the form [ip_addr, is_ipv6, jail]
                expired_records.append([ip_addr, is_ipv6, jail])
        except sqlite3.Error as e:
            logging.error(f"An error occurred while fetching expired records: {e}")
            raise  # Re-raise to notify higher-level code

        return expired_records

    def show_bans(self, ip_addr=None, jail_name=None):
        """Show a list of records in a human-readable format for the given ip_addr and jail_name."""
        # Build the base query
        query = "SELECT id, ip_address, jail, usage_count, ban_expire_time FROM ban_table WHERE 1=1"
        params = []

        # Add filtering by ip_addr if provided
        if ip_addr:
            query += " AND ip_address = ?"
            params.append(ip_addr)

        # Add filtering by jail_name if provided
        if jail_name:
            query += " AND jail = ?"
            params.append(jail_name)

        try:
            # Execute the query
            self.cursor.execute(query, tuple(params))
            records = self.cursor.fetchall()

            # Check if records were found
            if records:
                logging.info(f"Found {len(records)} record(s):")
                for record in records:
                    ip_addr, jail = record[1], record[2]
                    try:
                        ip_obj = ipaddress.ip_address(ip_addr)
                        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                        if is_ipv6:
                            ip_addr = ip_obj.compressed  # Shrink IPv6 address to its compressed form
                    except ValueError:
                        is_ipv6 = False
                    logging.info(
                        f"ID: {record[0]}, IP: {ip_addr}, Jail: {jail}, "
                        f"Usage Count: {record[3]}, Ban Expire Time: {record[4]}"
                    )
            else:
                logging.info("No matching records found.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while showing bans: {e}")
            raise  # Re-raise to notify higher-level code

    def remove_record(self, ip_addr, jail_name):
        """Remove a record from the ban_table based on ip_address and jail_name."""
        delete_query = '''
        DELETE FROM ban_table WHERE ip_address = ? AND jail = ?
        '''
        try:
            self.cursor.execute(delete_query, (ip_addr, jail_name))
            self.connection.commit()
            logging.info(f"Record for IP {ip_addr} in jail '{jail_name}' has been removed.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while removing record: {e}")
            raise  # Re-raise to notify higher-level code

    def show_database(self):
        """Show all records in the database in a human-readable format, and show if the ban has expired."""
        # Get the current time
        current_time = datetime.now()

        try:
            # Query to select all records from the ban_table
            query = "SELECT id, ip_address, jail, usage_count, ban_expire_time FROM ban_table"
            self.cursor.execute(query)
            records = self.cursor.fetchall()

            # Check if records were found
            if records:
                logging.info(f"Found {len(records)} record(s):")
                for record in records:
                    id, ip_addr, jail, usage_count, ban_expire_time = record

                    # Determine if the IP address is IPv6 and compress it
                    try:
                        ip_obj = ipaddress.ip_address(ip_addr)
                        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                        if is_ipv6:
                            ip_addr = ip_obj.compressed  # Shrink IPv6 address to its compressed form
                    except ValueError:
                        is_ipv6 = False

                    # Check if the ban has expired
                    try:
                        ban_expire_time_dt = datetime.strptime(ban_expire_time, '%Y-%m-%d %H:%M:%S.%f')
                        if current_time > ban_expire_time_dt:
                            expired_status = "Expired"
                        else:
                            expired_status = "Active"
                    except ValueError:
                        expired_status = "Unknown"

                    # Log the record with ban status
                    logging.info(
                        f"ID: {id}, IP: {ip_addr}, Jail: {jail}, Usage Count: {usage_count}, "
                        f"Ban Expire Time: {ban_expire_time} ({expired_status})"
                    )
            else:
                logging.info("No records found in the database.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while showing the database: {e}")
            raise  # Re-raise to notify higher-level code

    def close(self):
        """Close the database connection and cursor."""
        # Close the cursor first
        if self.cursor:
            try:
                self.cursor.close()
                logging.info("Database cursor closed.")
                self.cursor = None  # Prevent further use
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the cursor: {e}")
                raise  # Re-raise to notify higher-level code

        # Close the connection
        if self.connection:
            try:
                self.connection.close()
                logging.info("Database connection closed.")
                self.connection = None  # Prevent further use
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the database connection: {e}")
                raise  # Re-raise to notify higher-level code

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the connection and cursor."""
        self.close()

    def __del__(self):
        """
        Destructor method to close the database connection when the object is destroyed.
        """
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.close()
                logging.info("Database connection closed.")
            except sqlite3.Error as e:
                logging.error(f"An error occurred while closing the database connection: {e}")

# Example main to use the new get_expired_records method
def main():
    try:
        with SQLiteDB('bans.db') as db:
            # Example usage of add_or_update_ban method
            ip_addr_ipv6 = '2001:db8::1'  # Example shortened IPv6 address
            jail_name = 'ssh'
            minutes_until_ban_end = 1  # Set short ban for testing
            # First call to add_or_update_ban (inserts a new record)
            db.add_or_update_ban(ip_addr_ipv6, jail_name, minutes_until_ban_end)

            # Example usage of add_or_update_ban method
            ip_addr_ipv4 = '192.168.8.0'  # Example IPv4 address
            jail_name = 'ssh'
            minutes_until_ban_end = 1  # Set short ban for testing
            # First call to add_or_update_ban (inserts a new record)
            db.add_or_update_ban(ip_addr_ipv4, jail_name, minutes_until_ban_end)

            # Show all bans
            db.show_database()

            # Wait for the ban to expire (for testing purposes)
            logging.info("Waiting for the bans to expire...")
            import time
            time.sleep(70)  # Wait for over a minute

            # Get and log expired records
            expired_records = db.get_expired_records()
            if expired_records:
                logging.info("Expired records:")
                for record in expired_records:
                    logging.info(record)
            else:
                logging.info("No expired records.")

            # Show all bans again to reflect expirations
            db.show_database()

    except sqlite3.Error as e:
        logging.error(f"Database error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Explicitly close the database connection if it's still open
        # Note: Using context manager handles this, but this is a safety net
        try:
            if 'db' in locals() and db.connection:
                db.close()
        except Exception as e:
            logging.error(f"Error occurred while closing the database: {e}")

if __name__ == "__main__":
    main()


