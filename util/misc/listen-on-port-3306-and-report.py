import socket

def start_server(host="127.0.0.1", port=3306):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Listening on {host}:{port}...")

    while True:
        # Wait for a connection
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()

        try:
            print(f"Connection established with {client_address}")
            
            while True:
                # Receive data in small chunks
                data = connection.recv(1024)
                
                if data:
                    # Print the data as ASCII
                    print(f"Received: {data.decode('ascii', errors='ignore')}")
                else:
                    # No more data from the client, close the connection
                    print("No more data from client. Closing connection.")
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Clean up the connection
            connection.close()

if __name__ == "__main__":
    start_server()

