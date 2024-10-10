import mysql.connector
import os
import sys

class CreateIPResponseTable:
    def __init__(self, conn):
        self.conn = conn
        self.create_table()
        self.create_index()

    def create_table(self):
        # SQL query to create the ip_responses table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ip_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL UNIQUE,  -- Unique IP address
            response TEXT NOT NULL,                  -- Response data (JSON or plain text)
            ref_cnt INT DEFAULT 1,                   -- Reference count, initialized to 1
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        # Execute the create table query
        cursor = self.conn.cursor()
        cursor.execute(create_table_sql)
        self.conn.commit()
        cursor.close()

    def create_index(self):
        # SQL query to create an index on ip_address for speed
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_ip_address ON ip_responses (ip_address);
        """
        # Execute the create index query
        cursor = self.conn.cursor()
        cursor.execute(create_index_sql)
        self.conn.commit()
        cursor.close()

# Usage example:
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
    CreateIPResponseTable(conn)

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()

