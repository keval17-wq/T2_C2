import socket
import threading
import time

def handle_ccp_connection(conn, addr):
    print(f"Connected to CCP at {addr}")
    conn.send("HELLO MCP".encode())
    while True:
        data = conn.recv(1024).decode()
        if not data:
            print(f"Connection lost with CCP at {addr}")
            conn.close()
            return
        
        print(f"Received from CCP: {data}")
        
        # Process received data and send appropriate response
        if data == "HELLO MCP":
            response = "HELLO CCP"
        elif data == "STATUS REPORT":
            # Dummy status report for example
            response = "STATUS OK"
        elif data == "LOCATION UPDATE":
            # Dummy location update for example
            response = "LOCATION ACK"
        else:
            response = "UNKNOWN COMMAND"
        
        conn.send(response.encode())

def start_mcp():
    host = 'localhost'
    port = 52002
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"MCP started on port {port}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    start_mcp()
