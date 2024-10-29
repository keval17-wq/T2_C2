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
    'BR05': ('127.0.0.1', 3005),
    # ... Add other BRs as needed
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

# Track map with both next and previous blocks for clockwise and anti-clockwise navigation
track_map = {
    'block_1': {'station': 'ST01', 'next_block': 'block_2', 'previous_block': 'block_10', 'turn': False},
    'block_2': {'station': 'ST02', 'next_block': 'block_3', 'previous_block': 'block_1', 'turn': False},
    'block_3': {'station': 'ST03', 'next_block': 'block_4', 'previous_block': 'block_2', 'turn': True, 'turn_severity': 0.5},
    'block_4': {'station': 'ST04', 'next_block': 'block_5', 'previous_block': 'block_3', 'turn': False},
    'block_5': {'station': 'ST05', 'next_block': 'block_6', 'previous_block': 'block_4', 'turn': False},
    'block_6': {'station': 'ST06', 'next_block': 'block_7', 'previous_block': 'block_5', 'turn': True, 'turn_severity': 0.7},
    'block_7': {'station': 'ST07', 'next_block': 'block_8', 'previous_block': 'block_6', 'turn': False},
    'block_8': {'station': 'ST08', 'next_block': 'block_9', 'previous_block': 'block_7', 'turn': False},
    'block_9': {'station': 'ST09', 'next_block': 'block_10', 'previous_block': 'block_8', 'turn': False},
    'block_10': {'station': 'ST10', 'next_block': 'block_1', 'previous_block': 'block_9', 'turn': False}
}

# Mapping from station_id to block_id
station_to_block = {block_info['station']: block_id for block_id, block_info in track_map.items()}

# Ordered list of all stations in track order
stations_in_order = ['ST01', 'ST02', 'ST03', 'ST04', 'ST05', 'ST06', 'ST07', 'ST08', 'ST09', 'ST10']

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
connected_stations = []  # List to maintain order
connected_stations_in_order = []  # Connected stations in track order
startup_queue = []  # Queue of BRs to process in startup protocol
current_startup_br = None  # BR currently being processed in startup
startup_in_progress = False  # Flag to indicate if startup protocol is in progress
override_triggered = False  # Flag to indicate if override has been triggered

# Dictionary to store current positions of BRs (Key: br_id, Value: station_id)
br_map = {}

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

# Broadcast a command to all connected CCPs
def broadcast_command(action):
    for ccp_id in connected_brs:
        s_mcp = increment_sequence_number('MCP', ccp_id)
        command = {
            "client_type": "CCP",  # Set to recipient's client_type
            "message": "EXEC",
            "client_id": ccp_id,
            "sequence_number": s_mcp,
            "action": action.upper()
        }
        send_message(ccp_ports[ccp_id], command)
    print(f"Broadcast command '{action}' sent to all connected BRs.")

# Send a specific command to a single BR
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
        send_message(ccp_ports[br_id], command)
        print(f"Command '{action}' sent to {br_id}.")
    else:
        print(f"BR ID {br_id} not connected.")

# Send a command to a station
def send_command_to_station(station_id, action, message_type, br_id):
    s_mcp = increment_sequence_number('MCP', station_id)
    command = {
        "client_type": "STC",
        "message": message_type,
        "client_id": station_id,
        "sequence_number": s_mcp,
        "action": action.upper(),
        "br_id": br_id
    }
    send_message(station_ports[station_id], command)
    print(f"Sent '{action}' command to Station {station_id} for BR {br_id}.")

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
    global current_startup_br, connected_stations_in_order
    station_id = message['client_id']
    message_type = message['message']
    print(f"{message_type} message received from Station {station_id}")

    s_stc = message['sequence_number']
    sequence_numbers[(station_id, 'MCP')] = s_stc
    s_mcp = increment_sequence_number('MCP', station_id)

    if message_type == 'STIN':
        print(f"Station {station_id} initialized.")
        # Acknowledge the station initialization
        ack_command = {
            "client_type": "STC",
            "message": "AKIN",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)
        if station_id not in connected_stations:
            connected_stations.append(station_id)
            # Rebuild connected_stations_in_order based on track order
            connected_stations_in_order = [st for st in stations_in_order if st in connected_stations]
            print(f"Connected Stations in order: {connected_stations_in_order}")
            check_startup_completion()

    elif message_type == 'TRIP':
        # Acknowledge the TRIP message from the station
        ack_command = {
            "client_type": "STC",
            "message": "AKTR",
            "client_id": station_id,
            "sequence_number": s_mcp
        }
        send_message(station_ports[station_id], ack_command)

        if current_startup_br is not None:
            # Handle TRIP message during startup
            br_map[current_startup_br] = station_id  # Store the current station for the BR
            print(f"BR {current_startup_br} is at Station {station_id}")
            print_current_positions()
            # Proceed to next BR in startup queue
            current_startup_br = None
            process_next_startup_br()
        else:
            # Handle TRIP message during normal operations
            if station_id not in connected_stations_in_order:
                print(f"Station {station_id} is not in connected stations.")
                return

            index = connected_stations_in_order.index(station_id)
            previous_index = index - 1 if index > 0 else len(connected_stations_in_order) - 1
            previous_station = connected_stations_in_order[previous_index]

            br_found = False
            for br_id, current_station in br_map.items():
                if current_station == previous_station:
                    # Update the BR's position to the current station
                    br_map[br_id] = station_id
                    print(f"BR {br_id} arrived at Station {station_id}")
                    print_current_positions()

                    # Send commands to BR as well 
                    slow_command = {
                        "client_type": "CCP",
                        "message": "EXEC",
                        "client_id": br_id,
                        "sequence_number": s_mcp,
                        "action": 'FSLOWC'  # Action based on track conditions
                    }
                    send_message(ccp_ports[br_id], slow_command)

                    # Send door open and light on commands to the station
                    send_command_to_station(station_id, "OPEN", "DOOR", br_id)
                    send_command_to_station(station_id, "ON", "EXEC", br_id)

                    # After 6 seconds, send door close and light off commands, and send FSLOWC to BR
                    threading.Timer(6.0, handle_departure, args=(station_id, br_id)).start()

                    br_found = True
                    break  # Exit after finding the correct BR for this TRIP

            if not br_found:
                print(f"No BR expected at Station {station_id} at this time.")

    elif message_type == 'STAT':
        print(f"Station {station_id} STAT received.")
        ack_command = {
            "client_type": "STC",
            "message": "AKST",
            "client_id": station_id,
            "sequence_number": s_mcp
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
    elif message_type == 'AKEX':
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

def handle_departure(station_id, br_id):
    # Send door close and light off commands to the station
    send_command_to_station(station_id, "CLOSE", "DOOR", br_id)
    send_command_to_station(station_id, "OFF", "EXEC", br_id)

    # Send FSLOWC command to the BR to proceed to the next station
    action = determine_action_for_br(br_id)
    send_command_to_br(br_id, action)

# Determine action for BR based on track map and connected stations
def determine_action_for_br(br_id):
    station_id = br_map.get(br_id)
    if station_id:
        # Get the index of the current station in connected_stations_in_order
        if station_id in connected_stations_in_order:
            index = connected_stations_in_order.index(station_id)
            # Get the next station in connected_stations_in_order
            next_index = (index + 1) % len(connected_stations_in_order)
            next_station_id = connected_stations_in_order[next_index]
        else:
            print(f"Current station {station_id} of BR {br_id} is not in connected stations.")
            return "FFASTC"

        # Get the block associated with the next station
        next_block_id = station_to_block.get(next_station_id)
        if next_block_id:
            next_block_info = track_map.get(next_block_id)
            if next_block_info:
                if next_block_info.get('turn'):
                    severity = next_block_info.get('turn_severity', 0)
                    # Decide to send FSLOWC command based on severity
                    if severity >= 0.5:
                        return "FSLOWC"
                    else:
                        return "FFASTC"
                else:
                    return "FFASTC"
            else:
                print(f"Block {next_block_id} not found in track map.")
                return "FFASTC"
        else:
            print(f"Next station {next_station_id} not associated with any block.")
            return "FFASTC"
    else:
        print(f"BR {br_id} location unknown.")
        return "FFASTC"  # Default action

# Print current positions of BRs
def print_current_positions():
    print("Current Positions of Blade Runners:")
    for br_id, station_id in br_map.items():
        print(f"BR {br_id} is at Station {station_id}")

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
    # Print current positions after startup
    print("Starting normal operations...")
    print_current_positions()
    # Send initial commands to BRs to start moving
    broadcast_start()

# Broadcast START command to all BRs to continue to the next station
def broadcast_start():
    for br_id in br_map.keys():
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

if __name__ == "__main__":
    start_mcp()

