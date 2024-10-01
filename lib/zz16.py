import socket
import threading
import time

class Tasklet_Console:
    def __init__(self, host='localhost', port=57, work_controller=None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        self.threads = []  # List to keep track of created threads
        self.work_controller = work_controller  # Reference to work_controller
        self.commands = {
            "help": self.show_help,
            "shutdown": self.shutdown,  # Shutdown command for stopping the console
        }

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
                if self.work_controller and self.work_controller.stop_flag:  # Check stop_flag for graceful shutdown
                    print("Shutdown flag detected. Exiting...")
                    break

                data = self.client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    print("Client disconnected.")
                    break

                print(f"Received command: {data}")
                self.dispatch_command(data)

        except ConnectionResetError:
            print("Client disconnected unexpectedly.")
        finally:
            self.client_socket.close()
            self.client_socket = None

    def dispatch_command(self, command):
        """Dispatch command to the appropriate handler."""
        if command in self.commands:
            self.commands[command]()
        else:
            self.client_socket.sendall(b"Unknown command. Type 'help' for a list of commands.\n")

    def show_help(self):
        """Display help information to the client."""
        help_message = (
            "Available commands:\n"
            "help - Show this help message\n"
            "shutdown - Shut down the server\n"
        )
        self.client_socket.sendall(help_message.encode('utf-8'))

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
            self.work_controller.request_shutdown = True  # Set the request_shutdown flag
        print("All threads have been stopped, and the server has been shut down.")


# Entry point for running the Tasklet_Console in a separate thread
def run_tasklet_console(**kwargs):
    work_controller = kwargs.get('work_controller')
    tasklet_console = Tasklet_Console(work_controller=work_controller)

    # Wait efficiently for the stop flag from work_controller or exit when stopped
    while not work_controller.stop_flag:  # Assuming work_controller.stop_flag is a boolean
        tasklet_console.start_server()
        time.sleep(1)  # Check stop flag every second, adjust as needed

    # When stop_flag is set, shutdown the tasklet console
    tasklet_console.shutdown()

    # Return status
    return "OK"

class DummyWorkController:
    def __init__(self):
        self.stop_flag = False  # Initially, stop_flag is False (running state)
        self.request_shutdown = False  # This will be set to True when shutdown is requested

    def shutdown(self):
        """Simulate a shutdown by setting stop_flag to True."""
        print("Shutdown method called.")
        self.stop_flag = True

if __name__ == "__main__":
    # Assume the work_controller is created elsewhere and passed into run_tasklet_console
    work_controller = DummyWorkController()

    console_thread = threading.Thread(target=run_tasklet_console, kwargs={'work_controller': work_controller})
    console_thread.start()

    # Simulate some operations and then trigger a shutdown for testing
    time.sleep(60*15)  # Let the console run for a bit (simulates the application running)
    
    # Set the stop_flag to True to signal shutdown
    print("Requesting shutdown...")
    work_controller.shutdown()  # Trigger the shutdown by setting stop_flag to True

    # Wait for the console thread to complete the shutdown
    console_thread.join()
    print("Test complete. Tasklet console has shut down.")
