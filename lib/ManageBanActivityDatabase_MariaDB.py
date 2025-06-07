
import os
import sys
import atexit
from datetime import datetime, timedelta
import logging
import mysql.connector
import traceback
import time

LOG_ID = "fail3ban"

class ManageBanActivityDatabase_MariaDB:
    def __init__(self, conn, log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)
        # Save conn
        self.conn = conn

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
        conn = self.conn
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

    def update_usage_count(self, ip_address):
        """Update the usage_count for the given IP address, or create it if it doesn't exist."""
        conn = self.conn
        cursor = conn.cursor()

        # Get the current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the query to either insert a new record or update if it exists
        query = '''
        INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
        VALUES (%s, 1, %s)
        ON DUPLICATE KEY UPDATE 
          usage_count = usage_count + 1,
          datetime_of_last_ban = VALUES(datetime_of_last_ban)
        '''

        if True:
            self.execute_with_retry(cursor, conn, query, (ip_address, current_time))
        else:
            # Execute the query with the IP address and current time
            cursor.execute(query, (ip_address, current_time))
        # Commit the changes
        conn.commit()
        cursor.close()
        return

        # TODO - Dead Code
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

    # Method to print active transactions
    def _show_active_transactions(self, conn):
        try:
            cursor = conn.cursor()

            # Query to get active transactions from the innodb_trx table
            query = """
            SELECT trx_id, trx_started, trx_state, trx_mysql_thread_id, trx_query 
            FROM information_schema.innodb_trx;
            """
            cursor.execute(query)
            transactions = cursor.fetchall()

            # Print out the transaction details
            print(f"{'Transaction ID':<20} {'Started':<30} {'State':<15} {'Thread ID':<10} {'Query':<50}")
            print("-" * 120)
            for trx in transactions:
                trx_id = trx[0]
                trx_started = trx[1]
                trx_state = trx[2] if trx[2] else 'None'
                trx_thread_id = trx[3] if trx[3] else 'None'
                trx_query = trx[4] if trx[4] else 'None'

                print(f"{trx_id:<20} {trx_started:<30} {trx_state:<15} {trx_thread_id:<10} {trx_query:<50}")

        except Exception as e:
            print(f"Failed to retrieve transactions: {e}")
        finally:
            cursor.close()
        
    # help debug locks
    def _show_processlist(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW PROCESSLIST")
            processlist = cursor.fetchall()

            # Display the process list
            print(f"{'Id':<6} {'User':<16} {'Host':<24} {'Db':<16} {'Command':<16} {'Time':<6} {'State':<16} {'Info':<16}")
            print("-" * 120)

            for process in processlist:
                # Handle None values to prevent format errors
                process_id = process[0] if process[0] is not None else 'NULL'
                user = process[1] if process[1] is not None else 'NULL'
                host = process[2] if process[2] is not None else 'NULL'
                db = process[3] if process[3] is not None else 'NULL'
                command = process[4] if process[4] is not None else 'NULL'
                time = process[5] if process[5] is not None else 'NULL'
                state = process[6] if process[6] is not None else 'NULL'
                info = process[7] if process[7] is not None else 'NULL'

                print(f"{process_id:<6} {user:<16} {host:<24} {db:<16} {command:<16} {time:<6} {state:<16} {info:<16}")

        except Exception as e:
            print(f"Failed to retrieve process list: {e}")
        finally:
            cursor.close()

    # Method to show detailed diagnostics (transactions, locks, open tables, etc.)
    def _show_detailed_diagnostics(self, conn):
        try:
            cursor = conn.cursor()

            # 1. SHOW ENGINE INNODB STATUS: Detailed InnoDB information, including locks and transactions
            cursor.execute("SHOW ENGINE INNODB STATUS")
            innodb_status = cursor.fetchone()
            print("\n==== INNODB STATUS ====")
            print(innodb_status[2])  # InnoDB status is in the third column

            # 2. Check for long-running transactions in information_schema
            print("\n==== RUNNING TRANSACTIONS ====")
            cursor.execute("""
                SELECT * 
                FROM information_schema.innodb_trx 
                WHERE trx_state = 'RUNNING'
            """)
            running_transactions = cursor.fetchall()
            if running_transactions:
                for trx in running_transactions:
                    print(f"Transaction ID: {trx[0]}, State: {trx[4]}, Time: {trx[6]}, Info: {trx[15]}")
            else:
                print("No long-running transactions found.")

            # 3. Information about currently held locks
            print("\n==== LOCKS ====")
            cursor.execute("SELECT * FROM information_schema.innodb_locks")
            locks = cursor.fetchall()
            if locks:
                for lock in locks:
                    print(f"Lock ID: {lock[0]}, Lock Mode: {lock[3]}, Lock Type: {lock[4]}, Locked Table: {lock[2]}")
            else:
                print("No locks found.")

            # 4. Open tables (check if many tables are open)
            print("\n==== OPEN TABLES ====")
            cursor.execute("SHOW STATUS LIKE 'Open_tables'")
            open_tables = cursor.fetchone()
            print(f"Open Tables: {open_tables[1]}")

            # 5. Check for the number of active connections
            print("\n==== THREADS CONNECTED ====")
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            threads_connected = cursor.fetchone()
            print(f"Threads Connected: {threads_connected[1]}")

        except Exception as e:
            print(f"Failed to retrieve detailed diagnostics: {e}")
        finally:
            cursor.close()
            
    # we will use this if we have to
    def execute_with_retry(self, cursor, conn, query, params, retries=3, delay=2):
        for attempt in range(retries):
            try:
                cursor.execute(query, params)
                conn.commit()
                print(f"execute_with_retry, completed on attempt {attempt} ...")
                return True
            except mysql.connector.errors.DatabaseError as e:
                print(f"execute_with_retry, received e.errno = {e.errno}")
                if e.errno == 1205:  # Lock wait timeout exceeded
                    self._show_processlist(conn)
                    self._show_detailed_diagnostics(conn)
                    self._show_active_transactions(conn)

                    if attempt < retries - 1:
                        print(f"execute_with_retry: sleeping {delay}, attempt = {attempt}")
                        time.sleep(delay)  # Wait before retrying
                    else:
                        # Out of retries
                        raise TimeoutError("Database Retries exhausted") from e
                else:
                    # Not error 1205
                    raise
                
        # If all retries are exhausted, raise the exception
        raise Exception("Database Retries exhausted")
            
    def update_time(self, ip_address):
        """Update the datetime_of_last_ban for the given IP address, or create it if it doesn't exist."""
        conn = self.conn
        cursor = conn.cursor()

        #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # mysql.connector will convert ???
        current_time = datetime.now()

        # Prepare the query to insert or update based on existence
        query = '''
        INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
        VALUES (%s, 1, %s)
          ON DUPLICATE KEY UPDATE 
          datetime_of_last_ban = VALUES(datetime_of_last_ban)
        '''

        # Execute the query in a single step
        if True:
            self.execute_with_retry(cursor, conn, query, (ip_address, current_time))
        else:               
            cursor.execute(query, (ip_address, current_time))
        conn.commit()
        cursor.close()
        return

        # This one will update the usage count if necessary too
        query = '''
        INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
        VALUES (%s, 1, %s)
        ON DUPLICATE KEY UPDATE 
          usage_count = usage_count + 1,
          datetime_of_last_ban = VALUES(datetime_of_last_ban)
        '''

        # TODO - dead code
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

    def show(self):
        """Display all records from the activity_table along with the age in days."""
        conn = self.conn
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

    def scan_for_expired(self, days_old=30):
        """Scan for records older than the specified number of days and delete them."""
        conn = self.conn
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

    def delete_record(self, record_id):
        """Delete a record from the activity_table by its ID."""
        conn = self.conn
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

    # handle any wacko date format, in any event, return proper datetime we can use in comparison
    def parse_date(self, date_input):
        if isinstance(date_input, datetime):
            # If it's already a datetime object, return it
            return date_input
        elif isinstance(date_input, str):
            try:
                # Try parsing the string with fractional seconds
                return datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    # If fractional seconds are not present, parse without them
                    return datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError("Unsupported date format")
        else:
            raise TypeError("Input must be a string or datetime object")
    
    def is_in_window(self, ip_addr, N=20):
        """Check if the record for the given IP address exists and is within N minutes old."""
        print(f"Checking if IP address {ip_addr} is within {N} minutes window...")

        conn = self.conn
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id, usage_count, datetime_of_last_ban FROM activity_table WHERE ip_address = %s", (ip_addr,))
            record = cursor.fetchone()

            if record:
                last_ban_time_str = record[2]      # -1 or None means forever
                new_usage_count = record[1] + 1
                current_date_time = datetime.now()

                # update the usage count in the activity table
                cursor.execute('''
                UPDATE activity_table
                SET datetime_of_last_ban = %s, usage_count = %s
                WHERE ip_address = %s
                ''', (current_date_time, new_usage_count, ip_addr))

                last_ban_time = self.parse_date(last_ban_time_str)
                
                time_difference = datetime.now() - last_ban_time

                if time_difference.total_seconds() <= N * 60:
                    print(f"IP {ip_addr} is within the {N} minutes window.")
                    return True
                else:
                    print(f"IP {ip_addr} is not within the {N} minutes window.")
            else:
                cursor.execute('''
                INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
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

    def _create_not_bad_get_string(self):
        """Create the not_bad_get_string_table if it doesn't exist."""
        conn = self.conn
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

    def put_not_bad_get_string(self, ip_address, not_bad_get_string):
        """Insert or update a record in not_bad_get_string_table."""
        conn = self.conn
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

    def show_not_bad_get_string_table(self):
        """Display all records in not_bad_get_string_table."""
        conn = self.conn
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

    def get_activity_records(self, callback):
        """
        Fetch one activity record at a time and pass it to the callback function.

        Args:
            callback (function): A function to process each record.
        """
        # Borrow a connection from the pool
        conn = self.conn
        cursor = conn.cursor()

        # Define the query to fetch records from activity_table
        query = '''
        SELECT ip_address, usage_count, datetime_of_last_ban FROM activity_table
        '''
        cursor.execute(query)

        # Fetch records one by one and pass them to the callback
        while True:
            record = cursor.fetchone()
            if record is None:
                break  # No more records

            ip_addr, usage_count, datetime_of_last_ban = record

            # Pass the processed record to the callback function
            callback([ip_addr, usage_count, datetime_of_last_ban])

        # Cleanup
        cursor.close()
            
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

