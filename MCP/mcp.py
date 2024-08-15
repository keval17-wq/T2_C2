import socket
import threading
import time
import logging
from signal import signal, SIGINT
from sys import exit

clients_by_ip = {}  # Dictionary to map IP addresses to client info
status_interval = 2  # seconds
timeout_interval = 3  # seconds

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_ccp_connection(conn, addr):
    logging.info(f"Connected to CCP at {addr}")
    client_ip = addr[0]

    try:
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                logging.info(f"Connection lost with CCP at {addr}")
                break
            
            logging.info(f"Received from CCP: {data}")
            response = "UNKNOWN COMMAND\n"

            if data == "TRIN":
                clients_by_ip[client_ip] = {'conn': conn, 'type': 'train', 'last_message': time.time()}
                response = f"ACKN {client_ip}\n"
            elif data == "STIN":
                clients_by_ip[client_ip] = {'conn': conn, 'type': 'station', 'last_message': time.time()}
                response = f"ACKN {client_ip}\n"
            elif data.startswith("STAT"):
                if client_ip in clients_by_ip:
                    clients_by_ip[client_ip]['last_message'] = time.time()
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
        logging.error(f"Socket error: {e}")
    finally:
        if client_ip in clients_by_ip:
            del clients_by_ip[client_ip]  # Remove from IP map
        conn.close()
        logging.info(f"Connection with CCP at {addr} closed")

def send_status():
    while True:
        for client_ip, client_info in list(clients_by_ip.items()):
            conn = client_info['conn']
            if time.time() - client_info['last_message'] > timeout_interval:
                logging.warning(f"Client {client_ip} is unresponsive. Removing from list.")
                conn.close()
                del clients_by_ip[client_ip]
                continue
            if client_info['type'] == 'train':
                try:
                    conn.send("STAT\n".encode())
                except socket.error as e:
                    logging.error(f"Socket error: {e}")
                    conn.close()
                    del clients_by_ip[client_ip]
        time.sleep(status_interval)

def send_command_to_ccp(ip_address, command):
    client_info = clients_by_ip.get(ip_address)
    if client_info:
        try:
            client_info['conn'].send(f"{command}\n".encode())
            logging.info(f"Sent command '{command}' to CCP at {ip_address}")
        except socket.error as e:
            logging.error(f"Failed to send command to {ip_address}: {e}")
            client_info['conn'].close()
            del clients_by_ip[ip_address]
    else:
        logging.warning(f"No active CCP found at {ip_address}")

def start_mcp(port):
    host = 'localhost'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"MCP started on port {port}")

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()
    except Exception as e:
        logging.error(f"Error in MCP on port {port}: {e}")
    finally:
        server_socket.close()

def command_input_listener():
    while True:
        user_input = input("Enter command (format: IP COMMAND): ").strip()
        if user_input:
            try:
                ip_address, command = user_input.split(maxsplit=1)
                send_command_to_ccp(ip_address, command)
            except ValueError:
                logging.warning("Invalid input. Use format: IP COMMAND")

def graceful_shutdown(signal_received, frame):
    logging.info('SIGINT or CTRL-C detected. Shutting down gracefully...')
    for client_ip, client_info in clients_by_ip.items():
        client_info['conn'].close()
    logging.info('All connections closed.')
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, graceful_shutdown)
    
    port = 52002  # Single port for all connections
    threading.Thread(target=start_mcp, args=(port,)).start()

    threading.Thread(target=send_status).start()
    threading.Thread(target=command_input_listener).start()  # Start listening for manual commands

# import socket
# import threading
# import time
# import logging
# from signal import signal, SIGINT
# from sys import exit

# clients_by_ip = {}  # Dictionary to map IP addresses to client info
# status_interval = 2  # seconds
# timeout_interval = 3  # seconds

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def handle_ccp_connection(conn, addr):
#     logging.info(f"Connected to CCP at {addr}")
#     client_ip = addr[0]

#     try:
#         while True:
#             data = conn.recv(1024).decode().strip()
#             if not data:
#                 logging.info(f"Connection lost with CCP at {addr}")
#                 break
            
#             logging.info(f"Received from CCP: {data}")
#             response = "UNKNOWN COMMAND\n"

#             if data == "TRIN":
#                 clients_by_ip[client_ip] = {'conn': conn, 'type': 'train', 'last_message': time.time()}
#                 response = f"ACKN {client_ip}\n"
#             elif data == "STIN":
#                 clients_by_ip[client_ip] = {'conn': conn, 'type': 'station', 'last_message': time.time()}
#                 response = f"ACKN {client_ip}\n"
#             elif data.startswith("STAT"):
#                 if client_ip in clients_by_ip:
#                     clients_by_ip[client_ip]['last_message'] = time.time()
#                     response = "STAT ACK\n"
#             elif data == "HELLO MCP":
#                 response = "HELLO CCP\n"
#             elif data == "STATUS REPORT":
#                 response = "STATUS OK\n"
#             elif data == "LOCATION UPDATE":
#                 response = "LOCATION ACK\n"
#             else:
#                 response = "UNKNOWN COMMAND\n"

#             conn.send(response.encode())
#     except socket.error as e:
#         logging.error(f"Socket error: {e}")
#     finally:
#         if client_ip in clients_by_ip:
#             del clients_by_ip[client_ip]  # Remove from IP map
#         conn.close()
#         logging.info(f"Connection with CCP at {addr} closed")

# def send_status():
#     while True:
#         for client_ip, client_info in list(clients_by_ip.items()):
#             conn = client_info['conn']
#             if time.time() - client_info['last_message'] > timeout_interval:
#                 logging.warning(f"Client {client_ip} is unresponsive. Removing from list.")
#                 conn.close()
#                 del clients_by_ip[client_ip]
#                 continue
#             if client_info['type'] == 'train':
#                 try:
#                     conn.send("STAT\n".encode())
#                 except socket.error as e:
#                     logging.error(f"Socket error: {e}")
#                     conn.close()
#                     del clients_by_ip[client_ip]
#         time.sleep(status_interval)

# def send_command_to_ccp(ip_address, command):
#     client_info = clients_by_ip.get(ip_address)
#     if client_info:
#         try:
#             client_info['conn'].send(f"{command}\n".encode())
#             logging.info(f"Sent command '{command}' to CCP at {ip_address}")
#         except socket.error as e:
#             logging.error(f"Failed to send command to {ip_address}: {e}")
#             client_info['conn'].close()
#             del clients_by_ip[ip_address]
#     else:
#         logging.warning(f"No active CCP found at {ip_address}")

# def start_mcp(port):
#     host = 'localhost'
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server_socket.bind((host, port))
#     server_socket.listen(5)
#     logging.info(f"MCP started on port {port}")

#     try:
#         while True:
#             conn, addr = server_socket.accept()
#             threading.Thread(target=handle_ccp_connection, args=(conn, addr)).start()
#     except Exception as e:
#         logging.error(f"Error in MCP on port {port}: {e}")
#     finally:
#         server_socket.close()

# def command_input_listener():
#     while True:
#         user_input = input("Enter command (format: IP COMMAND): ").strip()
#         if user_input:
#             try:
#                 ip_address, command = user_input.split(maxsplit=1)
#                 send_command_to_ccp(ip_address, command)
#             except ValueError:
#                 logging.warning("Invalid input. Use format: IP COMMAND")

# def graceful_shutdown(signal_received, frame):
#     logging.info('SIGINT or CTRL-C detected. Shutting down gracefully...')
#     for client_ip, client_info in clients_by_ip.items():
#         client_info['conn'].close()
#     logging.info('All connections closed.')
#     exit(0)

# if __name__ == "__main__":
#     signal(SIGINT, graceful_shutdown)
    
#     port = 52002  # Single port for all connections
#     threading.Thread(target=start_mcp, args=(port,)).start()

#     threading.Thread(target=send_status).start()
#     threading.Thread(target=command_input_listener).start()  # Start listening for manual commands

# import socket
# import threading
# import time

# clients = {}
# client_id_counter = 0
# status_interval = 2  # seconds
# timeout_interval = 3  # seconds

# def assign_id():
#     global client_id_counter
#     client_id_counter += 1
#     return client_id_counter

# def handle_ccp_connection(conn, addr):
#     print(f"Connected to CCP at {addr}")
#     client_id = None

#     while True:
#         try:
#             data = conn.recv(1024).decode().strip()
#             if not data:
#                 print(f"Connection lost with CCP at {addr}")
#                 conn.close()
#                 if client_id in clients:
#                     del clients[client_id]
#                 return
            
#             print(f"Received from CCP: {data}")
#             response = "UNKNOWN COMMAND\n"

#             if data == "TRIN":
#                 client_id = assign_id()
#                 clients[client_id] = {'conn': conn, 'type': 'train', 'last_message': time.time()}
#                 response = f"ACKN {client_id}\n"
#             elif data == "STIN":
#                 client_id = assign_id()
#                 clients[client_id] = {'conn': conn, 'type': 'station', 'last_message': time.time()}
#                 response = f"ACKN {client_id}\n"
#             elif data.startswith("STAT"):
#                 if client_id:
#                     clients[client_id]['last_message'] = time.time()
#                     response = "STAT ACK\n"
#             elif data == "HELLO MCP":
#                 response = "HELLO CCP\n"
#             elif data == "STATUS REPORT":
#                 response = "STATUS OK\n"
#             elif data == "LOCATION UPDATE":
#                 response = "LOCATION ACK\n"
#             else:
#                 response = "UNKNOWN COMMAND\n"

#             conn.send(response.encode())
#         except socket.error as e:
#             print(f"Socket error: {e}")
#             conn.close()
#             if client_id in clients:
#                 del clients[client_id]
#             return

# def send_status():
#     while True:
#         for client_id, client_info in list(clients.items()):
#             conn = client_info['conn']
#             if time.time() - client_info['last_message'] > timeout_interval:
#                 print(f"Client {client_id} is unresponsive. Removing from list.")
#                 conn.close()
#                 del clients[client_id]
#                 continue
#             if client_info['type'] == 'train':
#                 try:
#                     conn.send("STAT\n".encode())
#                 except socket.error as e:
#                     print(f"Socket error: {e}")
#                     conn.close()
#                     del clients[client_id]
#         time.sleep(status_interval)

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
#     ports = [52002, 52003, 52004, 52005, 52006, 52007, 52008, 52009]  # Expanded list of ports
#     for port in ports:
#         threading.Thread(target=start_mcp, args=(port,)).start()

#     threading.Thread(target=send_status).start()


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
