class foo:
    
    def update_time(self, ip_address):
        """Update the datetime_of_last_ban for the given IP address."""
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
            # If the IP address doesn't exist, log or handle the error
            self.logger.warning(f"IP address {ip_address} not found in the database")

            # Commit the changes
            conn.commit()

        # Return the connection to the pool
        cursor.close()
        self.database_connection_pool.return_connection(conn)
