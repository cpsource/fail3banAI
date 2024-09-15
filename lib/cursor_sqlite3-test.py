import sqlite3

def select_all_from_table(db_name, table_name):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Execute the SELECT query
        cursor.execute(f"SELECT * FROM {table_name}")

        # Fetch all results
        results = cursor.fetchall()

        # Print out each row
        for row in results:
            print(row)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

# Example usage
db_name = 'example.db'
table_name = 'my_table'
select_all_from_table(db_name, table_name)

