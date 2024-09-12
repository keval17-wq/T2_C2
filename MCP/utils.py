import socket
import json

def create_socket(port):
    print(f"Creating UDP socket on port {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"UDP socket created on port {port}")
    return sock

def send_message(address, message):
    print(f"Sending UDP message to {address}: {message}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(message).encode('utf-8'), address)

def receive_message(sock):
    print("Receiving UDP message...")
    data, address = sock.recvfrom(1024)
    message = json.loads(data.decode('utf-8'))
    print(f"Message received from {address}: {message}")
    return message, address

def log_event(event_type, details):
    print(f"[{event_type}] - {details}")
