import threading
import queue
import logging

# Dummy logger setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SQLiteConnectionPool:
    def __init__(self, pool_size=5):
        """
        Initialize the connection pool and the necessary locks.
        """
        self.pool = queue.Queue(maxsize=pool_size)  # Connection pool
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
        self.in_use.acquire()
        
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


# Dummy test of the class
if __name__ == "__main__":
    pool = SQLiteConnectionPool(pool_size=2)
    
    conn1 = pool.get_connection()
    print(f"Acquired: {conn1}")

    conn2 = pool.get_connection()
    print(f"Acquired: {conn2}")

    pool.return_connection(conn1)
    print(f"Returned: {conn1}")

    conn3 = pool.get_connection()
    print(f"Acquired: {conn3}")
