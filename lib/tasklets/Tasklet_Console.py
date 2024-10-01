
import os
import socket
import threading
import time
import semaphore
import subprocess

class Tasklet_Console:
    def __init__(self, host='localhost', port=1027, work_controller=None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False # signals start_server to exit
        self.threads = []    # List to keep track of created threads
        self.work_controller = work_controller  # Reference to work_controller
        self.shutdown_semaphore = threading.Semaphore(0)  # Semaphore to signal shutdown of run_tasklet_console
        self.commands = {
            "help": self.do_show_help,
            "shutdown": self.shutdown,  # Shutdown command for stopping the console
            "exit" : self.do_exit,         # exit this console
            "show-activity_table": self.show_activity_table  # New command
        }

    def show_activity_table(self, filter_arg=None):
        """Run the ManageBanActivityDatabase.py show command with an optional filter argument."""
        try:
            # Prepare the command
            command = 'FAIL3BAN_PROJECT_ROOT/util/ManageBanActivityDatabase.py show'
            
            # If there's a filter argument (e.g., to pipe output to grep), add it
            if filter_arg:
                command += f' | grep {filter_arg}'

            env = os.environ.copy()  # Copy the current environment
            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)

            if result.returncode == 0:
                print(result.stdout)  # Normally, you'd send this to the client socket
            else:
                error_message = f"Error running command: {result.stderr}\n"
                print(error_message)

        except Exception as e:
            error_message = f"Exception occurred: {e}\n"
            print(error_message)
    
    def start_server(self):
        """Start the telnet server and listen for a connection."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)  # Only allow one connection at a time
            self.running = True
            print(f"Tasklet console listening on {self.host}:{self.port}...")

            while self.running:
                print("Waiting for connection...")
                self.client_socket, self.client_address = self.server_socket.accept()
                print(f"Connected to {self.client_address}")

                # Handle commands in a new thread
                thread = threading.Thread(target=self.handle_client)
                self.threads.append(thread)  # Keep track of the thread
                thread.start()

        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop_server()

    def stop_server(self):
        """Stop the server and close sockets."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped.")

    def handle_client(self):
        """Handle the connected client and process commands."""
        try:
            self.client_socket.sendall(b"Welcome to Tasklet Console!\n")
            self.client_socket.sendall(b"Type 'help' for a list of commands.\n")

            while self.running:
                try:
                    self.client_socket.sendall(b"cmd>")
                    data = self.client_socket.recv(1024)
                    # Safely decode data, ignoring problematic bytes
                    decoded_data = data.decode('utf-8', errors='ignore').strip()

                    if not decoded_data:
                        print("Client disconnected.")
                        break

                    print(f"Received command: {decoded_data}")
                    status = self.dispatch_command(decoded_data)
                    if not status:
                        print("Client disconnected.")
                        break
                
                except UnicodeDecodeError as e:
                    print(f"Unicode decode error: {e}")
                    continue  # Skip problematic data

        except ConnectionResetError:
            print("Client disconnected unexpectedly.")
        finally:
            self.client_socket.close()
            self.client_socket = None

    def dispatch_command(self, command):
        """Dispatch command to the appropriate handler with optional arguments."""
        parts = command.split()

        # Extract the main command and any optional argument
        main_command = parts[0]
        optional_arg = parts[1] if len(parts) > 1 else None

        if main_command in self.commands:
            if main_command == 'show-activity_table':
                self.commands[main_command](optional_arg)  # Pass the optional argument
            else:
                self.commands[main_command]()  # No arguments for other commands
        else:
            print("Unknown command. Type 'help' for a list of commands.\n")
            
    def do_show_help(self):
        """Display help information to the client."""
        help_message = (
            "Available commands:\n"
            "help - Show this help message\n"
            "shutdown - Shut down the server\n"
            "show-activity_table - Display the contents of the activity_table\n"
        )
        self.client_socket.sendall(help_message.encode('utf-8'))
        return True
    
    def do_exit(self):
        return False
    
    def shutdown(self):
        """Shut down the server and stop all threads."""
        self.running = False
        self.client_socket.sendall(b"Shutting down the server...\n")

        # Walk through all threads and wait for them to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join()

        self.stop_server()  # Stop the server after all threads are joined
        if self.work_controller:
            self.work_controller.request_shutdown = True  # Set the request_shutdown flag to our parent
        print("All threads have been stopped, and the server has been shut down.")
        self.shutdown_semaphore.release()  # Release semaphore to signal shutdown
        return False
    
# Thread - Entry point from WorkController for running the Tasklet_Console in a separate thread
def run_tasklet_console(**kwargs):
    work_controller = kwargs.get('work_controller')
    tasklet_console = Tasklet_Console(work_controller=work_controller)

    # Start the server
    tasklet_console.start_server()

    while not work_controller.stop_flag.is_set():
        # Wait for the shutdown signal, with a timeout of 15 seconds
        if tasklet_console.shutdown_semaphore.acquire(timeout=15):
            # Semaphore was acquired within 10 seconds
            print("Semaphore acquired, shutting down.")
        else:
            # Timeout reached without the semaphore being released
            print("Timeout reached, continuing without semaphore.")
    
    # Done
    return "OK"

if __name__ == "__main__":
    # Dummy work_controller class for testing
    class DummyWorkController:
        def __init__(self):
            self.stop_flag = False  # Initially, stop_flag is False (running state)
            self.request_shutdown = False  # This will be set to True when shutdown is requested

    # Create an instance of the dummy work_controller
    work_controller = DummyWorkController()

    # Start the Tasklet_Console in a thread
    console_thread = threading.Thread(target=run_tasklet_console, kwargs={'work_controller': work_controller})
    console_thread.start()

    # Simulate shutdown after 10 seconds (for testing)
    time.sleep(60*5)
    work_controller.stop_flag = True  # Simulate stop flag being set
    print("Stop flag set, waiting for Tasklet_Console to shut down.")
