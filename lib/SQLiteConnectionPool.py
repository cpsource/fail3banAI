import sqlite3
import threading
from queue import Queue, Empty, Full
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
    def __init__(self, pool_size=5):
        """
        Initialize the connection pool and the necessary locks.
        """
        self.pool = Queue(maxsize=pool_size)  # Connection pool
        self.lock = threading.Lock()  # Main lock for the pool
        self.in_use = threading.Lock()  # Second lock to control access to the connection process
        self.track_all_outstanding_connections = []  # List to track all active connections
        self.shutdown_in_progress = False  # Flag for shutdown
        self._initialize_pool()

    def _initialize_pool(self):
        """Fill the pool with initial connections."""
        for _ in range(self.pool.maxsize):
            conn = self._create_connection()
            if conn:
                self.pool.put_nowait(conn)

    def _create_connection(self):
        """Simulate creating a new connection (this should be replaced with actual DB connection creation logic)."""
        return f"SQLiteConnection_{len(self.track_all_outstanding_connections) + 1}"

    def get_connection(self):
        """
        Retrieve a connection from the pool or create a new one if the pool is empty.
        This method acquires the self.in_use lock and holds it until return_connection is called.
        It also ensures proper release of the lock in case of an error.
        
        :return: SQLite connection object or None if shutdown is in progress or error occurs.
        """
        # Explicitly acquire the in_use lock
        self.in_use.acquire() # self.in_use_acquire(blocking=False) won't block

        # Use this code to pass the blocking condition to caller
        if False and not self.in_use.acquire(blocking=False):
            logger.debug("Connection in use. Unable to get connection now.")
            return None
        
        try:
            with self.lock:
                if self.shutdown_in_progress:
                    logger.info("Shutdown in progress. No new connections will be provided.")
                    # Release the in_use lock before returning
                    self.in_use.release()
                    return None

                try:
                    conn = self.pool.get_nowait()
                except queue.Empty:
                    logger.warning("No available connections in the pool. Creating a new connection.")
                    try:
                        conn = self._create_connection()
                    except Exception as e:
                        logger.error(f"Failed to create a new connection: {e}")
                        # Release the in_use lock before returning in case of error
                        self.in_use.release()
                        return None

                self.track_all_outstanding_connections.append(conn)
                return conn
        
        except Exception as e:
            logger.error(f"Error in get_connection: {e}")
            # Ensure that we release the in_use lock even in case of an unexpected error
            self.in_use.release()
            return None

    def return_connection(self, conn):
        """
        Return a connection to the pool, releasing the self.in_use lock.
        """
        with self.lock:
            if conn in self.track_all_outstanding_connections:
                self.track_all_outstanding_connections.remove(conn)

            try:
                self.pool.put_nowait(conn)
                logger.debug(f"Returned connection to pool: {conn}")
            except queue.Full:
                logger.warning("Connection pool is full. Closing the returned connection.")
                conn.close()
        
        # Release the in_use lock after returning the connection
        self.in_use.release()

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

    # A wrapper function
    def shutdown():
        self.close_all_connections()
        
    def get_total_connections_created(self):
        """
        Get the total number of connections created, including dynamic ones.

        :return: Integer count of created connections.
        """
        with self.lock:
            return self.created_connections

    def show(self):
        """
        Display the current state of the SQLiteConnectionPool, including:
        - Number of connections in use
        - Number of available connections in the pool
        - Total number of connections created
        """
        with self.lock:
            in_use = len(self.track_all_outstanding_connections)
            available_in_pool = self.pool.qsize()
            total_created = self.created_connections

            logger.info(f"SQLiteConnectionPool State:")
            logger.info(f"Connections in use: {in_use}")
            logger.info(f"Connections available in pool: {available_in_pool}")
            logger.info(f"Total connections created (including dynamic): {total_created}")

    # a wrapper function so we are consistent with project standards
    def shutdown(self):
        self.close_all_connections()

    def is_in_use(self):
        """Returns True if the self.in_use lock is currently held."""
        return self.in_use.locked()
    
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

# Test the class using threads
import threading
import time

def worker(pool, worker_id):
    logger.info(f"Worker {worker_id} attempting to get a connection...")
    conn = pool.get_connection()

    if conn:
        logger.info(f"Worker {worker_id} acquired connection: {conn}")
        time.sleep(2)  # Simulate work
        pool.return_connection(conn)
        logger.info(f"Worker {worker_id} returned connection: {conn}")
    else:
        logger.info(f"Worker {worker_id} could not acquire a connection. In use: {pool.is_in_use()}")

if __name__ == "__main__":
    pool = SQLiteConnectionPool(pool_size=2)

    threads = []
    for i in range(4):  # 4 threads trying to access 2 connections
        t = threading.Thread(target=worker, args=(pool, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        
if __name__ == "__main__" and False:
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

    # Show the state of the connection pool
    pool.show()

    # Properly tear down the connection pool
    pool.close_all_connections()

    # Log the number of dynamically created connections
    logger.info(f"Total connections created (including dynamic): {pool.get_total_connections_created()}")

