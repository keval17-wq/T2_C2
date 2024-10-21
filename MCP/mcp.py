import socket
import threading
import time
from utils import create_socket, send_message, receive_message, log_event

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('127.0.0.1', 3001),
    'BR02': ('127.0.0.1', 3002),
    'BR03': ('127.0.0.1', 3003),
    'BR04': ('127.0.0.1', 3004),
    'BR05': ('127.0.0.1', 3005)
}

# Track missed heartbeats
heartbeat_missed = {ccp_id: 0 for ccp_id in ccp_ports}

# Sequence number tracking
sequence_number = 1000

def generate_sequence_number():
    global sequence_number
    sequence_number += 1
    return sequence_number

# Start MCP server and emergency handler thread
def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_socket(2000)  # MCP listens on port 2000
    print("MCP listening on port 2000")

    # Start the heartbeat monitoring thread
    heartbeat_thread = threading.Thread(target=send_heartbeat_requests)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    # Start the manual command input thread
    manual_input_thread = threading.Thread(target=handle_manual_commands)
    manual_input_thread.daemon = True
    manual_input_thread.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_message(mcp_socket)
        handle_message(message, address)

# Send status requests (heartbeat) to all CCPs every 2 seconds
def send_heartbeat_requests():
    while True:
        for ccp_id, address in ccp_ports.items():
            status_request = {
                "client_type": "mcp",
                "message": "STRQ",
                "client_id": ccp_id,
                "sequence_number": generate_sequence_number()
            }
            send_message(address, status_request)
            print(f"Sent STRQ (heartbeat) to {ccp_id}")

            # Increment missed heartbeat counter if no response
            heartbeat_missed[ccp_id] += 1
            if heartbeat_missed[ccp_id] >= 3:
                print(f"CCP {ccp_id} missed 3 heartbeats. Triggering emergency stop.")
                send_emergency_stop(ccp_id)

        time.sleep(2)  # Wait 2 seconds before sending the next round of STRQ

# Handle manual commands from the user
def handle_manual_commands():
    while True:
        command_input = input("Enter a command (e.g., 'BR01 FSLOWC' or 'ALL STOPC'): ").strip()
        if command_input:
            process_manual_command(command_input)

# Process manual commands and send to CCPs
def process_manual_command(command_input):
    parts = command_input.split()
    if len(parts) == 2:
        target, action = parts
        if target.upper() == "ALL":
            broadcast_command(action)
        elif target in ccp_ports:
            send_command_to_br(target, action)
        else:
            print(f"Unknown target: {target}")
    else:
        print("Invalid command format. Use 'BR01 FSLOWC' or 'ALL STOPC'.")

# Broadcast a command to all CCPs
def broadcast_command(action):
    for ccp_id, address in ccp_ports.items():
        command = {
            "client_type": "mcp",
            "message": "EXEC",
            "client_id": ccp_id,
            "sequence_number": generate_sequence_number(),
            "action": action.upper()
        }
        send_message(address, command)
        print(f"Sent '{action}' to all CCPs")

# Send a command to a specific CCP (BR)
def send_command_to_br(br_id, action):
    if br_id in ccp_ports:
        command = {
            "client_type": "mcp",
            "message": "EXEC",
            "client_id": br_id,
            "sequence_number": generate_sequence_number(),
            "action": action.upper()
        }
        send_message(ccp_ports[br_id], command)
        print(f"Sent '{action}' to {br_id}")
    else:
        print(f"Unknown BR ID: {br_id}")

# Handle incoming messages from CCPs
def handle_message(message, address):
    if message['client_type'] == 'ccp':
        handle_ccp_message(message)

# Handle CCP messages, including STAT responses for heartbeats
def handle_ccp_message(message):
    ccp_id = message['client_id']
    if message['message'] == 'STAT':
        print(f"Received STAT from {ccp_id}")
        heartbeat_missed[ccp_id] = 0  # Reset the heartbeat missed counter
        send_acknowledgement(ccp_id, "AKST")  # Send acknowledgement
    elif message['message'] == 'CCIN':
        print(f"CCP {ccp_id} initialized.")
        send_acknowledgement(ccp_id, "AKIN")
    elif message['message'] == 'EXEC':
        print(f"Received EXEC command response from {ccp_id}")

# Send an acknowledgement (e.g., for STAT or CCIN messages)
def send_acknowledgement(client_id, ack_type):
    ack_message = {
        "client_type": "mcp",
        "message": ack_type,
        "client_id": client_id,
        "sequence_number": generate_sequence_number()
    }
    send_message(ccp_ports[client_id], ack_message)
    print(f"Sent {ack_type} to {client_id}")

# Send an emergency stop command to a specific BR
def send_emergency_stop(br_id):
    emergency_command = {
        "client_type": "mcp",
        "message": "EXEC",
        "client_id": br_id,
        "sequence_number": generate_sequence_number(),
        "action": "STOPC"
    }
    send_message(ccp_ports[br_id], emergency_command)
    print(f"Emergency stop sent to {br_id}")

if _name_ == "_main_":
    start_mcp()
