#
# Create 5 threads, pound on sqlite3 and look for lock errors
#

import sqlite3
import threading
import random
import time

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_connection(self):
        """Each thread gets its own connection."""
        return sqlite3.connect(self.db_name)

    def execute_transaction(self, thread_id):
        """Perform a write, select, or delete operation within a transaction."""
        conn = self.get_connection()
        new_records = 0  # Track how many new records this thread added or deleted

        try:
            for _ in range(100):  # Each thread does 100 operations
                cursor = conn.cursor()

                # Randomly choose an action (write, select, delete)
                action = random.choice(['write', 'select', 'delete'])

                if action == 'write':
                    try:
                        # Perform a write (insert a row)
                        name = f'Thread_{thread_id}_name'
                        cursor.execute("INSERT INTO my_table (name) VALUES (?)", (name,))
                        conn.commit()  # Commit after the write operation
                        new_records += 1  # Increment the local count for new records

                        # Increment the add-count for this thread in the inc_dec_cnt table
                        cursor.execute("UPDATE inc_dec_cnt SET add_count = add_count + 1 WHERE thread_id = ?", (f'Thread_{thread_id}',))
                        conn.commit()
                        
                        print(f"Thread {thread_id}: Inserted {name}")
                    except sqlite3.DatabaseError as e:
                        print(f"Thread {thread_id}: Write error: {e}")
                        conn.rollback()

                elif action == 'select':
                    try:
                        # Perform a select (read all rows)
                        cursor.execute("SELECT * FROM my_table WHERE name = ?", (f'Thread_{thread_id}_name',))
                        results = cursor.fetchall()
                        print(f"Thread {thread_id}: Fetched {len(results)} rows")
                    except sqlite3.DatabaseError as e:
                        print(f"Thread {thread_id}: Select error: {e}")
                        conn.rollback()

                elif action == 'delete':
                    try:
                        # Perform a delete (delete a random record specific to this thread)
                        cursor.execute("SELECT id FROM my_table WHERE name = ?", (f'Thread_{thread_id}_name',))
                        records = cursor.fetchall()
                        if records:
                            # Select a random record to delete
                            random_record_id = random.choice(records)[0]
                            cursor.execute("DELETE FROM my_table WHERE id = ?", (random_record_id,))
                            conn.commit()
                            new_records -= 1  # Decrement the local count for deleted records

                            # Increment the delete-count for this thread in the inc_dec_cnt table
                            cursor.execute("UPDATE inc_dec_cnt SET delete_count = delete_count + 1 WHERE thread_id = ?", (f'Thread_{thread_id}',))
                            conn.commit()

                            print(f"Thread {thread_id}: Deleted record with id {random_record_id}")
                        else:
                            print(f"Thread {thread_id}: No records to delete.")
                    except sqlite3.DatabaseError as e:
                        print(f"Thread {thread_id}: Delete error: {e}")
                        conn.rollback()

                cursor.close()

                # Small random delay between operations
                time.sleep(random.uniform(0.01, 0.1))

            # After all operations, calculate the actual number of records specific to this thread
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM my_table WHERE name = ?", (f'Thread_{thread_id}_name',))
            record_count_in_db = cursor.fetchone()[0]
            cursor.close()

        except sqlite3.DatabaseError as e:
            print(f"Thread {thread_id}: Database error: {e}")
            conn.rollback()  # Rollback if an error occurs
        finally:
            print(f"Thread {thread_id}: Closing connection with {record_count_in_db} records in database.")
            conn.close()

        # Compare the local record count with the actual count in the database
        if new_records == record_count_in_db:
            print(f"Thread {thread_id}: Consistency check passed!")
        else:
            print(f"Thread {thread_id}: Consistency check failed! Local count: {new_records}, DB count: {record_count_in_db}")

        return record_count_in_db  # Return the final count of records for this thread

# Function to be executed by each thread
def thread_function(db_manager, thread_id, results):
    results[thread_id] = db_manager.execute_transaction(thread_id)

# Main function to set up threads
def main():
    db_name = 'example.db'

    # Set up the database schema (for simplicity)
    db_manager = DatabaseManager(db_name)
    conn = db_manager.get_connection()

    # Create the tables if they don't exist
    conn.execute("CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inc_dec_cnt (
            id INTEGER PRIMARY KEY,
            thread_id TEXT,
            add_count INTEGER DEFAULT 0,
            delete_count INTEGER DEFAULT 0
        )
    """)

    # Clean up the tables by deleting all records
    conn.execute("DELETE FROM my_table")
    conn.execute("DELETE FROM inc_dec_cnt")
    conn.commit()
    print("Cleaned the tables, all records deleted.")

    # Initialize the inc_dec_cnt table with a row for each thread
    for i in range(5):  # Assuming 5 threads
        conn.execute("INSERT INTO inc_dec_cnt (thread_id, add_count, delete_count) VALUES (?, 0, 0)", (f'Thread_{i}',))
    conn.commit()

    # Close the connection after setting up the tables and cleaning them
    conn.close()

    # Create a list to store the final record counts from each thread
    results = [0] * 5  # Assuming 5 threads

    # Create and start multiple threads
    threads = []
    for i in range(5):  # 5 threads for this example
        thread = threading.Thread(target=thread_function, args=(db_manager, i, results))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Sum up the final row counts from all threads
    total_records = sum(results)
    print(f"Total records reported by threads: {total_records}")

    # Check the actual number of rows in the database to verify consistency
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM my_table")
    actual_row_count = cursor.fetchone()[0]

    # Verify the inc_dec_cnt table and display the final report with net count and running total
    cursor.execute("SELECT * FROM inc_dec_cnt")
    inc_dec_records = cursor.fetchall()

    print(f"Actual records in the database: {actual_row_count}")
    print("\nThread operation counts (add/delete/net):")

    running_total = 0
    for record in inc_dec_records:
        thread_id = record[1]
        add_count = record[2]
        delete_count = record[3]
        net_count = add_count - delete_count
        running_total += net_count

        print(f"Thread {thread_id} -> Add count: {add_count}, Delete count: {delete_count}, Net count: {net_count}, Running total: {running_total}")

    conn.close()

    # Check consistency
    if total_records == actual_row_count:
        print("\nOverall consistency check passed!")
    else:
        print("\nOverall consistency check failed!")

if __name__ == "__main__":
    main()

