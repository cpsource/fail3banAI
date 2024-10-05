# Manage a database pool for mariaDB

import os
import sys
import threading
from queue import Queue, Empty, Full
#import queue
import logging
from dotenv import load_dotenv
import mysql.connector

class MariaDBConnectionPool:
    def __init__(self, logger, pool_size=5):
        """
        Initialize the connection pool and the necessary locks.
        """
        self.logger = logger
        self.created_connections = 0
        self.pool = Queue(maxsize=pool_size)  # Connection pool
        self.lock = threading.Lock()  # Main lock for the pool
        self.track_all_outstanding_connections = []  # List to track all active connections
        self.shutdown_in_progress = False  # Flag for shutdown
        self._initialize_pool(pool_size)
        
    def _initialize_pool(self, pool_size):
        """Fill the pool with initial connections."""
        for _ in range(pool_size):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
                self.logger.debug(f"Added connection: {conn}")
                
    def _create_connection(self):
        """Create a connection to the database"""
        conn = mysql.connector.connect(
            user=os.getenv('MARIADB_USER_NAME'),
            password=os.getenv('MARIADB_USER_PASSWORD'),
            host=os.getenv('MARIADB_USER_HOST'),
            port=os.getenv('MARIADB_USER_PORT'),
            database=os.getenv('MARIADB_USER_DATABASE')
        )

        if conn is not None:
            self.logger.debug("Created connection ok")
        else:
            self.logger.debug("Failed to create connection")
            
        self.created_connections += 1
        return conn

    def get_connection(self):
        """
        Retrieve a connection from the pool or create a new one if the pool is empty.
        
        :return: SQLite connection object or None if shutdown is in progress or error occurs.
        """

        try:
            with self.lock:
                # If shutdown is in progress, don't return any new connections
                if self.shutdown_in_progress:
                    self.logger.debug("Shutdown in progress. No new connections will be provided.")
                    return None

                try:
                    # Try to get a connection from the pool without blocking
                    conn = self.pool.get_nowait()
                except Empty:  # queue.Empty is replaced by Empty due to the direct import from queue
                    logger.warning("No available connections in the pool. Creating a new connection.")
                    try:
                        # Create a new connection if the pool is empty
                        conn = self._create_connection()
                    except Exception as e:
                        logger.error(f"Failed to create a new connection: {e}")
                        return None

            # Add the connection to the list of outstanding connections
            self.track_all_outstanding_connections.append(conn)
            return conn
        
        except Exception as e:
            logger.error(f"Error in get_connection: {e}")
            return None

    def return_connection(self, conn):
        """
        Return a connection to the pool
        """
        with self.lock:
            if conn in self.track_all_outstanding_connections:
                self.track_all_outstanding_connections.remove(conn)
                try:
                    self.pool.put_nowait(conn)
                    logger.debug(f"Returned connection to pool: {conn}")
                except Full:
                    logger.warning("Connection pool is full. Closing the returned connection.")
                    conn.close()

    def _close_connection(self, conn):
        """Close a single SQLite connection."""
        try:
            conn.close()
            logger.debug(f"Closed connection: {conn}")
        except mysql.connector.Error as e:
            logger.error(f"Error closing connection: {e}")

    def close_all_connections(self):
        """
        Close all connections in the pool and any outstanding connections.

        :return: None
        """
        with self.lock:
            self.logger.debug("Initiating shutdown. Closing all connections.")
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

            self.logger.debug("All connections have been closed.")

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

            self.logger.debug(f"SQLiteConnectionPool State:")
            self.logger.debug(f"Connections in use: {in_use}")
            self.logger.debug(f"Connections available in pool: {available_in_pool}")
            self.logger.debug(f"Total connections created (including dynamic): {total_created}")

    # a wrapper function so we are consistent with project standards
    def shutdown(self):
        self.close_all_connections()

    def is_in_use(self):
        """Returns True if the self.in_use lock is currently held."""
        return self.in_use.locked()

    def print_pool_contents(self):
        """Print pool contents by temporarily removing connections."""
        temp_list = []
        while not self.pool.empty():
            conn = self.pool.get()
            print(f"Connection in pool: {conn}")
            temp_list.append(conn)
        
        # Return all connections to the pool
        for conn in temp_list:
            self.pool.put(conn)
            
# Example usage in a threaded environment
def db_task(pool, task_id):
    """
    Function to be executed by each thread to perform database operations.

    :param pool: Instance of SQLiteConnectionPool.
    :param task_id: Identifier for the task/thread.
    """
    conn = pool.get_connection()
    if conn is None:
        print(f"Task {task_id}: No connection available due to shutdown.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")  # MariaDB equivalent of listing tables
        rows = cursor.fetchall()
        print(f"Task {task_id}: Tables in database: {rows}")
    except mysql.connector.Error as e:
        logger.error(f"Task {task_id}: Database error: {e}")
    finally:
        pool.return_connection(conn)
    
# Test the class using threads
import threading
import time

# Extracted constants for log file name and format
LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
# Set up the logging format to include file name and line number
LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
# And our log id
LOG_ID = "fail3ban"

# Extracted function to set up logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE_NAME),
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    # Call the extracted function to configure logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)

    # load dotenv
    try:
        # Attempt to load dotenv file using the environment variable
        dotenv_config = load_dotenv(f"{os.getenv('HOME')}/.env")
        print("dotenv file loaded successfully.")
    except Exception as e:
        # Handle any exceptions that may occur
        print(f"An error occurred while loading dotenv: {e}")
    
    # debugging
    user=os.getenv('MARIADB_USER_NAME')
    password=os.getenv('MARIADB_USER_PASSWORD')
    host=os.getenv('MARIADB_USER_HOST')
    port=os.getenv('MARIADB_USER_PORT')
    database=os.getenv('MARIADB_USER_DATABASE')
    print(f"user = {user}")
    print(f"password = {password}")
    print(f"host = {host}")
    print(f"port = {port}")
    print(f"database = {database}")
    
    # Initialize the connection pool
    pool = MariaDBConnectionPool(logger, pool_size=5)
    pool.print_pool_contents() # Prints all connections in the pool

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
    print(f"Total connections created (including dynamic): {pool.get_total_connections_created()}")
