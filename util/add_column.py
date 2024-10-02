import sqlite3
import os
import sys

def add_column_to_table(db_name, table_name, column_name, column_type):
    # Connect to the SQLite database
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if cursor.fetchone() is None:
        print(f"Error: Table '{table_name}' does not exist.")
        conn.close()
        sys.exit(1)

    # Check if column already exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if col[1] == column_name:
            print(f"Error: Column '{column_name}' already exists in table '{table_name}'.")
            conn.close()
            sys.exit(1)

    # Add the column to the table
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        conn.commit()
        print(f"Column '{column_name}' of type '{column_type}' added to table '{table_name}' successfully.")
    except sqlite3.Error as e:
        print(f"Error adding column: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 add_column.py <table_name> <column_name> <column_type>")
        sys.exit(1)

    # Database location
    db_name = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/fail3ban_server.db"

    # Get the arguments from the command line
    table_name = sys.argv[1]
    column_name = sys.argv[2]
    column_type = sys.argv[3]

    # Add the column to the specified table
    add_column_to_table(db_name, table_name, column_name, column_type)

