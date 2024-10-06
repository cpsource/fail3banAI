import sqlite3
import threading
from queue import Queue, Empty
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sqlite_connection_pool.log")
    ]
)

logger = logging.getLogger("SQLiteConnectionPool")

class SQLiteConnectionPool:
    def __init__(self, db_name, pool_size=5):
        """
        Initialize the SQLiteConnectionPool.

        :param db_name: Name of the SQLite database file.
        :param pool_size: Number of connections to maintain in the pool.
        """
        self.db_name = db_name
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()  # Ensures thread safety
        self.created_connections = 0  # Tracks dynamically created connections
        self.track_all_outstanding_connections = []  # Tracks all active connections
        self.shutdown_in_progress = False  # Indicates if shutdown has started

        # Pre-create pool_size connections
        try:
            for _ in range(pool_size):
                conn = self._create_connection()
                self.pool.put(conn)
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            self.close_all_connections()
            raise

    def _create_connection(self):
        """Create a new SQLite connection."""
        try:
            conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.created_connections += 1
            logger.debug(f"Created new connection: {conn}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error creating connection: {e}")
            raise

    def get_connection(self):
        """
        Retrieve a connection from the pool or create a new one if the pool is empty.

        :return: SQLite connection object or None if shutdown is in progress.
        """
        with self.lock:
            if self.shutdown_in_progress:
                logger.info("Shutdown in progress. No new connections will be provided.")
                return None

            try:
                conn = self.pool.get_nowait()
                logger.debug(f"Retrieved connection from pool: {conn}")
            except Empty:
                logger.warning("No available connections in the pool. Creating a new connection.")
                try:
                    conn = self._create_connection()
                except Exception as e:
                    logger.error(f"Failed to create a new connection: {e}")
                    return None

            self.track_all_outstanding_connections.append(conn)
            return conn

    def return_connection(self, conn):
        """
        Return a connection to the pool or close it if the pool is full or shutdown is in progress.

        :param conn: SQLite connection object to return.
        :return: None
        """
        with self.lock:
            if self.shutdown_in_progress:
                logger.info("Shutdown in progress. Closing returned connection.")
                self._close_connection(conn)
                return

            if conn in self.track_all_outstanding_connections:
                self.track_all_outstanding_connections.remove(conn)
            else:
                logger.warning("Attempted to return an unmanaged connection.")

            if not self.pool.full():
                self.pool.put(conn)
                logger.debug(f"Returned connection to pool: {conn}")
            else:
                logger.info("Pool is full. Closing returned connection.")
                self._close_connection(conn)

    def _close_connection(self, conn):
        """Close a single SQLite connection."""
        try:
            conn.close()
            logger.debug(f"Closed connection: {conn}")
        except sqlite3.Error as e:
            logger.error(f"Error closing connection: {e}")

    def close_all_connections(self):
        """
        Close all connections in the pool and any outstanding connections.

        :return: None
        """
        with self.lock:
            logger.info("Initiating shutdown. Closing all connections.")
            self.shutdown_in_progress = True

            # Close all outstanding connections
            for conn in self.track_all_outstanding_connections:
                self._close_connection(conn)
            self.track_all_outstanding_connections.clear()

            # Close all connections remaining in the pool
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    self._close_connection(conn)
                except Empty:
                    break

            logger.info("All connections have been closed.")

    def get_total_connections_created(self):
        """
        Get the total number of connections created, including dynamic ones.

        :return: Integer count of created connections.
        """
        with self.lock:
            return self.created_connections

# Example usage in a threaded environment
def db_task(pool, task_id):
    """
    Function to be executed by each thread to perform database operations.

    :param pool: Instance of SQLiteConnectionPool.
    :param task_id: Identifier for the task/thread.
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
    except sqlite3.Error as e:
        logger.error(f"Task {task_id}: Database error: {e}")
    finally:
        pool.return_connection(conn)

if __name__ == "__main__":
    # Ensure the database exists for demonstration purposes
    db_path = 'example.db'
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS example_table (id INTEGER PRIMARY KEY, name TEXT);")
        conn.commit()
        conn.close()

    # Initialize the connection pool
    pool = SQLiteConnectionPool(db_name=db_path, pool_size=5)

    # Create and start threads
    threads = []
    num_threads = 10  # More than pool size to test dynamic connections
    for i in range(num_threads):
        thread = threading.Thread(target=db_task, args=(pool, i+1))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Properly tear down the connection pool
    pool.close_all_connections()

    # Log the number of dynamically created connections
    logger.info(f"Total connections created (including dynamic): {pool.get_total_connections_created()}")

