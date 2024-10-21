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

# Static port mapping for Checkpoints
checkpoint_ports = {
    'CP01': ('127.0.0.1', 5001),
    'CP02': ('127.0.0.1', 5002),
    'CP03': ('127.0.0.1', 5003),
    'CP04': ('127.0.0.1', 5004),
    'CP05': ('127.0.0.1', 5005),
    'CP06': ('127.0.0.1', 5006),
    'CP07': ('127.0.0.1', 5007),
    'CP08': ('127.0.0.1', 5008),
    'CP09': ('127.0.0.1', 5009),
    'CP10': ('127.0.0.1', 5010)
}

# Track map for block management
track_map = {
    'block_1': {'checkpoint': 'CP01', 'station': 'ST01', 'next_block': 'block_2', 'turn': False},
    'block_2': {'checkpoint': 'CP02', 'station': 'ST02', 'next_block': 'block_3', 'turn': False},
    # Add more blocks as needed
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
connected_checkpoints = set()
br_locations = {}  # Key: br_id, Value: block_id
startup_queue = []  # Queue of BRs to process in startup protocol
current_startup_br = None  # BR currently being processed in startup
startup_in_progress = False  # Flag to indicate if startup protocol is in progress

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
    elif client_type == 'CPC':
        print(f"Handling Checkpoint message from {address}")
        handle_checkpoint_message(address, message)
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
            # Start processing if not already in progress
            if not current_startup_br:
                process_next_startup_br()
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
    elif message['message'] == 'TRIP':
        # Handle TRIP messages (if any)
        print(f"TRIP message received from Station {station_id}")
        ack_command = {
            "client_type": "STC",
            "message": "AKTR",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)
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

# Handle Checkpoint messages
def handle_checkpoint_message(address, message):
    log_event("Checkpoint Message Received", message)
    checkpoint_id = message['client_id']
    s_cpc = message['sequence_number']
    sequence_numbers[(checkpoint_id, 'MCP')] = s_cpc
    s_mcp = increment_sequence_number('MCP', checkpoint_id)

    if message['message'] == 'CPIN':
        # Handle initialization: Send AKIN
        print(f"Checkpoint {checkpoint_id} initialized.")
        ack_command = {
            "client_type": "CPC",  # Recipient's client_type
            "message": "AKIN",
            "client_id": checkpoint_id,
            "sequence_number": s_mcp
        }
        send_message(checkpoint_ports[checkpoint_id], ack_command)
        if checkpoint_id not in connected_checkpoints:
            connected_checkpoints.add(checkpoint_id)
            print(f"Added {checkpoint_id} to connected Checkpoints.")
    elif message['message'] == 'TRIP':
        print(f"TRIP signal received from {checkpoint_id}")
        ack_command = {
            "client_type": "CPC",
            "message": "AKTR",
            "client_id": checkpoint_id,
            "sequence_number": s_mcp
        }
        send_message(checkpoint_ports[checkpoint_id], ack_command)
        # Associate the TRIP with the current BR in the startup process
        if current_startup_br:
            block_id = get_block_by_checkpoint(checkpoint_id)
            if block_id:
                br_locations[current_startup_br] = block_id
                print(f"BR {current_startup_br} is at {checkpoint_id} (Block: {block_id})")
                print_current_positions()
                current_startup_br = None  # Reset current BR
                # Proceed to the next BR in the startup queue
                process_next_startup_br()
    elif message['message'] == 'STAT':
        print(f"Checkpoint {checkpoint_id} STAT received.")
        ack_command = {
            "client_type": "CPC",
            "message": "AKST",
            "client_id": checkpoint_id,
            "sequence_number": s_mcp
        }
        send_message(checkpoint_ports[checkpoint_id], ack_command)
        if message['status'] == 'ERR':
            error_command = {
                "client_type": "CPC",
                "message": "EXEC",
                "client_id": checkpoint_id,
                "sequence_number": s_mcp,
                "action": "BLINK",
                "br_id": ""
            }
            send_message(checkpoint_ports[checkpoint_id], error_command)
    elif message['message'] == 'AKEX':
        print(f"Checkpoint {checkpoint_id} acknowledged command.")
    else:
        # Handle unknown messages
        noip_message = {
            "client_type": "CPC",
            "message": "NOIP",
            "client_id": checkpoint_id,
            "sequence_number": s_mcp
        }
        send_message(checkpoint_ports[checkpoint_id], noip_message)

# Get block_id by checkpoint_id
def get_block_by_checkpoint(checkpoint_id):
    for block_id, block_info in track_map.items():
        if block_info['checkpoint'] == checkpoint_id:
            return block_id
    return None

# Process the next BR in the startup queue
def process_next_startup_br():
    global current_startup_br
    if startup_queue:
        current_startup_br = startup_queue.pop(0)
        send_command_to_br(current_startup_br, "FSLOWC")
        print(f"Sent FSLOWC command to {current_startup_br} to find initial position.")
    else:
        current_startup_br = None  # No BR is currently being processed

# Start normal operations
def start_normal_operations():
    # Send initial commands to BRs to start moving
    broadcast_start()

# Broadcast START command to all BRs to continue to the next checkpoint
def broadcast_start():
    for br_id in connected_brs:
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
    print(f"START command broadcasted to all CCPs.")

# Determine action for BR based on track map (e.g., handle turns)
def determine_action_for_br(br_id):
    block_id = br_locations.get(br_id)
    if block_id:
        block_info = track_map[block_id]
        if block_info.get('turn'):
            severity = block_info.get('turn_severity', 0)
            # Decide to send slow command
            return "FSLOWC"
        else:
            return "FFASTC"
    else:
        return "FFASTC"  # Default action

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

# Print current positions of BRs
def print_current_positions():
    print("Current Positions of Blade Runners:")
    for br_id, block_id in br_locations.items():
        block_info = track_map.get(block_id, {})
        checkpoint_id = block_info.get('checkpoint', 'Unknown')
        station_id = block_info.get('station', 'Unknown')
        print(f"BR {br_id} is at Block {block_id}, Checkpoint {checkpoint_id}, Station {station_id}")

if __name__ == "__main__":
    start_mcp()
