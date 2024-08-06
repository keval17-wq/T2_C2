import socket
import threading
import time

clients = {}
client_id_counter = 0
status_interval = 2  # seconds
timeout_interval = 3  # seconds

def assign_id():
    global client_id_counter
    client_id_counter += 1
    return client_id_counter

def handle_ccp_connection(conn, addr):
    print(f"Connected to CCP at {addr}")
    client_id = None

    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                print(f"Connection lost with CCP at {addr}")
                conn.close()
                if client_id in clients:
                    del clients[client_id]
                return
            
            print(f"Received from CCP: {data}")
            response = "UNKNOWN COMMAND\n"

            if data == "TRIN":
                client_id = assign_id()
                clients[client_id] = {'conn': conn, 'type': 'train', 'last_message': time.time()}
                response = f"ACKN {client_id}\n"
            elif data == "STIN":
                client_id = assign_id()
                clients[client_id] = {'conn': conn, 'type': 'station', 'last_message': time.time()}
                response = f"ACKN {client_id}\n"
            elif data.startswith("STAT"):
                if client_id:
                    clients[client_id]['last_message'] = time.time()
                    response = "STAT ACK\n"
            elif data == "HELLO MCP":
                response = "HELLO CCP\n"
            elif data == "STATUS REPORT":
                response = "STATUS OK\n"
            elif data == "LOCATION UPDATE":
                response = "LOCATION ACK\n"
            else:
                response = "UNKNOWN COMMAND\n"

            conn.send(response.encode())
        except socket.error as e:
            print(f"Socket error: {e}")
            conn.close()
            if client_id in clients:
                del clients[client_id]
            return

def send_status():
    while True:
        for client_id, client_info in list(clients.items()):
            conn = client_info['conn']
            if time.time() - client_info['last_message'] > timeout_interval:
                print(f"Client {client_id} is unresponsive. Removing from list.")
                conn.close()
                del clients[client_id]
                continue
            if client_info['type'] == 'train':
                try:
                    conn.send("STAT\n".encode())
                except socket.error as e:
                    print(f"Socket error: {e}")
                    conn.close()
                    del clients[client_id]
        time.sleep(status_interval)

def start_mcp(port):
    host = 'localhost'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"MCP started on port {port}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    ports = [52002, 52003, 52004, 52005, 52006, 52007, 52008, 52009]  # Expanded list of ports
    for port in ports:
        threading.Thread(target=start_mcp, args=(port,)).start()

    threading.Thread(target=send_status).start()


# import socket
# import threading

# def handle_ccp_connection(conn, addr):
#     print(f"Connected to CCP at {addr}")
#     while True:
#         data = conn.recv(1024).decode()
#         if not data:
#             break
#         print(f"Received from CCP: {data}")
        
#         # Process received data and send appropriate response
#         if data == "HELLO MCP":
#             response = "HELLO CCP"
#         elif data == "STATUS REPORT":
#             # Dummy status report for example
#             response = "STATUS OK"
#         elif data == "LOCATION UPDATE":
#             # Dummy location update for example
#             response = "LOCATION ACK"
#         else:
#             response = "UNKNOWN COMMAND"
        
#         conn.send(response.encode())
#     conn.close()

# def start_mcp(port):
#     host = 'localhost'
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((host, port))
#     server_socket.listen(5)
#     print(f"MCP started on port {port}")

#     while True:
#         conn, addr = server_socket.accept()
#         threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()

# if __name__ == "__main__":
#     ports = [52002, 52003, 52004, 52005]  # List of ports to listen on
#     for port in ports:
#         threading.Thread(target=start_mcp, args=(port,)).start()






# import socket
# import threading
# import time

# def handle_ccp_connection(conn, addr):
#     print(f"Connected to CCP at {addr}")
#     conn.send("HELLO MCP".encode())
#     while True:
#         data = conn.recv(1024).decode()
#         if not data:
#             print(f"Connection lost with CCP at {addr}")
#             conn.close()
#             return
        
#         print(f"Received from CCP: {data}")
        
#         # Process received data and send appropriate response
#         if data == "HELLO MCP":
#             response = "HELLO CCP"
#         elif data == "STATUS REPORT":
#             # Dummy status report for example
#             response = "STATUS OK"
#         elif data == "LOCATION UPDATE":
#             # Dummy location update for example
#             response = "LOCATION ACK"
#         else:
#             response = "UNKNOWN COMMAND"
        
#         conn.send(response.encode())

# def start_mcp():
#     host = 'localhost'
#     port = 52002
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((host, port))
#     server_socket.listen(5)
#     print(f"MCP started on port {port}")

#     while True:
#         conn, addr = server_socket.accept()
#         threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()

# if __name__ == "__main__":
#     start_mcp()
