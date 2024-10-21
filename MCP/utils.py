import socket
import json
import random

# Track sequence numbers for each system
sequence_ranges = {
    "mcp": (1000, 1010), # Starting point for MCP sequence numbers
    "ccp": (2000, 2010), # Starting point for CCP sequence numbers
    "cpc": (3000, 3010), # Starting point for CPC sequence numbers
    "stc": (4000, 4010)  # Starting point for STC sequence numbers
}

sequence_tracker = {
    "mcp": 0,
    "ccp": 0,
    "cpc": 0,
    "stc": 0
}

def create_socket(port):
    print(f"Creating UDP socket on port {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"UDP socket created on port {port}")
    return sock

# def send_message(address, message):
#     print(f"Sending UDP message to {address}: {message}")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.sendto(json.dumps(message).encode('utf-8'), address)

def send_message(address, message):
    client_type = message.get("client_type")
    # message["sequence_number"] = increment_sequence(client_type)
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

def initialise_sequence(client_type):
    if client_type in sequence_ranges and sequence_tracker[client_type] == 0:
        start, end = sequence_ranges[client_type]
        random_sequence_number = random.randint(start, end)
        sequence_tracker[client_type] = random_sequence_number
        return random_sequence_number
    elif client_type in sequence_tracker:
        return sequence_tracker[client_type]  # Return the existing sequence number

def increment_sequence(client_type):
    if client_type in sequence_tracker:
        # Increment and check if it exceeds the valid range
        sequence_tracker[client_type] += 1
        print(f"Incremented sequence for {client_type}. New value: {sequence_tracker[client_type]}")
        if sequence_tracker[client_type] >= 2000:  # Ensure it doesn't reach CCP range
            sequence_tracker[client_type] = 1000  # Reset to the beginning of MCP range
        return sequence_tracker[client_type]
