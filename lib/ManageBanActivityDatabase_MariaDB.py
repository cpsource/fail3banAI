
import os
import sys
import atexit
from datetime import datetime, timedelta
import logging
import mysql.connector
import traceback

LOG_ID = "fail3ban"

class ManageBanActivityDatabase_MariaDB:
    def __init__(self, database_connection_pool, log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        # Save off connection pool
        self.database_connection_pool = database_connection_pool

        # Register cleanup function to close the database connection
        atexit.register(self.cleanup)
        
        try:
            self._create_activity_table()
            self.logger.info("Created activity table successfully.")
        except mysql.connector.Error as ex:
            self.logger.error(f"Created activity table returned {ex}")
            # dump the stack
            traceback.print_exc()
            raise  # Re-raise the exception to notify higher-level code

        try:
            self._create_not_bad_get_string()
            self.logger.info("Created not bad get string table successfully.")
        except mysql.connector.Error as ex:
            self.logger.error(f"Created not bad get string table returned {ex}")
            # dump the stack
            traceback.print_exc()
            raise  # Re-raise the exception to notify higher-level code
        
    def _create_activity_table(self):
        """Create the activity_table and the index on ip_address if they don't exist."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute("SHOW TABLES LIKE 'activity_table';")
        if cursor.fetchone():
            pass
        else:
            # Create the table if it does not exist
            create_table_query = '''
            CREATE TABLE activity_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address CHAR(40) NOT NULL UNIQUE,
                usage_count INT DEFAULT 1,
                datetime_of_last_ban DATETIME
            );
            '''
            try:
                cursor.execute(create_table_query)
                conn.commit()
                print("Activity table created.")
            except mysql.connector.Error as e:
                # dump the stack
                traceback.print_exc()
                print(f"Error creating table: {e}")

        # Check if the index exists
        cursor.execute("SHOW INDEX FROM activity_table WHERE Key_name = 'idx_ip_address';")
        if cursor.fetchone():
            pass
        else:
            # Create the index if it does not exist
            create_index_query = "CREATE INDEX idx_ip_address ON activity_table (ip_address);"
            try:
                cursor.execute(create_index_query)
                conn.commit()
                print("Index 'idx_ip_address' created.")
            except mysql.connector.Error as er:
                print(f"Error creating index: {er}")
                # dump the stack
                traceback.print_exc()

        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def update_usage_count(self, ip_address):
        """Update the usage_count for the given IP address, or create it if it doesn't exist."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Check if the IP address exists
        cursor.execute("SELECT usage_count FROM activity_table WHERE ip_address = %s", (ip_address,))
        record = cursor.fetchone()

        if record:
            # If the IP address exists, increment the usage_count
            new_count = record[0] + 1
            update_query = '''
            UPDATE activity_table
            SET usage_count = %s
            WHERE ip_address = %s
            '''
            cursor.execute(update_query, (new_count, ip_address))
            self.logger.debug(f"Incremented usage_count for {ip_address} to {new_count}")
        else:
            # If the IP address doesn't exist, insert a new record
            insert_query = '''
            INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
            VALUES (%s, 1, %s)
            '''
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_query, (ip_address, current_time))
            self.logger.info(f"Inserted new record for {ip_address} with usage_count = 1 and datetime_of_last_ban = {current_time}")

        # Commit the changes
        conn.commit()
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def update_time(self, ip_address):
        """Update the datetime_of_last_ban for the given IP address, or create it if it doesn't exist."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the IP address exists
        cursor.execute("SELECT id FROM activity_table WHERE ip_address = %s", (ip_address,))
        record = cursor.fetchone()

        if record:
            # If the IP address exists, update the datetime_of_last_ban
            update_query = '''
            UPDATE activity_table
            SET datetime_of_last_ban = %s
            WHERE ip_address = %s
            '''
            cursor.execute(update_query, (current_time, ip_address))
            self.logger.debug(f"Updated datetime_of_last_ban for {ip_address} to {current_time}")
        else:
            # If the IP address doesn't exist, insert a new record
            insert_query = '''
            INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
            VALUES (%s, 1, %s)
            '''
            cursor.execute(insert_query, (ip_address, current_time))
            self.logger.info(f"Inserted new record for {ip_address} with datetime_of_last_ban = {current_time}")

        conn.commit()
        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def show(self):
        """Display all records from the activity_table along with the age in days."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activity_table")
        records = cursor.fetchall()

        if records:
            print(f"{'ID':<5} {'IP Address':<40} {'Usage Count':<12} {'Last Ban Time':<20} {'Age (days)'}")
            print("=" * 90)
            for row in records:
                last_ban_time = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                age_in_days = (datetime.now() - last_ban_time).days
                print(f"{row[0]:<5} {row[1]:<40} {row[2]:<12} {row[3]:<20} {age_in_days}")
        else:
            print("No records found in the activity table.")

        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def scan_for_expired(self, days_old=30):
        """Scan for records older than the specified number of days and delete them."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("SELECT id, ip_address, datetime_of_last_ban FROM activity_table WHERE datetime_of_last_ban < %s", (cutoff_date,))
        expired_records = cursor.fetchall()

        if expired_records:
            print(f"Found {len(expired_records)} records older than {days_old} days.")
            for record in expired_records:
                print(f"Deleting record ID {record[0]}, IP {record[1]}, Last Ban {record[2]}")
                self.delete_record(record[0])
        else:
            print(f"No records older than {days_old} days found.")

        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def delete_record(self, record_id):
        """Delete a record from the activity_table by its ID."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM activity_table WHERE id = %s", (record_id,))
            conn.commit()
            print(f"Deleted record ID {record_id}")
        except mysql.connector.Error as e:
            print(f"Error deleting record: {e}")
            # dump the stack
            traceback.print_exc()

        cursor.close()
        self.database_connection_pool.return_connection(conn)

    def is_in_window(self, ip_addr, N=20):
        """Check if the record for the given IP address exists and is within N minutes old."""
        print(f"Checking if IP address {ip_addr} is within {N} minutes window...")

        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id, usage_count, datetime_of_last_ban FROM activity_table WHERE ip_address = %s", (ip_addr,))
            record = cursor.fetchone()

            if record:
                last_ban_time_str = record[2]
                new_usage_count = record[1] + 1
                current_date_time = datetime.now()

                cursor.execute('''
                UPDATE activity_table
                SET datetime_of_last_ban = %s, usage_count = %s
                WHERE ip_address = %s
                ''', (current_date_time, new_usage_count, ip_addr))

                try:
                    # Try to parse with fractional seconds
                    last_ban_time = datetime.strptime(last_ban_time_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    # If fractional seconds are not present, parse without them
                    last_ban_time = datetime.strptime(last_ban_time_str, '%Y-%m-%d %H:%M:%S')

                time_difference = datetime.now() - last_ban_time

                if time_difference.total_seconds() <= N * 60:
                    print(f"IP {ip_addr} is within the {N} minutes window.")
                    return True
                else:
                    print(f"IP {ip_addr} is not within the {N} minutes window.")
            else:
                cursor.execute('''
                INSERT INTO

 activity_table (ip_address, usage_count, datetime_of_last_ban)
                VALUES (%s, 1, %s)
                ''', (ip_addr, datetime.now()))
                self.logger.debug(f"Inserted new record for {ip_addr}")
                return False

        except mysql.connector.Error as e:
            print(f"SQL Error: {e}")
            # dump the stack
            traceback.print_exc()
            return False

        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def _create_not_bad_get_string(self):
        """Create the not_bad_get_string_table if it doesn't exist."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute("SHOW TABLES LIKE 'not_bad_get_string_table';")
        if cursor.fetchone():
            pass
        else:
            # Create the table if it does not exist
            create_table_query = '''
            CREATE TABLE not_bad_get_string_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address CHAR(39) NOT NULL,
                not_bad_get CHAR(32) NOT NULL,
                examined BOOLEAN DEFAULT FALSE
            );
            '''
            try:
                cursor.execute(create_table_query)
                conn.commit()
                print("not_bad_get_string_table created.")
            except mysql.connector.Error as e:
                print(f"Error creating table: {e}")
                # dump the stack
                traceback.print_exc()
            finally:
                cursor.close()
                self.database_connection_pool.return_connection(conn)

    def put_not_bad_get_string(self, ip_address, not_bad_get_string):
        """Insert or update a record in not_bad_get_string_table."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        insert_query = '''
        INSERT INTO not_bad_get_string_table (ip_address, not_bad_get, examined)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        not_bad_get = VALUES(not_bad_get), examined = FALSE;
        '''
        try:
            cursor.execute(insert_query, (ip_address, not_bad_get_string, False))
            conn.commit()
            print(f"Record for {ip_address} added/updated.")
        except mysql.connector.Error as e:
            print(f"Error inserting/updating record: {e}")
            # dump the stack
            traceback.print_exc()
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def show_not_bad_get_string_table(self):
        """Display all records in not_bad_get_string_table."""
        conn = self.database_connection_pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM not_bad_get_string_table;")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No records found.")
        except mysql.connector.Error as e:
            print(f"Error fetching records: {e}")
            # dump the stack
            traceback.print_exc()
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)
            
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


if __name__ == "__main__":
    import MariaDBConnectionPool  # Update your connection pool class

    database_connection_pool = MariaDBConnectionPool.MariaDBConnectionPool()
    manage_ban = ManageBanActivityDatabase_Mariadb(database_connection_pool)

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
                    # dump the stack
                    traceback.print_exc()

        elif command == "expired":
            if len(sys.argv) != 3:
                print("Error: 'expired' requires the number of days.")
            else:
                try:
                    days_old = int(sys.argv[2])
                    manage_ban.scan_for_expired(days_old)
                except ValueError:
                    print("Error: Days must be a valid integer.")
                    # dump the stack
                    traceback.print_exc()

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

