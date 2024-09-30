import sqlite3
import threading
from queue import Queue

# Create a connection pool
class SQLiteConnectionPool:
    def __init__(self, db_name, pool_size=5):
        self.db_name = db_name
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()  # Lock for thread safety
        self.created_connections = 0  # To track the number of total connections created
        self.track_all_outstanding_connections = []  # Tracks all outstanding connections (from the pool or dynamic)
        
        # Pre-create connections and store them in the pool and tracking list
        for _ in range(pool_size):
            conn = sqlite3.connect(db_name, check_same_thread=False)
            self.pool.put(conn)

    def get_connection(self):
        """Get a connection from the pool or create a new one if the pool is empty."""
        with self.lock:
            if not self.pool.empty():
                # If the pool has available connections, use one
                conn = self.pool.get()
            else:
                # Pool is empty, create a new connection and track it
                print("No connections available in the pool. Creating a new connection.")
                self.created_connections += 1
                conn = sqlite3.connect(self.db_name, check_same_thread=False)
            
            # Add the connection to the list of outstanding connections
            self.track_all_outstanding_connections.append(conn)
            return conn

    def return_connection(self, conn):
        """Return a connection to the pool or close it if the pool is full."""
        with self.lock:
            # Remove the connection from the outstanding connections list
            if conn in self.track_all_outstanding_connections:
                self.track_all_outstanding_connections.remove(conn)

            # If there is room in the pool, put the connection back
            if self.pool.qsize() < self.pool_size:
                self.pool.put(conn)
                print("Connection returned to the pool.")
            else:
                # If the pool is full, close the connection
                print("Pool is full, closing the connection.")
                conn.close()

    def close_all_connections(self):
        """Closes all outstanding connections (both from the pool and dynamic)."""
        with self.lock:
            # Close all outstanding connections
            for conn in self.track_all_outstanding_connections:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")

            # Clear the outstanding connections list
            self.track_all_outstanding_connections.clear()

# Function for the thread to execute
def db_task(pool):
    # Get a connection from the pool
    conn = pool.get_connection()
    cursor = conn.cursor()
    # Perform database operations (example: listing all tables)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cursor.fetchall()
    print(rows)
    # Return the connection to the pool
    pool.return_connection(conn)

if __name__ == "__main__":
    # Initialize the connection pool
    pool = SQLiteConnectionPool('example.db', pool_size=5)

    # Create and start threads
    threads = []
    for _ in range(10):  # Use more threads than the pool size to test dynamic creation
        thread = threading.Thread(target=db_task, args=(pool,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Properly tear down the connection pool
    pool.close_all_connections()

    # Print the number of dynamically created connections
    print(f"Total connections created (including dynamic): {pool.created_connections}")

