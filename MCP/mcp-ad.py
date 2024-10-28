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
    # Add more BRs as needed
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

# Track map for block management
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
startup_queue = []  # Queue of BRs to process in startup protocol
current_startup_br = None  # BR currently being processed in startup
startup_in_progress = False  # Flag to indicate if startup protocol is in progress
override_triggered = False  # Flag to indicate if override has been triggered
br_locations = {}  # Key: br_id, Value: block_id

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
            print("Invalid input format. Use 'BR01 FFASTC', 'ALL STOPC', or 'OVERRIDE'.")
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
            "client_type": "CCP",  # Recipient's client_type
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
            startup_queue.append(ccp_id)
            print(f"Added {ccp_id} to connected BRs.")
            print(f"Currently connected BRs: {sorted(connected_brs)}")  # Print connected BRs
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

        # Associate the TRIP with the current BR in the startup process
        if current_startup_br:
            block_id = get_block_by_station(station_id)
            if block_id:
                br_locations[current_startup_br] = block_id  # Store block_id instead of station_id
                print(f"BR {current_startup_br} is at Station {station_id} (Block: {block_id})")
                print_current_positions()
                current_startup_br = None  # Reset current BR
                process_next_startup_br()
            else:
                print(f"Station {station_id} not found in track map.")
        else:
            print(f"No BR is currently in startup process. TRIP from {station_id} ignored.")

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

# Get block_id by station_id
def get_block_by_station(station_id):
    for block_id, block_info in track_map.items():
        if block_info['station'] == station_id:
            return block_id
    return None

# Check if startup protocol can be initiated
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

# Process the next BR in the startup queue
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

# Start normal operations
def start_normal_operations():
    # Send initial commands to BRs to start moving
    broadcast_start()

# Broadcast START command to all BRs to continue to the next station
def broadcast_start():
    for br_id in br_locations.keys():
        s_mcp = increment_sequence_number('MCP', br_id)
        action = determine_action_for_br(br_id)
        start_command = {
            "client_type": "CCP",
            "message": "EXEC",
            "client_id": br_id,
            "sequence_number": s_mcp,
            "action": action  # Action based on track conditions
        }
        send_message(ccp_ports[br_id], start_command)
        print(f"Sent '{action}' command to {br_id}")
    print(f"START command broadcasted to all positioned BRs.")

# Determine action for BR based on track map (e.g., handle turns)
def determine_action_for_br(br_id):
    block_id = br_locations.get(br_id)
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

# Print current positions of BRs
def print_current_positions():
    print("Current Positions of Blade Runners:")
    for br_id, block_id in br_locations.items():
        block_info = track_map.get(block_id, {})
        station_id = block_info.get('station', 'Unknown')
        print(f"BR {br_id} is at Block {block_id}, Station {station_id}")

if __name__ == "__main__":
    start_mcp()
