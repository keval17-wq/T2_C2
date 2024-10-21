# expect from station 

import socket
import threading
import random
from utils import create_socket, receive_message, send_message, log_event
import time

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('127.0.0.1', 3001),
    'BR02': ('127.0.0.1', 3002),
    'BR03': ('127.0.0.1', 3003),
    'BR04': ('127.0.0.1', 3004),
    'BR05': ('127.0.0.1', 3005)
}

# Static port mapping for Stations
station_ports = {
    'ST01': ('127.0.0.1', 4001),
    'ST02': ('127.0.0.1', 4002),
    'ST03': ('127.0.0.1', 4003),
    'ST04': ('127.0.0.1', 4004),
    'ST05': ('127.0.0.1', 4005),
    'ST06': ('127.0.0.1', 4006),
    'ST07': ('127.0.0.1', 4007),
    'ST08': ('127.0.0.1', 4008),
    'ST09': ('127.0.0.1', 4009),
    'ST10': ('127.0.0.1', 4010)
}

# Sequence numbers per client and per direction
sequence_numbers = {
    # Key: (sender, receiver), Value: sequence_number
}

def increment_sequence_number(sender, receiver):
    key = (sender, receiver)
    if key not in sequence_numbers:
        sequence_numbers[key] = random.randint(1000, 30000)
    else:
        sequence_numbers[key] += 1
    return sequence_numbers[key]

# State variables
connected_brs = set()
connected_stations = set()
startup_completed = False
br_locations = {}  # Key: br_id, Value: station_id

# Start MCP server and emergency handler thread
def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_socket(2000)  # MCP listens on port 2000
    print("MCP listening on port 2000")

    # Start the emergency command thread
    emergency = threading.Thread(target=emergency_command_handler)
    emergency.daemon = True  # Ensure this thread stops when the main program exits
    emergency.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_message(mcp_socket)
        handle_message(address, message)

# Handle emergency commands (running in parallel)
def emergency_command_handler():
    while True:
        # Simulate emergency command handling, with target BR selection
        emergency_input = input("Enter command (e.g., 'BR01 STOPC' or 'ALL FFASTC'): ").strip()
        if emergency_input:
            process_command(emergency_input)

        time.sleep(1)

# Process the user input command
def process_command(emergency_input):
    try:
        # Parse the input command
        parts = emergency_input.split()
        if len(parts) == 2:
            target, action = parts
            if target.upper() == 'ALL':
                # Broadcast to all BRs
                broadcast_command(action)
            elif target.startswith("BR"):
                # Send command to specific BR
                send_command_to_br(target.upper(), action)
            else:
                print("Invalid target. Use 'BR01' or 'ALL'.")
        else:
            print("Invalid input format. Use 'BR01 FFASTC' or 'ALL STOPC'.")
    except Exception as e:
        print(f"Error processing command: {e}")

# Broadcast a command to all CCPs
def broadcast_command(action):
    for ccp_id, address in ccp_ports.items():
        s_mcp = increment_sequence_number('MCP', ccp_id)
        command = {
            "client_type": "CCP",  # Set to recipient's client_type
            "message": "EXEC",
            "client_id": ccp_id,
            "sequence_number": s_mcp,
            "action": action.upper()
        }
        send_message(address, command)
    print(f"Broadcast command '{action}' sent to all CCPs.")

# Send a specific command to a single BR
def send_command_to_br(br_id, action):
    if br_id in ccp_ports:
        s_mcp = increment_sequence_number('MCP', br_id)
        command = {
            "client_type": "CCP",  # Set to recipient's client_type
            "message": "EXEC",
            "client_id": br_id,
            "sequence_number": s_mcp,
            "action": action.upper()
        }
        send_message(ccp_ports[br_id], command)
        print(f"Command '{action}' sent to {br_id}.")
    else:
        print(f"BR ID {br_id} not recognized.")

# Handle incoming messages
def handle_message(address, message):
    client_type = message['client_type']
    if client_type == 'CCP':
        print(f"Handling CCP message from {address}")
        handle_ccp_message(address, message)
    elif client_type == 'STC':
        print(f"Handling Station message from {address}")
        handle_station_message(address, message)
    else:
        print(f"Unknown client_type: {client_type}")

# Handle CCP messages
def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']
    s_ccp = message['sequence_number']
    # Store the CCP's sequence number
    sequence_numbers[(ccp_id, 'MCP')] = s_ccp
    s_mcp = increment_sequence_number('MCP', ccp_id)

    if message['message'] == 'CCIN':
        # Handle initialization: Send AKIN
        print(f"CCP {ccp_id} initialized.")
        ack_command = {
            "client_type": "CCP",  # Recipient's client_type
            "message": "AKIN",
            "client_id": ccp_id,
            "sequence_number": s_mcp
        }
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge initialization
        if ccp_id not in connected_brs:
            connected_brs.add(ccp_id)
            print(f"Added {ccp_id} to connected BRs.")
            check_startup_completion()
    elif message['message'] == 'STAT':
        print(f"BR {ccp_id} STAT received.")
        ack_command = {
            "client_type": "CCP",
            "message": "AKST",
            "client_id": ccp_id,
            "sequence_number": s_mcp
        }
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge status
        if message['status'] == 'ERR':
            # Handle error status
            broadcast_command("STOPC")
            send_command_to_br(ccp_id, "DISCONNECT")
    elif message['message'] == 'AKEX':
        print(f"BR {ccp_id} acknowledged command.")
    else:
        # Handle unknown messages
        noip_message = {
            "client_type": "CCP",
            "message": "NOIP",
            "client_id": ccp_id,
            "sequence_number": s_mcp
        }
        send_message(ccp_ports[ccp_id], noip_message)

# Handle Station messages
def handle_station_message(address, message):
    log_event("Station Message Received", message)
    station_id = message['client_id']
    s_stc = message['sequence_number']
    sequence_numbers[(station_id, 'MCP')] = s_stc
    s_mcp = increment_sequence_number('MCP', station_id)

    if message['message'] == 'STIN':
        # Handle initialization: Send AKIN
        print(f"Station {station_id} initialized.")
        ack_command = {
            "client_type": "STC",  # Recipient's client_type
            "message": "AKIN",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)
        if station_id not in connected_stations:
            connected_stations.add(station_id)
            print(f"Added {station_id} to connected Stations.")
            check_startup_completion()
    elif message['message'] == 'TRIP':
        # Handle TRIP messages
        print(f"TRIP message received from Station {station_id}")
        ack_command = {
            "client_type": "STC",
            "message": "AKTR",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)
        # Update BR location
        br_id = message.get('br_id')
        if br_id:
            br_locations[br_id] = station_id
            print(f"BR {br_id} is at station {station_id}")
            check_all_brs_positioned()
    elif message['message'] == 'STAT':
        print(f"Station {station_id} STAT received.")
        ack_command = {
            "client_type": "STC",
            "message": "AKST",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)
        if message['status'] == 'ERR':
            error_command = {
                "client_type": "STC",
                "message": "EXEC",
                "client_id": station_id,
                "sequence_number": s_mcp,
                "action": "BLINK",
                "br_id": ""
            }
            send_message(station_ports[station_id], error_command)
    elif message['message'] == 'AKEX':
        print(f"Station {station_id} acknowledged command.")
    else:
        # Handle unknown messages
        noip_message = {
            "client_type": "STC",
            "message": "NOIP",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], noip_message)

# Check if startup protocol can be initiated
def check_startup_completion():
    global startup_completed
    if not startup_completed and connected_brs and connected_stations:
        print("All BRs and Stations are connected. Starting startup protocol...")
        startup_completed = True
        start_startup_protocol()

# Start the startup protocol
def start_startup_protocol():
    for br_id in connected_brs:
        send_command_to_br(br_id, "FSLOWC")
        print(f"Sent FSLOWC command to {br_id} to find initial position.")

# Check if all BRs have been positioned
def check_all_brs_positioned():
    if len(br_locations) == len(connected_brs):
        print("All BRs have been positioned. Starting normal operations.")
        start_normal_operations()

# Start normal operations
def start_normal_operations():
    # Send initial commands to BRs to start moving
    broadcast_start()

# Broadcast START command to all BRs to continue to the next station
def broadcast_start():
    for ccp_id, address in ccp_ports.items():
        s_mcp = increment_sequence_number('MCP', ccp_id)
        start_command = {
            "client_type": "CCP",
            "message": "EXEC",
            "client_id": ccp_id,
            "sequence_number": s_mcp,
            "action": "FFASTC"  # BR moves forward fast, door is closed
        }
        send_message(address, start_command)
    print(f"START command broadcasted to all CCPs.")

# Control station doors
def control_station_doors(station_id, action):
    s_mcp = increment_sequence_number('MCP', station_id)
    door_command = {
        "client_type": "STC",
        "message": "DOOR",
        "client_id": station_id,
        "sequence_number": s_mcp,
        "action": action
    }
    send_message(station_ports[station_id], door_command)

if __name__ == "__main__":
    start_mcp()
