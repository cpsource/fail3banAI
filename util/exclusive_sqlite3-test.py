import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)

    def execute_with_exclusive_lock(self, query):
        try:
            # Start an exclusive transaction
            self.connection.execute('BEGIN EXCLUSIVE')

            # Your code inside the exclusive lock
            print("Exclusive lock acquired.")
            self.connection.execute(query)
            self.connection.commit()  # Commit the changes

        except sqlite3.DatabaseError as e:
            self.connection.rollback()  # Roll back any changes if there's an error
            print(f"Database error: {e}")
        finally:
            print("Exclusive lock released.")

    def close(self):
        self.connection.close()

# Example usage
db_name = 'example.db'
db_manager = DatabaseManager(db_name)

# Run multiple queries in the same session
db_manager.execute_with_exclusive_lock("INSERT INTO my_table (name) VALUES ('John Doe')")
db_manager.execute_with_exclusive_lock("INSERT INTO my_table (name) VALUES ('Jane Smith')")

# Close the database connection after all transactions
db_manager.close()

