import os
import mysql.connector
from datetime import datetime, timedelta
import ipaddress
import logging
import atexit
import traceback

LOG_ID = "fail3ban"

class Maria_DB:

    def __init__(self, database_connection_pool, log_id=LOG_ID):
        """
        Initializes the database connection pool.
        """
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        # Register a cleanup function
        atexit.register(self.cleanup)
        # Save our pool
        self.database_connection_pool = database_connection_pool
        
        try:
            # Create tables if they don't exist
            self._create_ban_table()
            self._create_threat_table()
            self.logger.info("Created ban and threat tables successfully.")
        except mysql.connector.Error as e:
            self.logger.error(f"An error occurred while creating ban and threat tables: {e}")
            # dump the stack
            traceback.print_exc()
            raise  # Re-raise the exception to notify higher-level code

    def _create_ban_table(self):
        """Create the ban_table if it doesn't already exist."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS ban_table (
            id INT PRIMARY KEY AUTO_INCREMENT,
            ip_address CHAR(40),
            jail CHAR(100),
            usage_count INT,
            ban_expire_time DATETIME NULL,
            UNIQUE(ip_address, jail)
        )
        '''
        try:
            cursor.execute(create_table_query)
            conn.commit()
            self.logger.info("ban_table created or already exists.")
        except mysql.connector.Error as e:
            self.logger.error(f"An error occurred while creating ban_table: {e}")
            # dump the stack
            traceback.print_exc()
            raise  # Re-raise the exception to notify higher-level code
        finally:
            # Return the connection we had on loan
            cursor.close()
            self.database_connection_pool.return_connection(conn)
            
    def _create_threat_table(self):
        """Create the threat_table if it doesn't already exist."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        create_threat_query = '''
        CREATE TABLE IF NOT EXISTS threat_table (
            id INT PRIMARY KEY AUTO_INCREMENT,
            shortened_string CHAR(255),
            hit_count INT,
            hazard_level CHAR(12),
            UNIQUE(shortened_string)
        )
        '''
        try:
            cursor.execute(create_threat_query)
            conn.commit()
            self.logger.info("threat_table created or already exists.")
        except mysql.connector.Error as e:
            self.logger.error(f"An error occurred while creating threat_table: {e}")
            # dump the stack
            traceback.print_exc()
            raise  # Re-raise the exception to notify higher-level code
        finally:
            # Return the connection we had on loan
            cursor.close()
            self.database_connection_pool.return_connection(conn)
            
    #
    # Handle threat table
    #

    def reset_hazard_level(self):
        """Reset hazard_level to 'unk' for rows with hazard_level = 'no'."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            update_query = """
            UPDATE threat_table
            SET hazard_level = 'unk'
            WHERE hazard_level = 'no';
            """
            cursor.execute(update_query)
            conn.commit()
            self.logger.debug("Hazard levels updated successfully.")
        except mysql.connector.Error as e:
            self.logger.error(f"An error occurred: {e}")
            # dump the stack
            traceback.print_exc()
            conn.rollback()
        finally:
            # Return the connection we had on loan
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def insert_or_update_threat(self, shortened_string, hit_count, hazard_level):
        """Insert or update a threat in the threat_table."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            query = '''
            INSERT INTO threat_table (shortened_string, hit_count, hazard_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE hit_count = hit_count + VALUES(hit_count),
                                    hazard_level = VALUES(hazard_level)
            '''
            cursor.execute(query, (shortened_string, hit_count, hazard_level))
            conn.commit()
        except mysql.connector.Error as e:
            self.logger.error(f"Error occurred: {e}")
            # dump the stack
            traceback.print_exc()
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def fetch_threat_level(self, shortened_string):
        """Fetch the threat level and hit count for a given shortened_string."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            query = '''
            SELECT hit_count, hazard_level FROM threat_table WHERE shortened_string = %s
            '''
            cursor.execute(query, (shortened_string,))
            result = cursor.fetchone()

            if result:
                hit_count = result[0] + 1
                hazard_level = result[1]

                # Update hit_count
                update_query = '''
                UPDATE threat_table
                SET hit_count = %s
                WHERE shortened_string = %s
                '''
                cursor.execute(update_query, (hit_count, shortened_string))
                conn.commit()

                return (True, hazard_level)
            else:
                return (False, None)
        except mysql.connector.Error as e:
            self.logger.error(f"Error occurred: {e}")
            # dump the stack
            traceback.print_exc()
            return (False, None)
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def show_threats(self):
        """Show all records from the threat_table."""

        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            query = '''
            SELECT id, shortened_string, hit_count, hazard_level FROM threat_table
            '''
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                print(f"{'ID':<5} {'Hit Count':<10} {'Hazard Level':<15} {'Shortened String':<25}")
                print("-" * 60)
                for row in results:
                    print(f"{row[0]:<5} {row[2]:<10} {row[3]:<15} {row[1]:<25}")
            else:
                print("No threats found in the table.")
        except mysql.connector.Error as e:
            self.logger.error(f"Error occurred: {e}")
            # dump the stack
            traceback.print_exc()
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    #
    # Handle ban table
    #
    def add_or_update_ban(self, ip_addr, jail_name='n/a', minutes_until_ban_end):
        """Add or update a ban record in the ban_table."""
        
        # Borrow a connection
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Parse and expand the IP address (IPv6 addresses to full form)
        try:
            ip_obj = ipaddress.ip_address(ip_addr)
            ip_addr = ip_obj.exploded  # Use the long form of the IP address
        except ValueError as e:
            self.logger.error(f"Invalid IP address '{ip_addr}': {e}")
            traceback.print_exc()
            raise

        # Calculate new ban expiration time
        if minutes_until_ban_end is None or minutes_until_ban_end == -1:
            # Infinite ban: set ban_expire_time to NULL
            ban_expire_time = None
            self.logger.info(f"Setting infinite ban for IP {ip_addr} in jail '{jail_name}'.")
        else:
            # Set regular ban expiration time
            ban_expire_time = datetime.now() + timedelta(minutes=minutes_until_ban_end)

        try:
            select_query = '''
            SELECT id, usage_count FROM ban_table WHERE ip_address = %s AND jail = %s
            '''
            cursor.execute(select_query, (ip_addr, jail_name))
            record = cursor.fetchone()

            if record:
                # Update an existing ban
                update_query = '''
                UPDATE ban_table 
                SET usage_count = usage_count + 1, ban_expire_time = %s 
                WHERE ip_address = %s AND jail = %s
                '''
                cursor.execute(update_query, (ban_expire_time, ip_addr, jail_name))
                conn.commit()
                self.logger.info(f"Updated ban for IP {ip_addr} in jail '{jail_name}'.")
            else:
                # Insert a new ban
                insert_query = '''
                INSERT INTO ban_table (ip_address, jail, usage_count, ban_expire_time) 
                VALUES (%s, %s, %s, %s)
                '''
                cursor.execute(insert_query, (ip_addr, jail_name, 1, ban_expire_time))
                conn.commit()
                self.logger.info(f"Added new ban for IP {ip_addr} in jail '{jail_name}'.")
        except mysql.connector.Error as e:
            self.logger.error(f"An error occurred while adding/updating ban: {e}")
            traceback.print_exc()
            raise
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def is_banned_for_life(self, ip_address):
        """
        Check if an IP address is banned for life (ban_expire_time is NULL).

        Args:
            ip_address (str): The IP address to check.

        Returns:
            bool: True if banned for life (ban_expire_time is NULL), 
                  False if not banned for life,
                  None if the IP address is not in the database.
        """
        conn = None
        try:
            # Borrow a connection from the pool
            conn = self.database_connection_pool.get_connection()
            cursor = conn.cursor()

            # Query to check if the IP address is banned for life (ban_expire_time is NULL)
            query = '''
            SELECT ban_expire_time FROM ban_table WHERE ip_address = %s
            '''
            cursor.execute(query, (ip_address,))
            record = cursor.fetchone()

            if record is None:
                # IP address is not found in the database
                return None

            ban_expire_time = record[0]

            # If ban_expire_time is NULL, the IP address is banned for life
            if ban_expire_time is None:
                return True
            else:
                return False

        except mysql.connector.Error as e:
            print(f"Error occurred while checking the ban: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                self.database_connection_pool.return_connection(conn)

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

    def remove_record(self, ip_addr):
        """Remove a record from the ban_table based on ip_address and jail_name."""
        delete_query = '''
        DELETE FROM ban_table WHERE ip_address = %s
        '''
        self.cursor.execute(delete_query, (ip_addr,))
        self.connection.commit()
        print(f"Record for IP {ip_addr} in jail {jail_name} has been removed.")
                
    def cleanup(self):
        pass
