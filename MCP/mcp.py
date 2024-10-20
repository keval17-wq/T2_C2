import socket
import threading
from utils import create_socket, receive_message, send_message, log_event
import time

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('10.126.195.126', 2002),
    'BR02': ('127.0.0.1', 2003),
    'BR03': ('127.0.0.1', 2004),
    'BR04': ('127.0.0.1', 2005),
    'BR05': ('127.0.0.1', 2006)
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

# Static port mapping for checkpoints
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
# Send the information to Station on notifying when START upon stopping after the trip thing. 
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
        print(f"Message received from {address}")
        handle_message(address, message)

# Handle emergency commands (running in parallel)
def emergency_command_handler():
    while True:
        # Simulate emergency command handling, with target BR selection
        emergency_input = input("Enter command (e.g., 'BR01 STOP' or 'ALL START'): ").strip()
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
    command = {"client_type": "mcp", "message": "EXEC", "action": action.upper()}
    for ccp_id, address in ccp_ports.items():
        send_message(address, command)
    print(f"Broadcast command '{action}' sent to all CCPs.")

# Send a specific command to a single BR
def send_command_to_br(br_id, action):
    if br_id in ccp_ports:
        command = {"client_type": "mcp", "message": "EXEC", "action": action.upper()}
        send_message(ccp_ports[br_id], command)
        print(f"Command '{action}' sent to {br_id}.")
    else:
        print(f"BR ID {br_id} not recognized.")

# Handle incoming messages
def handle_message(address, message):
    if message['client_type'] == 'ccp':
        handle_ccp_message(address, message)
    elif message['client_type'] == 'station':
        handle_station_message(address, message)
    elif message['client_type'] == 'checkpoint':
        handle_checkpoint_message(address, message)

# Handle CCP messages
def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']

    if message['message'] == 'CCIN':
        # Handle initialization: Send ACK first
        print(f"CCP {ccp_id} initialized.")
        ack_command = {"client_type": "mcp", "message": "AKIN", "status": "RECEIVED"}
        send_message(ccp_ports[ccp_id], ack_command)  # Acknowledge initialization
    
    # Handle other status or commands if needed

# Handle Station messages
def handle_station_message(address, message):
    log_event("Station Message Received", message)
    station_id = message['client_id']
    print(f"Station message handled from {station_id}: {message}")

# Handle Checkpoint messages (TRIP signal)
def handle_checkpoint_message(address, message):
    log_event("Checkpoint Message Received", message)
    checkpoint_id = message['client_id']
    
    # Assuming TRIP message contains which block was tripped
    if message['message'] == 'TRIP':
        tripped_block = message['block_id']
        print(f"TRIP signal received from {checkpoint_id}, block {tripped_block}")
        
        # Determine which BR is in this block
        if tripped_block in track_occupancy:
            br_id = track_occupancy[tripped_block]
            handle_slow(br_id)
            notify_station_and_checkpoint(br_id, track_map[tripped_block]['station'])
            stop_br_at_station(br_id, track_map[tripped_block]['station'])

# Handle BR stops at stations and notify checkpoint/station of arrival
def stop_br_at_station(br_id, station_id):
    stop_command = {"client_type": "mcp", "message": "EXEC", "action": "STOP"}
    send_message(ccp_ports[br_id], stop_command)

    # Handle stopping at checkpoint or station
    if track_map.get(station_id, {}).get('is_checkpoint'):
        print(f"BR {br_id} stopping briefly at checkpoint {station_id}")
        time.sleep(3)  # Brief stop
    else:
        print(f"BR {br_id} stopping at station {station_id}")
        control_station_doors(station_id, "OPEN")
        time.sleep(10)  # Wait time
        control_station_doors(station_id, "CLOSE")
    
    broadcast_start()

# Notify both checkpoint and station about BR's arrival
def notify_station_and_checkpoint(br_id, station_id):
    checkpoint_id = track_map[station_id].get('checkpoint_id')

    if checkpoint_id:
        notify_checkpoint_arrival(br_id, checkpoint_id)

    notify_station_arrival(br_id, station_id)

# Notify the checkpoint that BR is arriving
def notify_checkpoint_arrival(br_id, checkpoint_id):
    arrival_message = {"client_type": "mcp", "message": "BRARRIVE", "client_id": checkpoint_id, "br_id": br_id}
    send_message(checkpoint_ports[checkpoint_id], arrival_message)
    # Turn on LED at checkpoint
    led_command = {"client_type": "mcp", "message": "EXEC", "client_id": checkpoint_id, "action": "ON"}
    send_message(checkpoint_ports[checkpoint_id], led_command)
    print(f"Notified checkpoint {checkpoint_id} about BR {br_id} arrival.")

# Notify the station that BR is arriving
def notify_station_arrival(br_id, station_id):
    arrival_message = {"client_type": "mcp", "message": "STNARRIVE", "client_id": station_id, "br_id": br_id}
    send_message(station_ports[station_id], arrival_message)
    print(f"Notified station {station_id} about BR {br_id} arrival.")

# Control station doors
def control_station_doors(station_id, action):
    door_command = {"client_type": "mcp", "message": "DOOR", "action": action}
    send_message(station_ports[station_id], door_command)

# Handle SLOW command for BRs before stopping
def handle_slow(br_id):
    slow_command = {"client_type": "mcp", "message": "EXEC", "action": "SLOW"}
    send_message(ccp_ports[br_id], slow_command)
    print(f"SLOW command sent to {br_id}.")

# Broadcast START command to all BRs to continue to the next station
def broadcast_start():
    start_command = {"client_type": "mcp", "message": "EXEC", "action": "START"}
    for ccp_id, address in ccp_ports.items():
        send_message(address, start_command)
    print(f"START command broadcasted to all CCPs.")

if __name__ == "__main__":
    start_mcp()
