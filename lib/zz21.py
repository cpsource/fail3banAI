import mysql.connector

class ManageBanActivityDatabase_Mariadb:
    def __init__(self, database_connection_pool):
        """Initialize the class with a database connection pool."""
        self.database_connection_pool = database_connection_pool

    def _create_not_bad_get_string_table(self):
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
                ip_address CHAR(39) NOT NULL UNIQUE,
                not_bad_get CHAR(32) NOT NULL UNIQUE,
                examined BOOLEAN DEFAULT FALSE
            );
            '''
            try:
                cursor.execute(create_table_query)
                conn.commit()
                self.logger.debug("not_bad_get_string_table created.")
            except mysql.connector.Error as e:
                self.logger.info(f"Error creating table: {e}")
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def put_not_bad_get(self, ip_address, not_bad_get_string):
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
            self.logger.debug(f"Record for {ip_address} added/updated.")
        except mysql.connector.Error as e:
            self.logger.info(f"Error inserting/updating record: {e}")
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)

    def show_not_bad_get(self):
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
                self.logger.debug("No records found.")
        except mysql.connector.Error as e:
            print(f"Error fetching records: {e}")
        finally:
            cursor.close()
            self.database_connection_pool.return_connection(conn)
