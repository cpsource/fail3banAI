
import os
import sys
import sqlite3
import atexit
from datetime import datetime, timedelta
import logging

LOG_ID = "fail3ban"

class ManageBanActivityDatabase:
    def __init__(self, database_connection_pool, log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        # save off connection pool
        self.database_connection_pool = database_connection_pool

        # Register cleanup function to close the database connection
        atexit.register(self.cleanup)
        
        try:
            self.create_activity_table()
            self.logger.info("Created activity table successfully.")
        except sqlite3.Error as ex:
            self.logger.error(f"Created activity table returned {ex}")
            raise  # Re-raise the exception to notify higher-level code

    def create_activity_table(self):
        """Create the activity_table and the index on ip_address if they don't exist."""

        # borrow a conn
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()
    
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_table';")
        if cursor.fetchone():
            pass
            #print("Table 'activity_table' already exists.")
        else:
            # Create the table if it does not exist
            create_table_query = '''
            CREATE TABLE activity_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address CHAR(40) NOT NULL UNIQUE,
            usage_count INTEGER DEFAULT 1,
            datetime_of_last_ban TEXT
            );
            '''
            try:
                cursor.execute(create_table_query)
                conn.commit()
                print("Activity table created.")
            except sqlite3.Error as e:
                print(f"Error creating table: {e}")

        # Check if the index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_ip_address';")
        if cursor.fetchone():
            pass
            #print("Index 'idx_ip_address' already exists.")
        else:
            # Create the index if it does not exist
            create_index_query = "CREATE INDEX idx_ip_address ON activity_table (ip_address);"
            try:
                cursor.execute(create_index_query)
                conn.commit()
                print("Index 'idx_ip_address' created.")
            except sqlite3.Error as er:
                print(f"Error creating index: {er}")

        # return the connection we had on loan
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def update_usage_count(self, ip_address):
        """Update the usage_count for the given IP address, or create it if it doesn't exist."""
        # Borrow a connection from the pool
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Check if the IP address exists
        cursor.execute("SELECT usage_count FROM activity_table WHERE ip_address = ?", (ip_address,))
        record = cursor.fetchone()

        if record:
            # If the IP address exists, increment the usage_count
            new_count = record[0] + 1
            update_query = '''
            UPDATE activity_table
            SET usage_count = ?
            WHERE ip_address = ?
            '''
            cursor.execute(update_query, (new_count, ip_address))
            self.logger.debug(f"Incremented usage_count for {ip_address} to {new_count}")
        else:
            # If the IP address doesn't exist, insert a new record
            insert_query = '''
            INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
            VALUES (?, 1, ?)
            '''
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_query, (ip_address, current_time))
            self.logger.info(f"Inserted new record for {ip_address} with usage_count = 1 and datetime_of_last_ban = {current_time}")

        # Commit the changes
        conn.commit()

        # Return the connection to the pool
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    # deprecated TODO
    def zinsert_or_update_activity(self, ip_address):
        """Insert a new record or update the existing record for the given IP address."""
        # borrow a conn
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()
        
        # Get the current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the IP address already exists
        cursor.execute("SELECT id, usage_count FROM activity_table WHERE ip_address = ?", (ip_address,))
        record = cursor.fetchone()
        
        if record:
            # If the IP address exists, update the record (increment usage_count and update datetime_of_last_ban)
            usage_count = record[1] + 1
            update_query = '''
            UPDATE activity_table
            SET usage_count = ?
            WHERE ip_address = ?
            '''
            cursor.execute(update_query, (usage_count, ip_address))
            self.logger.debug(f"Updated record for {ip_address}, usage_count incremented to {usage_count}")
        else:
            # If the IP address doesn't exist, insert a new record
            insert_query = '''
            INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
            VALUES (?, 1, ?)
            '''
            cursor.execute(insert_query, (ip_address, current_time))
            self.logger.debug(f"Inserted new record for {ip_address}")
        
        # Commit the changes
        conn.commit()

        # return the connection we had on loan
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def update_time(self, ip_address):
        """Update the datetime_of_last_ban for the given IP address, or create it if it doesn't exist."""
        # Borrow a connection from the pool
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Get the current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the IP address exists
        cursor.execute("SELECT id FROM activity_table WHERE ip_address = ?", (ip_address,))
        record = cursor.fetchone()

        if record:
            # If the IP address exists, update the datetime_of_last_ban
            update_query = '''
            UPDATE activity_table
            SET datetime_of_last_ban = ?
            WHERE ip_address = ?
            '''
            cursor.execute(update_query, (current_time, ip_address))
            self.logger.debug(f"Updated datetime_of_last_ban for {ip_address} to {current_time}")
        else:
            # If the IP address doesn't exist, insert a new record
            insert_query = '''
            INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
            VALUES (?, 1, ?)
            '''
            cursor.execute(insert_query, (ip_address, current_time))
            self.logger.info(f"Inserted new record for {ip_address} with datetime_of_last_ban = {current_time}")

        # Commit the changes
        conn.commit()

        # Return the connection to the pool
        cursor.close()
        self.database_connection_pool.return_connection(conn)
        
    def show(self):
        """Display all records from the activity_table along with the age in days."""

        # borrow a conn
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activity_table")
        records = cursor.fetchall()

        if records:
            print(f"{'ID':<5} {'IP Address':<40} {'Usage Count':<12} {'Last Ban Time':<20} {'Age (days)'}")
            print("=" * 90)
            for row in records:
                # Calculate the age of the record in days
                last_ban_time = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                age_in_days = (datetime.now() - last_ban_time).days
                print(f"{row[0]:<5} {row[1]:<40} {row[2]:<12} {row[3]:<20} {age_in_days}")
        else:
            print("No records found in the activity table.")

        # return the connection we had on loan
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def scan_for_expired(self, days_old=30):
        """Scan for records older than the specified number of days and delete them."""

        # borrow a conn
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Calculate the expiration cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Select records older than the cutoff date
        cursor.execute("SELECT id, ip_address, datetime_of_last_ban FROM activity_table WHERE datetime_of_last_ban < ?", (cutoff_date,))
        expired_records = cursor.fetchall()
        
        if expired_records:
            print(f"Found {len(expired_records)} records older than {days_old} days.")
            for record in expired_records:
                print(f"Deleting record ID {record[0]}, IP {record[1]}, Last Ban {record[2]}")
                self.delete_record(record[0])
        else:
            print(f"No records older than {days_old} days found.")

        # return the connection we had on loan
        cursor.close()
        self.database_connection_pool.return_connection(conn)
            
    def delete_record(self, record_id):
        """Delete a record from the activity_table by its ID."""

        # borrow a conn
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM activity_table WHERE id = ?", (record_id,))
            conn.commit()
            print(f"Deleted record ID {record_id}")
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")

        # return the connection we had on loan
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def is_in_window(self, ip_addr, N=15):
        """Check if the record for the given IP address exists and is within N minutes old."""

        print(f"Checking if IP address {ip_addr} is within {N} minutes window...")

        # Borrow a connection from the pool
        conn = self.database_connection_pool.get_connection()
        if conn is None:
            print("Failed to retrieve a connection from the pool.")
            return False

        cursor = conn.cursor()

        try:
            # Query the record for the given IP address
            print(f"Executing SQL query to retrieve last ban time for IP: {ip_addr}")
            cursor.execute("SELECT id, usage_count, datetime_of_last_ban FROM activity_table WHERE ip_address = ?", (ip_addr,))
            record = cursor.fetchone()

            return_status = False
            if record:
                last_ban_time_str = record[2]
                new_usage_count = record[1] + 1
                
                print(f"Record found for IP {ip_addr}, new_usage_count = {new_usage_count} last ban time: {last_ban_time_str}")
                # Get the current date and time
                current_date_time = datetime.now()

                # Update the datetime_of_last_ban and usage_count
                update_query = '''
                UPDATE activity_table
                SET datetime_of_last_ban = ?, usage_count = ?
                WHERE ip_address = ?
                '''
                cursor.execute(update_query, (current_date_time, new_usage_count, ip_addr))

                # Convert the datetime_of_last_ban to a datetime object
                try:
                    last_ban_time = datetime.strptime(last_ban_time_str, '%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing datetime: {e}")
                    return False

                time_difference = datetime.now() - last_ban_time
                print(f"Time difference for IP {ip_addr}: {time_difference.total_seconds()} seconds")

                # Check if the difference is less than or equal to N minutes
                if time_difference.total_seconds() <= N * 60:
                    print(f"IP {ip_addr} is within the {N} minutes window.")
                    return_status = True
                else:
                    print(f"IP {ip_addr} is not within the {N} minutes window.")
            else:
                # If the IP address doesn't exist, insert a new record
                current_date_time = datetime.now()
                insert_query = '''
                INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
                VALUES (?, 1, ?)
                '''
                cursor.execute(insert_query, (ip_addr, current_date_time))
                self.logger.debug(f"Inserted new record for {ip_addr}")
                return_status = True
                
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            return_status = False

        finally:
            # Return the connection to the pool
            cursor.close()
            self.database_connection_pool.return_connection(conn)
            ##print(f"Connection for IP {ip_addr} returned to the pool.")

        return return_status
            
    # do any cleanup
    def cleanup(self):
        pass

    @staticmethod
    def print_help():
        """Print the help message for the command-line interface."""
        print("Usage:")
        print("  show                - Display all records")
        print("  delete <record-id>  - Delete a record by its ID")
        print("  expired <days-old>  - Scan for and delete records older than <days-old>")
        print("  insert <ip_address> - Adds or updates a record")
        print("  help                - Show this help message")
        
# Main function to handle command-line arguments
if __name__ == "__main__":

    import SQLiteConnectionPool

    db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/fail3ban_server.db"
    database_connection_pool = SQLiteConnectionPool.SQLiteConnectionPool(db_name)
    manage_ban = ManageBanActivityDatabase(database_connection_pool)

    # Check if any arguments are passed
    if len(sys.argv) < 2:
        print("No command provided. Use 'help' for usage instructions.")
    else:
        command = sys.argv[1].lower()

        if command == "show":
            manage_ban.show()

        elif command == "delete":
            if len(sys.argv) != 3:
                print("Error: 'delete' requires a record ID.")
            else:
                try:
                    record_id = int(sys.argv[2])
                    manage_ban.delete_record(record_id)
                except ValueError:
                    print("Error: Record ID must be a valid integer.")

        elif command == "expired":
            if len(sys.argv) != 3:
                print("Error: 'expired' requires the number of days.")
            else:
                try:
                    days_old = int(sys.argv[2])
                    manage_ban.scan_for_expired(days_old)
                except ValueError:
                    print("Error: Days must be a valid integer.")

        elif command == "insert":
            if len(sys.argv) != 3:
                print("Error: 'insert' requires an IP address.")
            else:
                ip_address = sys.argv[2]
                manage_ban.insert_or_update_activity(ip_address)

        elif command == "help":
            manage_ban.print_help()

        else:
            print(f"Unknown command: {command}. Use 'help' for usage instructions.")

        database_connection_pool.shutdown()            

