This was one of chat's attempts. It's full of holes, so I gave up.

But it does point the way towards a class that accounts for resource exhaustion
if a task dies and doesnt return the conn

import sqlite3
import threading
from queue import Queue, Empty
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SQLiteConnectionPool")

class SQLiteConnectionPool:
    def __init__(self, db_name, pool_size=5, max_conn_time=300):  # max_conn_time in seconds
        self.db_name = db_name
        self.pool_size = pool_size
        self.max_conn_time = max_conn_time  # Maximum time a connection can be checked out
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self.conn_timestamps = {}  # Tracks when connections are checked out
        self.shutdown_in_progress = False

        for _ in range(pool_size):
            conn = sqlite3.connect(db_name, check_same_thread=False)
            self.pool.put(conn)

    def get_connection(self):
        with self.lock:
            if self.shutdown_in_progress:
                return None

            try:
                conn = self.pool.get_nowait()
                self.conn_timestamps[conn] = time.time()
                return conn
            except Empty:
                conn = sqlite3.connect(self.db_name, check_same_thread=False)
                self.conn_timestamps[conn] = time.time()
                return conn

    def return_connection(self, conn):
        with self.lock:
            # Remove the connection's timestamp
            if conn in self.conn_timestamps:
                del self.conn_timestamps[conn]

            if self.shutdown_in_progress:
                conn.close()
            else:
                self.pool.put(conn)

    def still_in_use(self, conn):
        """
        Updates the timestamp for a connection to indicate it is still in use.

        :param conn: The SQLite connection object that is still being used.
        """
        with self.lock:
            if conn in self.conn_timestamps:
                self.conn_timestamps[conn] = time.time()
                logger.debug(f"Updated timestamp for connection {conn}.")
            else:
                logger.warning(f"Connection {conn} is not tracked for in-use status.")

    def enforce_timeouts(self):
        """
        Closes connections that have been held longer than max_conn_time.

        :return: None
        """
        with self.lock:
            current_time = time.time()
            for conn, checkout_time in list(self.conn_timestamps.items()):
                if current_time - checkout_time > self.max_conn_time:
                    logger.info(f"Closing connection {conn} due to timeout.")
                    self._close_connection(conn)
                    del self.conn_timestamps[conn]

    def _close_connection(self, conn):
        """Close a single SQLite connection."""
        try:
            conn.close()
            logger.debug(f"Closed connection: {conn}")
        except sqlite3.Error as e:
            logger.error(f"Error closing connection: {e}")

    def close_all_connections(self):
        """Closes all outstanding connections and those remaining in the pool."""
        with self.lock:
            logger.info("Initiating shutdown. Closing all connections.")
            self.shutdown_in_progress = True

            # Close all outstanding connections
            for conn in self.conn_timestamps.keys():
                self._close_connection(conn)
            self.conn_timestamps.clear()

            # Close all connections remaining in the pool
            while not self.pool.empty():
                conn = self.pool.get_nowait()
                self._close_connection(conn)

# Example usage
def db_task(pool, task_id):
    """
    Function to be executed by each thread to perform database operations.
    This simulates a long-running task that periodically updates the connection usage.
    """
    conn = pool.get_connection()
    if conn is None:
        logger.info(f"Task {task_id}: No connection available due to shutdown.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cursor.fetchall()
        logger.info(f"Task {task_id}: Tables in database: {rows}")

        # Simulate long-running task by updating connection usage periodically
        for _ in range(5):
            time.sleep(60)  # Simulate work being done
            pool.still_in_use(conn)

    except sqlite3.Error as e:
        logger.error(f"Task {task_id}: Database error: {e}")
    finally:
        pool.return_connection(conn)

if __name__ == "__main__":
    # Initialize the connection pool
    pool = SQLiteConnectionPool(db_name='example.db', pool_size=5)

    # Create and start threads
    threads = []
    for i in range(3):  # Simulate fewer threads than the pool size for testing
        thread = threading.Thread(target=db_task, args=(pool, i+1))
        thread.start()
        threads.append(thread)

    # Wait for threads to finish
    for thread in threads:
        thread.join()

    # Properly shut down the connection pool
    pool.close_all_connections()

