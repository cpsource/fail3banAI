import os
import sys
import sqlite3
import atexit
from datetime import datetime
import logging

LOG_ID = "fail3ban"

class ManageBanActivity:
    def __init__(self, db_name='fail3ban_server.db', log_id=LOG_ID):
        # Obtain logger
        self.logger = logging.getLogger(log_id)

        # adjust path for db_name
        self.db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + db_name
        self.conn = None

        # Register cleanup function to close the database connection
        atexit.register(self.cleanup)
        
        try:
            self.connect_db()
            self.create_activity_table()
            self.logger.info(f"Connected to database '{db_name}' successfully.")
        except sqlite3.Error as ex:
            self.logger.error(f"An error occurred while connecting to the database: {ex}")
            raise  # Re-raise the exception to notify higher-level code
        
    def connect_db(self):
        """Connect to the SQLite database, creating it if necessary."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            print(f"Connected to database {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_activity_table(self):
        """Create the activity_table and the index on ip_address if they don't exist."""
        cursor = self.conn.cursor()
    
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
                self.conn.commit()
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
                self.conn.commit()
                print("Index 'idx_ip_address' created.")
            except sqlite3.Error as er:
                print(f"Error creating index: {er}")
            
    def insert_or_update_activity(self, ip_address):
        """Insert a new record or update the existing record for the given IP address."""
        cursor = self.conn.cursor()
        
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
            SET usage_count = ?, datetime_of_last_ban = ?
            WHERE ip_address = ?
            '''
            cursor.execute(update_query, (usage_count, current_time, ip_address))
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
        self.conn.commit()

    def show(self):
        """Display all records from the activity_table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM activity_table")
        records = cursor.fetchall()
        
        if records:
            print(f"{'ID':<5} {'IP Address':<40} {'Usage Count':<12} {'Last Ban Time'}")
            print("=" * 70)
            for row in records:
                print(f"{row[0]:<5} {row[1]:<40} {row[2]:<12} {row[3]}")
        else:
            print("No records found in the activity table.")

    def scan_for_expired(self, days_old=30):
        """Scan for records older than the specified number of days and delete them."""
        cursor = self.conn.cursor()

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
    
    def delete_record(self, record_id):
        """Delete a record from the activity_table by its ID."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM activity_table WHERE id = ?", (record_id,))
            self.conn.commit()
            print(f"Deleted record ID {record_id}")
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")
            
    # do any cleanup
    def cleanup(self):
        """Cleanup function to close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

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
    manage_ban = ManageBanActivity()

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
            ManageBanActivity.print_help()

        else:
            print(f"Unknown command: {command}. Use 'help' for usage instructions.")


