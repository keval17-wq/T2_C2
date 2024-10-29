import socket
import threading
import random
from utils import create_socket, receive_message, send_message, log_event
import time

# Static port mapping for Stations (remains the same)
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

# Track map for block management (remains the same)
track_map = {
    'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False},
    'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False},
    'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True, 'turn_severity': 0.5},
    'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False},
    'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False},
    'block_6': {'station': 'ST06', 'next_block': 'block_7', 'turn': True, 'turn_severity': 0.7},
    'block_7': {'station': 'ST07', 'next_block': 'block_8', 'turn': False},
    'block_8': {'station': 'ST08', 'next_block': 'block_9', 'turn': False},
    'block_9': {'station': 'ST09', 'next_block': 'block_10', 'turn': False},
    'block_10': {'station': 'ST10', 'next_block': 'block_1', 'turn': False}
}

# Initialize ccp_ports as an empty dictionary for dynamic additions
ccp_ports = {}

# Dictionary to track heartbeat status for each CCP
heartbeat_missed = {}

# Sequence numbers per client and per direction (remains the same)
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
startup_queue = []  # Queue of BRs to process in startup protocol
current_startup_br = None  # BR currently being processed in startup
startup_in_progress = False  # Flag to indicate if startup protocol is in progress
override_triggered = False  # Flag to indicate if override has been triggered
br_map = {}  # Key: br_id, Value: block_id

# Track initialized CCPs using a set
initialized_ccp = set()

def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_socket(2000)  # MCP listens on port 2000
    print("MCP listening on port 2000")

    # Start the heartbeat monitoring thread
    heartbeat_thread = threading.Thread(target=heartbeat_monitoring)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    # Start the emergency command thread
    emergency = threading.Thread(target=emergency_command_handler)
    emergency.daemon = True  # Ensure this thread stops when the main program exits
    emergency.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_message(mcp_socket)
        handle_message(address, message)

def heartbeat_monitoring():
    while True:
        for ccp_id in list(initialized_ccp):
            s_mcp = increment_sequence_number('MCP', ccp_id)
            status_request = {
                "client_type": "mcp",
                "message": "STRQ",
                "client_id": ccp_id,
                "sequence_number": s_mcp
            }
            if ccp_id in ccp_ports:
                send_message(ccp_ports[ccp_id], status_request)
                print(f"Sent STRQ (heartbeat) to {ccp_id}")
            else:
                print(f"CCP {ccp_id} not found in ccp_ports.")

            # Increment missed heartbeat counter
            heartbeat_missed[ccp_id] = heartbeat_missed.get(ccp_id, 0) + 1

            # If missed heartbeats >= 3, take action
            if heartbeat_missed[ccp_id] >= 3:
                print(f"CCP {ccp_id} missed {heartbeat_missed[ccp_id]} heartbeats. Triggering emergency stop.")
                send_emergency_stop(ccp_id)
        time.sleep(2)

def send_emergency_stop(br_id):
    s_mcp = increment_sequence_number('MCP', br_id)
    emergency_command = {
        "client_type": "CCP",
        "message": "EXEC",
        "client_id": br_id,
        "sequence_number": s_mcp,
        "action": "STOPC"
    }
    if br_id in ccp_ports:
        send_message(ccp_ports[br_id], emergency_command)
        print(f"Emergency stop sent to {br_id}")
    else:
        print(f"CCP {br_id} not found in ccp_ports.")

def emergency_command_handler():
    global override_triggered
    while True:
        # Simulate emergency command handling, with target BR selection
        emergency_input = input("Enter command (e.g., 'BR01 STOPC', 'ALL FFASTC', or 'OVERRIDE'): ").strip()
        if emergency_input:
            if emergency_input.upper() == 'OVERRIDE':
                override_triggered = True
                print("Override triggered. Proceeding with startup protocol using connected BRs.")
                check_startup_completion()
            else:
                process_command(emergency_input)
        time.sleep(1)

def process_command(emergency_input):
    try:
        # Parse the input command
        parts = emergency_input.split()
        if len(parts) == 2:
            target, action = parts
            if target.upper() == 'ALL':
                # Broadcast to all connected BRs
                broadcast_command(action)
            elif target.startswith("BR"):
                # Send command to specific BR
                send_command_to_br(target.upper(), action)
            else:
                print("Invalid target. Use 'BR01' or 'ALL'.")
        else:
            print("Invalid input format. Use 'BR01 FFASTC', 'ALL STOPC', or 'OVERRIDE'.")
    except Exception as e:
        print(f"Error processing command: {e}")

def broadcast_command(action):
    for ccp_id in connected_brs:
        send_command_to_br(ccp_id, action)
    print(f"Broadcast command '{action}' sent to all connected BRs.")

def send_command_to_br(br_id, action):
    if br_id in connected_brs:
        s_mcp = increment_sequence_number('MCP', br_id)
        command = {
            "client_type": "CCP",  # Recipient's client_type
            "message": "EXEC",
            "client_id": br_id,
            "sequence_number": s_mcp,
            "action": action.upper()
        }
        if br_id in ccp_ports:
            send_message(ccp_ports[br_id], command)
            print(f"Command '{action}' sent to {br_id}.")
        else:
            print(f"BR ID {br_id} not found in ccp_ports.")
    else:
        print(f"BR ID {br_id} not connected.")

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

def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']
    s_ccp = message['sequence_number']
    s_mcp = increment_sequence_number('MCP', ccp_id)

    # Store the CCP's address
    ccp_ports[ccp_id] = address

    # Initialize heartbeat_missed for the new ccp_id
    if ccp_id not in heartbeat_missed:
        heartbeat_missed[ccp_id] = 0

    # Add ccp_id to initialized_ccp
    initialized_ccp.add(ccp_id)

    # Store the CCP's sequence number
    sequence_numbers[(ccp_id, 'MCP')] = s_ccp

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
            startup_queue.append(ccp_id)
            print(f"Added {ccp_id} to connected BRs.")
            print(f"Currently connected BRs: {sorted(connected_brs)}")  # Print connected BRs
            check_startup_completion()
    elif message['message'] == 'STAT':
        print(f"BR {ccp_id} STAT received.")
        # Reset the heartbeat missed counter
        heartbeat_missed[ccp_id] = 0

        ack_command = {
            "client_type": "CCP",
            "message": "AKST",
            "client_id": ccp_id,
            "sequence_number": s_mcp
        }
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge status
        if message.get('status') == 'ERR':
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

def handle_station_message(address, message):
    global current_startup_br
    log_event("Station Message Received", message)
    station_id = message['client_id']
    s_stc = message['sequence_number']
    sequence_numbers[(station_id, 'MCP')] = s_stc

    if message['message'] == 'TRIP':
        print(f"TRIP message received from Station {station_id}")

        # Acknowledge the TRIP message from the station
        ack_command = {
            "client_type": "STC",
            "message": "AKTR",
            "client_id": station_id,
            "sequence_number": increment_sequence_number('MCP', station_id)
        }
        send_message(station_ports[station_id], ack_command)

        if current_startup_br:
            # Handle TRIP message during startup as before
            block_id = get_block(station_id)
            if block_id:
                br_map[current_startup_br] = block_id  # Store block_id instead of station_id
                print(f"BR {current_startup_br} is at Station {station_id} (Block: {block_id})")
                print_current_positions()
                current_startup_br = None  # Reset current BR
                process_next_startup_br()
            else:
                print(f"Station {station_id} not found in track map.")
        else:
            # Handle TRIP message during normal operations
            # Try to find which BR is expected at this station
            br_found = False
            for br_id, current_block_id in br_map.items():
                # Get the next block for this BR, considering only connected stations
                next_block_id = get_next_block(current_block_id)
                if next_block_id:
                    next_block_info = track_map.get(next_block_id)
                    next_station_id = next_block_info.get('station')
                    if next_station_id == station_id:
                        # Update BR's location
                        br_map[br_id] = next_block_id
                        print(f"BR {br_id} arrived at Station {station_id} (Block: {next_block_id})")
                        print_current_positions()

                        # Send FSLOWC command to the BR
                        action = "FSLOWC"
                        send_command_to_br(br_id, action)

                        br_found = True
                        break
            if not br_found:
                print(f"No BR expected at Station {station_id} at this time.")

    elif message['message'] == 'STIN':
        print(f"Station {station_id} initialized.")
        # Acknowledge the station initialization
        ack_command = {
            "client_type": "STC",
            "message": "AKIN",
            "client_id": station_id,
            "sequence_number": increment_sequence_number('MCP', station_id)
        }
        send_message(station_ports[station_id], ack_command)
        if station_id not in connected_stations:
            connected_stations.add(station_id)
            print(f"Added {station_id} to connected Stations.")
            check_startup_completion()

    elif message['message'] == 'STAT':
        print(f"Station {station_id} STAT received.")
        ack_command = {
            "client_type": "STC",
            "message": "AKST",
            "client_id": station_id,
            "sequence_number": increment_sequence_number('MCP', station_id)
        }
        send_message(station_ports[station_id], ack_command)
        if message.get('status') == 'ERR':
            error_command = {
                "client_type": "STC",
                "message": "EXEC",
                "client_id": station_id,
                "sequence_number": increment_sequence_number('MCP', station_id),
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
            "sequence_number": s_stc
        }
        send_message(station_ports[station_id], noip_message)

def get_block(station_id):
    for block_id, block_info in track_map.items():
        if block_info['station'] == station_id:
            return block_id
    return None

def get_next_block(current_block_id):
    next_block_id = current_block_id
    visited_blocks = set()
    while True:
        if next_block_id in visited_blocks:
            return None  # Prevent infinite loops
        visited_blocks.add(next_block_id)

        current_block_info = track_map.get(next_block_id)
        if current_block_info:
            next_block_id = current_block_info.get('next_block')
            if not next_block_id or next_block_id == current_block_id:
                return None  # End of the track or loop detected
            next_block_info = track_map.get(next_block_id)
            next_station_id = next_block_info.get('station')
            if next_station_id in connected_stations:
                return next_block_id
            else:
                # Skip to the next block
                continue
        else:
            return None

def check_startup_completion():
    global startup_in_progress
    if not startup_in_progress:
        if connected_brs and connected_stations:
            startup_in_progress = True
            print("All required devices are connected. Starting startup protocol...")
            process_next_startup_br()
        elif override_triggered:
            if connected_brs:
                startup_in_progress = True
                print("Override activated. Starting startup protocol with connected BRs...")
                process_next_startup_br()
            else:
                print("Override activated, but no BRs are connected.")
        else:
            print("Waiting for required devices to connect...")

def process_next_startup_br():
    global current_startup_br
    if startup_queue:
        current_startup_br = startup_queue.pop(0)
        send_command_to_br(current_startup_br, "FSLOWC")
        print(f"Sent FSLOWC command to {current_startup_br} to find initial position.")
    else:
        current_startup_br = None  # No BR is currently being processed
        if startup_in_progress:
            print("Startup protocol completed with connected BRs.")
            start_normal_operations()

def start_normal_operations():
    # Send initial commands to BRs to start moving
    broadcast_start()

def broadcast_start():
    for br_id in br_map.keys():
        action = determine_action_for_br(br_id)
        send_command_to_br(br_id, action)
    print(f"START command broadcasted to all positioned BRs.")

def determine_action_for_br(br_id):
    block_id = br_map.get(br_id)
    if block_id:
        block_info = track_map.get(block_id)
        if block_info:
            if block_info.get('turn'):
                severity = block_info.get('turn_severity', 0)
                # Decide to send slow command based on severity
                return "FSLOWC"
            else:
                return "FFASTC"
        else:
            print(f"Block {block_id} not found in track map.")
            return "FFASTC"
    else:
        print(f"BR {br_id} location unknown.")
        return "FFASTC"  # Default action

def print_current_positions():
    print("Current Positions of Blade Runners:")
    for br_id, block_id in br_map.items():
        block_info = track_map.get(block_id, {})
        station_id = block_info.get('station', 'Unknown')
        print(f"BR {br_id} is at Block {block_id}, Station {station_id}")

if _name_ == "_main_":
    start_mcp()