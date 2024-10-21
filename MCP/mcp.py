import socket
import threading
from utils import create_socket, receive_message, send_message, log_event, initialise_sequence, increment_sequence, sequence_tracker
import time

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('127.0.0.1', 3001),
    'BR02': ('127.0.0.1', 3002),
    'BR03': ('127.0.0.1', 3003),
    'BR04': ('127.0.0.1', 3004),
    'BR05': ('127.0.0.1', 3005)
}

# Static port mapping for 10 stations
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

# Static port mapping for 10 checkpoints
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

# Track map for block management, handling turns and checkpoints
track_map = {
    'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False, 'is_checkpoint': True},
    'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False, 'is_checkpoint': True},
    'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True, 'turn_severity': 0.5, 'is_checkpoint': True},
    'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False, 'is_checkpoint': True},
    'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False, 'is_checkpoint': True},
    'block_6': {'station': 'ST06', 'next_block': 'block_7', 'turn': True, 'turn_severity': 0.7, 'is_checkpoint': True},
    'block_7': {'station': 'ST07', 'next_block': 'block_8', 'turn': False, 'is_checkpoint': True},
    'block_8': {'station': 'ST08', 'next_block': 'block_9', 'turn': False, 'is_checkpoint': True},
    'block_9': {'station': 'ST09', 'next_block': 'block_10', 'turn': False, 'is_checkpoint': True},
    'block_10': {'station': 'ST10', 'next_block': 'block_1', 'turn': False, 'is_checkpoint': True}
}

# Track occupancy to map which block is occupied by which BR
track_occupancy = {}

# Dictionary to track heartbeat status for each CCP
heartbeat_missed = {}

# Track sequence numbers for each system
sequence_numbers = {
    "mcp": 1000,  # Starting point for MCP sequence numbers
    "ccp": 2000,  # Starting point for CCP sequence numbers
    "cpc": 3000,  # Starting point for CPC sequence numbers
    "stc": 4000   # Starting point for STC sequence numbers
}

# Start MCP server and emergency handler thread
# def start_mcp():
#     print("Starting MCP...")
#     mcp_socket = create_socket(2000)  # MCP listens on port 2000
#     print("MCP listening on port 2000")

#     # Initialize MCP sequence number randomly
#     initialise_sequence("mcp")
#     print(f"MCP starting with initial sequence number: {sequence_tracker['mcp']}")

#     # Start the emergency command thread
#     emergency = threading.Thread(target=emergency_command_handler)
#     emergency.daemon = True  # Ensure this thread stops when the main program exits
#     emergency.start()

#     while True:
#         print("Waiting for messages...")
#         message, address = receive_message(mcp_socket)
#         print(f"Message received from {address}")
#         handle_message(address, message)
def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_socket(2000)  # MCP listens on port 2000
    print("MCP listening on port 2000")

    # Initialize MCP sequence number randomly
    initialise_sequence("mcp")
    print(f"MCP starting with initial sequence number: {sequence_tracker['mcp']}")

    while True:
        # Alternate between asking for manual input and listening for messages
        emergency_input = input("Enter command (e.g., 'BR01 STOPC' or 'FFASTC'): ").strip()
        if emergency_input:
            process_command(emergency_input)

        # Check if there are incoming messages to handle
        print("Waiting for messages...")
        mcp_socket.settimeout(2)  # Use a timeout to periodically return from blocking
        try:
            message, address = receive_message(mcp_socket)
            print(f"Message received from {address}")
            handle_message(address, message)
        except socket.timeout:
            # No messages received, continue the loop to check for manual commands
            pass


# Handle emergency commands (running in parallel)
def emergency_command_handler():
    while True:
        # Simulate emergency command handling, with target BR selection
        emergency_input = input("Enter command (e.g., 'BR01 STOPC' or 'FFASTC'): ").strip()
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
                send_command_to_br(target, action)
            else:
                print("Invalid target. Use 'BR01' or 'ALL'.")
        else:
            print("Invalid input format. Use 'BR01 START' or 'ALL STOP'.")
    except Exception as e:
        print(f"Error processing command: {e}")

# Broadcast a command to all CCPs
def broadcast_command(action):
    command = {"client_type": "mcp", "message": "EXEC", "action": action.upper(), "sequence_number": increment_sequence("mcp")}
    for ccp_id, address in ccp_ports.items():
        send_message(address, command)
    print(f"Broadcast command '{action}' sent to all CCPs.")

# Send a specific command to a single BR
def send_command_to_br(br_id, action):
    if br_id in ccp_ports:
        command = {"client_type": "mcp", "message": "EXEC", "action": action.upper(), "sequence_number": increment_sequence("mcp")}
        send_message(ccp_ports[br_id], command)
        print(f"Command '{action}' sent to {br_id}.")
    else:
        print(f"BR ID {br_id} not recognized.")

# Send STRQ (Status Request) to all CCPs, Stations, and Checkpoints every 2 seconds
# def send_status_requests(address, message):
#     while True:
#         # Send STRQ to all CCPs
#         for ccp_id in ccp_ports:
#             ccp_id = message['client_id']
#             status_request = {"client_type": "ccp", "message": "STRQ", "client_id": ccp_id, "sequence_number": s_mcp}
#             send_message(ccp_ports[ccp_id], status_request)
#             print(f"Sent STRQ to CCP {ccp_id}")

#             # Increment the missed heartbeat count if a STAT isn't received
#             if ccp_id in heartbeat_missed:
#                 heartbeat_missed[ccp_id] += 1
#             else:
#                 heartbeat_missed[ccp_id] = 1

#             # If 3 consecutive heartbeats are missed, trigger an emergency
#             if heartbeat_missed[ccp_id] > 3:
#                 print(f"Missed 3 heartbeats from CCP {ccp_id}.")
#                 # emergency_stop(ccp_id)
#                 # broadcast stop to all BRs
#                 exec_command = {"client_type": "mcp", "message": "EXEC", "client_id": "ccp_id", "sequence_number": "s_mcp", "action": "STOPC"} # BR stopped and doors closed
#                 broadcast_command(ccp_ports[ccp_id], exec_command) # Emergency stop - all BRs halt
#                 # disconnect specified BR
#                 exec_command = {"client_type": "mcp", "message": "EXEC", "client_id": "ccp_id", "sequence_number": "s_mcp", "action": "DISCONNECT"}
#                 send_command_to_br(ccp_ports[ccp_id], exec_command) # Disconnect
#                 # CCP should send an OFLN status message

#         # Send STRQ to all Stations
#         for station_id in station_ports:
#             station_id = message['client_id']
#             status_request = { "client_type": "stc", "message": "STRQ", "client_id": station_id, "sequence_number": s_mcp}
#             send_message(station_ports[station_id], status_request)
#             print(f"Sent STRQ to Station {station_id}")

#             # Increment the missed heartbeat count if a STAT isn't received
#             if station_id in heartbeat_missed:
#                 heartbeat_missed[station_id] += 1
#             else:
#                 heartbeat_missed[station_id] = 1

#             # If 3 consecutive heartbeats are missed, trigger an emergency
#             if heartbeat_missed[station_id] > 3:
#                 print(f"Missed 3 heartbeats from Station {station_id}.")
#                 # emergency_stop(station_id)


#         # Send STRQ to all Checkpoints
#         for checkpoint_id in checkpoint_ports:
#             status_request = {"client_type": "cpc", "message": "STRQ", "client_id": checkpoint_id, "sequence_number": s_mcp}
#             send_message(checkpoint_ports[checkpoint_id], status_request)
#             print(f"Sent STRQ to Checkpoint {checkpoint_id}")

#             # Increment the missed heartbeat count if a STAT isn't received
#             if checkpoint_id in heartbeat_missed:
#                 heartbeat_missed[checkpoint_id] += 1
#             else:
#                 heartbeat_missed[checkpoint_id] = 1

#             # If 3 consecutive heartbeats are missed, trigger an emergency
#             if heartbeat_missed[checkpoint_id] > 3:
#                 print(f"Missed 3 heartbeats from Checkpoint {checkpoint_id}. Taking emergency action.")
#                 # emergency_stop(checkpoint_id)

#         time.sleep(2)  # Wait for 2 seconds before sending the next STRQ    

# Handle incoming messages
def handle_message(address, message):
    if message['client_type'] == 'ccp':
        print(f"Handling CCP message from {address}")
        handle_ccp_message(address, message)
    elif message['client_type'] == 'station':
        print(f"Handling Station message from {address}")
        handle_station_message(address, message)
    elif message['client_type'] == 'checkpoint':
        print(f"Handling Checkpoint message from {address}")
        handle_checkpoint_message(address, message)

# Handle CCP messages
def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']
    # s_ccp = message['sequence_number']
    # s_mcp = s_ccp+1

    if message['message'] == 'CCIN':
        # Handle initialization: Send ACK first
        print(f"CCP {ccp_id} initialized.")
        ack_command = {"client_type": "mcp", "message": "AKIN", "client_id": ccp_id, "sequence_number": increment_sequence("mcp")}
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge initialisation
    # Status update
    elif message['message'] == 'STAT':
        print(f"BR {ccp_id} STAT received.")
        ack_command = {"client_type": "mcp", "message": "AKST", "client_id": ccp_id, "sequence_number": increment_sequence("mcp")}
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge status
        if message['status'] == 'ERR':
            exec_command = {"client_type": "mcp", "message": "EXEC", "client_id": ccp_id, "sequence_number": increment_sequence("mcp"), "action": "STOPC"}
            # exec_command = {"client_type": "mcp", "message": "EXEC", "client_id": "ccp_id", "sequence_number": "s_mcp", "action": "STOPC"}
            broadcast_command(ccp_ports[ccp_id], exec_command) # Emergency stop - all BRs halt
            exec_command = {"client_type": "mcp", "message": "EXEC", "client_id": "ccp_id", "sequence_number": increment_sequence("mcp"), "action": "DISCONNECT"}
            send_command_to_br(ccp_ports[ccp_id], exec_command) # Disconnect
            # CCP should send an OFLN status message

    # EXEC acknowledgement
    elif message['message'] == 'AKEX':
        print(f"BR {ccp_id} acknowledged command.")
    
    # No need for CCP to send block info as MCP will determine that from checkpoints.

# Handle Station messages
def handle_station_message(address, message):
    log_event("Station Message Received", message)
    station_id = message['client_id']

    if message['message'] == 'STIN':
        # Handle initialisation: Send ACK first
        print(f"Station {station_id} initialized.")
        ack_command = {"client_type": "mcp", "message": "AKIN", "client_id": station_id, "sequence_number": increment_sequence("mcp")}
        send_message(station_ports[station_id], ack_command)  # Acknowledge initialisation
    # print(f"Station message handled from {station_id}: {message}")
    # Status update
    elif message['message'] == 'STAT':
        print(f"Station {station_id} STAT received.")
        if message['status'] == 'ERR':
            error_command = {"client_type": "stc", "message": "EXEC", "client_id": "station_id", "sequence_number": increment_sequence("mcp"), "action": "BLINK", "br_id": ""}
            send_message(station_ports[station_id], error_command)  # BLINK
    # EXEC acknowledgement
    elif message['message'] == 'AKEX':
        print(f"BR {station_id} acknowledged command.")
    

# Handle Checkpoint messages (TRIP signal)
def handle_checkpoint_message(address, message):
    log_event("Checkpoint Message Received", message)
    checkpoint_id = message['client_id']
    
    if message['message'] == 'CPIN':
        # Handle initialization: Send ACK first
        print(f"Station {checkpoint_id} initialized.")
        ack_command = {"client_type": "mcp", "message": "AKIN", "status": "RECEIVED", "sequence_number": increment_sequence("mcp")}
        send_message(checkpoint_ports[checkpoint_id], ack_command)  # Acknowledge initialization
    # Assuming TRIP message contains which block was tripped
    elif message['message'] == 'TRIP':
        tripped_block = message['block_id']
        print(f"TRIP signal received from {checkpoint_id}, block {tripped_block}")
        ack_command = {"client_type": "cpc", "message": "AKTR", "sequence_number": increment_sequence("mcp")}
        send_message(checkpoint_ports[checkpoint_id], ack_command)  # Acknowledge TRIP

        # Turn on LED
        led_command = {"client_type": "cpc", "message": "EXEC", "client_id": "checkpoint_id", "sequence_number": increment_sequence("mcp"), "action": "ON"}
        send_message(checkpoint_ports[checkpoint_id], led_command)  # Turn ON the checkpoint LED

        # EXEC FSLOWC
        # Determine which BR is in this block
        if tripped_block in track_occupancy:
            br_id = track_occupancy[tripped_block]
            # Send SLOW command to BR before full stop
            handle_slow(br_id)
            stop_br_at_station(br_id, track_map[tripped_block]['station'])
    # Status update
    elif message['message'] == 'STAT':
        print(f"Checkpoint {checkpoint_id} STAT received.")
        if message['status'] == 'ERR':
            error_command = {"client_type": "cpc", "message": "EXEC", "client_id": "checkpoint_id", "sequence_number": increment_sequence("mcp"), "action": "BLINK"}
            send_message(checkpoint_ports[checkpoint_id], error_command)
    # EXEC acknowledgement
    elif message['message'] == 'AKEX':
        print(f"BR {checkpoint_id} acknowledged command.")

# Handle BR stops at stations
def stop_br_at_station(br_id, station_id):
    stop_command = {"client_type": "mcp", "message": "EXEC", "sequence_number": increment_sequence("mcp"), "action": "STOPO"} # BR stops and the door is opened
    send_message(ccp_ports[br_id], stop_command)
    print(f"BR {br_id} stopping at station {station_id}")
    control_station_doors(station_id, "OPEN")
    time.sleep(10)  # Wait time
    control_station_doors(station_id, "CLOSE")
    
    # Broadcast START again to all BRs after each station stop
    broadcast_start()

    for checkpoint_id in checkpoint_ports:
        off_command = {"client_type": "cpc", "message": "EXEC", "client_id": "checkpoint_id", "sequence_number": increment_sequence("mcp"), "action": "OFF"}
        send_message(checkpoint_ports[checkpoint_id], off_command)  # Turn OFF the checkpoint LED
        print(f"Sent OFF command to checkpoint {checkpoint_id}")

# Control station doors
def control_station_doors(station_id, action):
    door_command = {"client_type": "mcp", "message": "DOOR", "sequence_number": increment_sequence("mcp"), "action": action}
    send_message(station_ports[station_id], door_command)

# Handle SLOW command for BRs before stopping
def handle_slow(br_id):
    slow_command = {"client_type": "mcp", "message": "EXEC", "sequence_number": increment_sequence("mcp"), "action": "FSLOWC"} #BR moves forward slowly and the door is closed
    send_message(ccp_ports[br_id], slow_command)
    print(f"FSLOWC command sent to {br_id}.")

# Broadcast START command to all BRs to continue to the next station
def broadcast_start():
    start_command = {"client_type": "mcp", "message": "EXEC", "sequence_number": increment_sequence("mcp"), "action": "FFASTC"} # BR moves forward, fast, door is closed
    for ccp_id, address in ccp_ports.items():
        send_message(address, start_command)
    print(f"START command broadcasted to all CCPs.")

def reset_system():
    global track_occupancy, heartbeat_missed, sequence_tracker
    track_occupancy = {}
    heartbeat_missed = {}
    
    # Reset sequence tracker for MCP
    for key in sequence_tracker:
        sequence_tracker[key] = 0

    # Broadcast reset command to all CCPs, Stations, and Checkpoints
    broadcast_reset_command()

    print("System has been reset.")

def broadcast_reset_command():
    reset_command = {"client_type": "mcp", "message": "RESET"}
    # Send to all CCPs
    for ccp_id, address in ccp_ports.items():
        send_message(address, reset_command)
    # Send to all Stations
    for station_id, address in station_ports.items():
        send_message(address, reset_command)
    # Send to all Checkpoints
    for checkpoint_id, address in checkpoint_ports.items():
        send_message(address, reset_command)

    print("Broadcast reset command sent to all components.")

if __name__ == "__main__":
    start_mcp()
