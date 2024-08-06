import socket
import time

def start_ccp():
    host = 'localhost'
    port = 52002
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to MCP at {host}:{port}")

    # Send initial hello message
    client_socket.send("HELLO MCP".encode())
    response = client_socket.recv(1024).decode()
    print(f"Received from MCP: {response}")
    
    if response == "HELLO CCP":
        # Start regular status updates and location updates
        while True:
            # Example of status report
            client_socket.send("STATUS REPORT".encode())
            response = client_socket.recv(1024).decode()
            print(f"Received from MCP: {response}")
            
            # Example of location update
            client_socket.send("LOCATION UPDATE".encode())
            response = client_socket.recv(1024).decode()
            print(f"Received from MCP: {response}")
            
            time.sleep(5)  # Wait 5 seconds before next update

    client_socket.close()

if __name__ == "__main__":
    start_ccp()
