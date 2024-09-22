# sqlite3_db.py

# Note

#  This code should be thread-safe, in that each thread will initialize
#  their own SQLiteDB
#

import os
import sqlite3
from datetime import datetime, timedelta
import ipaddress
import logging
import atexit

LOG_ID = "fail3ban"

class SQLiteDB:

    def __init__(self, db_name="fail3ban_server.db", log_id=LOG_ID):
        """
        Initializes the database connection.

        Parameters:
            db_name (str): The name of the SQLite database file.
        """
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        # register a cleanup
        atexit.register(self.cleanup)
        # adjust path for db_name
        self.db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + db_name
        
        try:
            self.connection = sqlite3.connect(db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
            # Create tables if they don't exist
            self.create_ban_table()
            self.create_threat_table()
            self.logger.info(f"Connected to database '{db_name}' successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while connecting to the database: {e}")
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
            self.logger.info("ban_table created or already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while creating ban_table: {e}")
            raise  # Re-raise the exception to notify higher-level code

    def create_threat_table(self):
        """Create the threat_table if it doesn't already exist."""
        create_threat_query = '''
        CREATE TABLE IF NOT EXISTS threat_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shortened_string CHAR(255),
            hit_count INTEGER,
            hazard_level CHAR(12),
            UNIQUE(shortened_string)
        )
        '''
        try:
            self.cursor.execute(create_threat_query)
            self.connection.commit()
            self.logger.info("threat_table created or already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while creating threat_table: {e}")
            raise  # Re-raise the exception to notify higher-level code

        
    #
    # Handle threat table
    #

    # a debugging method
    def reset_hazard_level(self):
        try:
            # Update all rows in the threat_table where hazard_level is 'no' and set it to 'unk'
            update_query = """
            UPDATE threat_table
            SET hazard_level = 'unk'
            WHERE hazard_level = 'no';
            """
            self.cursor.execute(update_query)
            self.connection.commit()
            print("Hazard levels updated successfully.")
        
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def insert_or_update_threat(self, shortened_string, hit_count, hazard_level):
        try:
            cursor = self.connection.cursor()
            # Insert new row or update existing one if shortened_string already exists
            query = '''
            INSERT INTO threat_table (shortened_string, hit_count, hazard_level)
            VALUES (?, ?, ?)
            ON CONFLICT(shortened_string) 
            DO UPDATE SET hit_count = hit_count + excluded.hit_count, 
                          hazard_level = excluded.hazard_level
            '''
            cursor.execute(query, (shortened_string, hit_count, hazard_level))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")

    def fetch_threat_level(self, shortened_string):
        try:
            cursor = self.connection.cursor()
            # Query to fetch hazard_level and hit_count based on shortened_string
            query = '''
            SELECT hit_count, hazard_level FROM threat_table WHERE shortened_string = ?
            '''
            cursor.execute(query, (shortened_string,))
            result = cursor.fetchone()  # Fetch one result
            if result:
                # If record exists, increment hit_count
                hit_count = result[0] + 1
                hazard_level = result[1]

                # Update hit_count
                update_query = '''
                UPDATE threat_table
                SET hit_count = ?
                WHERE shortened_string = ?
                '''
                cursor.execute(update_query, (hit_count, shortened_string))
                self.connection.commit()

                return (True, hazard_level)  # Return True and hazard_level
            else:
                return (False, None)  # Return False if not found
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
            return (False, None)
            
    def show_threats(self):
        try:
            cursor = self.connection.cursor()
            # Query to select all rows from the threat_table
            query = '''
            SELECT id, shortened_string, hit_count, hazard_level FROM threat_table
            '''
            cursor.execute(query)
            results = cursor.fetchall()  # Fetch all results
            if results:
                print(f"{'ID':<5} {'Hit Count':<10} {'Hazard Level':<15} {'Shortened String':<25}")
                print("-" * 60)
                for row in results:
                    print(f"{row[0]:<5} {row[2]:<10} {row[3]:<15} {row[1]:<25} ")
            else:
                print("No threats found in the table.")
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")

    #
    # Handle ban table
    #
    def add_or_update_ban(self, ip_addr, jail_name, minutes_until_ban_end):
        """Add a new ban or update an existing ban based on ip_address and jail."""
        # Parse and expand the IP address (IPv6 addresses to full form)
        try:
            ip_obj = ipaddress.ip_address(ip_addr)
            ip_addr = ip_obj.exploded  # Use the long form of the IP address
        except ValueError as e:
            self.logger.error(f"Invalid IP address '{ip_addr}': {e}")
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
                self.logger.info(f"Updated ban for IP {ip_addr} in jail '{jail_name}'.")
            else:
                # If the record does not exist, insert a new record
                insert_query = '''
                INSERT INTO ban_table (ip_address, jail, usage_count, ban_expire_time) 
                VALUES (?, ?, ?, ?)
                '''
                self.cursor.execute(insert_query, (ip_addr, jail_name, 1, ban_expire_time))
                self.connection.commit()
                self.logger.info(f"Added new ban for IP {ip_addr} in jail '{jail_name}'.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while adding/updating ban: {e}")
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
            self.logger.error(f"An error occurred while fetching expired records: {e}")
            raise  # Re-raise to notify higher-level code

        return expired_records

    def get_non_expired_records(self):
        """Return a list of expired records in the form [ip_addr, is_ipv6, jail]."""
        expired_records = []

        # Get the current time
        current_time = datetime.now()

        try:
            # Query for expired records (ban_expire_time < current_time)
            query = '''
            SELECT ip_address, jail, ban_expire_time FROM ban_table WHERE ban_expire_time >= ?
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
            self.logger.error(f"An error occurred while fetching expired records: {e}")
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
                self.logger.info(f"Found {len(records)} record(s):")
                for record in records:
                    ip_addr, jail = record[1], record[2]
                    try:
                        ip_obj = ipaddress.ip_address(ip_addr)
                        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
                        if is_ipv6:
                            ip_addr = ip_obj.compressed  # Shrink IPv6 address to its compressed form
                    except ValueError:
                        is_ipv6 = False
                    self.logger.info(
                        f"ID: {record[0]}, IP: {ip_addr}, Jail: {jail}, "
                        f"Usage Count: {record[3]}, Ban Expire Time: {record[4]}"
                    )
            else:
                self.logger.info("No matching records found.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while showing bans: {e}")
            raise  # Re-raise to notify higher-level code

    def remove_record(self, ip_addr, jail_name):
        """Remove a record from the ban_table based on ip_address and jail_name."""
        delete_query = '''
        DELETE FROM ban_table WHERE ip_address = ? AND jail = ?
        '''
        try:
            self.cursor.execute(delete_query, (ip_addr, jail_name))
            self.connection.commit()
            self.logger.info(f"Record for IP {ip_addr} in jail '{jail_name}' has been removed.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while removing record: {e}")
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
                self.logger.info(f"Found {len(records)} record(s):")
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
                    self.logger.info(
                        f"ID: {id}, IP: {ip_addr}, Jail: {jail}, Usage Count: {usage_count}, "
                        f"Ban Expire Time: {ban_expire_time} ({expired_status})"
                    )
            else:
                self.logger.info("No records found in the database.")
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred while showing the database: {e}")
            raise  # Re-raise to notify higher-level code


    def check_db_integrity(self):
        """
        Check the integrity of the SQLite database.
        
        Raises:
        DatabaseIntegrityError: If corruption is detected in the database.
        """
        db_path = self.db_name
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Run the integrity check
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()

            # Check if the integrity check passed
            if result[0] == "ok":
                print("Database is consistent.")
            else:
                raise DatabaseIntegrityError(f"Database corruption detected: {result[0]}")

        except sqlite3.Error as e:
            raise sqlite3.Error(f"SQLite error occurred: {e}")
        finally:
            # Close the connection
            if conn:
                conn.close()

# Example usage
#try:
#    check_db_integrity("/path/to/your-database.db")
#except DatabaseIntegrityError as e:
#    print(f"Integrity check failed: {e}")
#except sqlite3.Error as e:
#    print(f"SQLite error: {e}")

    def close(self):
        """Close the database connection and cursor."""
        if self.cursor:
            try:
                self.cursor.close()
                self.logger.info("Database cursor closed.")
                self.cursor = None  # Prevent further use
            except sqlite3.Error as e:
                self.logger.error(f"An error occurred while closing the cursor: {e}")
                raise
        
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.logger.info("Database connection closed.")
            except sqlite3.Error as e:
                self.logger.error(f"An error occurred while closing the database connection: {e}")
                raise  # Re-raise to notify higher-level code

#    def __del__(self):
#        """
#        Destructor method to close the database connection when the object is destroyed.
#        """
#        if hasattr(self, 'connection') and self.connection:
#            try:
#                self.connection.close()
#                logger.info("Database connection closed.")
#            except sqlite3.Error as e:
#                logger.error(f"An error occurred while closing the database connection: {e}")

    def cleanup(self):
        self.close()

if __name__ == "__main__":
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)
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
            logger.info("Waiting for the bans to expire...")
            import time
            time.sleep(70)  # Wait for over a minute

            # Get and log expired records
            expired_records = db.get_expired_records()
            if expired_records:
                logger.info("Expired records:")
                for record in expired_records:
                    logger.info(record)
            else:
                logger.info("No expired records.")

            # Show all bans again to reflect expirations
            db.show_database()

    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        # Explicitly close the database connection if it's still open
        # Note: Using context manager handles this, but this is a safety net
        try:
            if 'db' in locals() and db.connection:
                db.close()
        except Exception as e:
            logger.error(f"Error occurred while closing the database: {e}")



