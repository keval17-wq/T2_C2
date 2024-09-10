import socket
import threading
from utils import create_udp_socket, receive_udp_message, send_udp_message, log_event
import time

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('192.168.1.101', 2002),
    'BR02': ('192.168.1.102', 2003),
    'BR03': ('192.168.1.103', 2004),
    'BR04': ('192.168.1.104', 2005),
    'BR05': ('192.168.1.105', 2006)
}

# Static port mapping for 10 stations
station_ports = {
    'ST01': ('192.168.1.201', 4001),
    'ST02': ('192.168.1.202', 4002),
    'ST03': ('192.168.1.203', 4003),
    'ST04': ('192.168.1.204', 4004),
    'ST05': ('192.168.1.205', 4005),
    'ST06': ('192.168.1.206', 4006),
    'ST07': ('192.168.1.207', 4007),
    'ST08': ('192.168.1.208', 4008),
    'ST09': ('192.168.1.209', 4009),
    'ST10': ('192.168.1.210', 4010)
}

# Track map for block management, handling turns and checkpoints
track_map = {
    'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False},
    'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False, 'is_checkpoint': True},
    'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True, 'turn_severity': 0.5},
    'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False, 'is_checkpoint': True},
    'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False},
    'block_6': {'station': 'ST06', 'next_block': 'block_7', 'turn': True, 'turn_severity': 0.7, 'is_checkpoint': True},
    'block_7': {'station': 'ST07', 'next_block': 'block_8', 'turn': False},
    'block_8': {'station': 'ST08', 'next_block': 'block_9', 'turn': False, 'is_checkpoint': True},
    'block_9': {'station': 'ST09', 'next_block': 'block_10', 'turn': False},
    'block_10': {'station': 'ST10', 'next_block': 'block_1', 'turn': False}
}

# Start MCP server and emergency handler thread
def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_udp_socket(2001)  # MCP listens on port 2001
    print("MCP listening on port 2001")
    
    # Start the emergency command thread
    emergency_thread = threading.Thread(target=emergency_command_handler)
    emergency_thread.daemon = True  # Ensure this thread stops when the main program exits
    emergency_thread.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_udp_message(mcp_socket)
        print(f"Message received from {address}")
        handle_message(address, message)

# Handle emergency commands (running in parallel)
def emergency_command_handler():
    while True:
        # Simulate emergency command handling
        emergency_input = input("Enter emergency command (e.g., 'stop' for STOP_ALL): ")
        if emergency_input == "stop":
            broadcast_emergency_command("STOP_ALL")
        time.sleep(1)

# Broadcast an emergency command to all CCPs
def broadcast_emergency_command(action):
    emergency_command = {"client_type": "mcp", "message": "EXEC", "action": action}
    for ccp_id, address in ccp_ports.items():
        send_udp_message(address, emergency_command)
    print(f"Emergency command '{action}' sent to all CCPs.")

# Handle incoming messages
def handle_message(address, message):
    if message['client_type'] == 'ccp':
        print(f"Handling CCP message from {address}")
        handle_ccp_message(address, message)
    elif message['client_type'] == 'station':
        print(f"Handling Station message from {address}")
        handle_station_message(address, message)

# Handle CCP messages
def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']

    if message['message'] == 'CCIN':
        # Handle initialization
        print(f"CCP {ccp_id} initialized.")
        # Send START command immediately after initialization
        start_command = {"client_type": "mcp", "message": "EXEC", "action": "START"}
        send_udp_message(ccp_ports[ccp_id], start_command)
        print(f"START command sent to CCP {ccp_id}.")
    
    current_block = message.get('current_block')  # Optional: Handle other messages related to blocks
    if current_block:
        # Check if the BR is approaching a station
        if 'station' in track_map[current_block]:
            station_id = track_map[current_block]['station']
            stop_br_at_station(ccp_id, station_id)
        # Handle turns
        if track_map[current_block].get('turn'):
            handle_turn(ccp_id, track_map[current_block]['turn_severity'])

# Handle Station messages
def handle_station_message(address, message):
    log_event("Station Message Received", message)
    station_id = message['client_id']
    print(f"Station message handled from {station_id}: {message}")

# Handle Blade Runner stops
def stop_br_at_station(ccp_id, station_id):
    stop_command = {"client_type": "mcp", "message": "EXEC", "action": "STOP"}
    send_udp_message(ccp_ports[ccp_id], stop_command)

    if track_map.get(station_id, {}).get('is_checkpoint'):
        print(f"BR {ccp_id} stopping briefly at checkpoint {station_id}")
        time.sleep(3)  # Brief stop at checkpoint (3 seconds)
    else:
        print(f"BR {ccp_id} stopping at station {station_id}")
        control_station_doors(station_id, "OPEN")
        time.sleep(10)  # Wait at station
        control_station_doors(station_id, "CLOSE")

    next_block = track_map[station_id]['next_block']
    move_to_next_station(ccp_id, next_block)

# Control station doors
def control_station_doors(station_id, action):
    door_command = {"client_type": "mcp", "message": "DOOR", "action": action}
    send_udp_message(station_ports[station_id], door_command)

# Move Blade Runner to next block
def move_to_next_station(ccp_id, next_block):
    move_command = {"client_type": "mcp", "message": "EXEC", "action": "MOVE_TO_NEXT_BLOCK"}
    send_udp_message(ccp_ports[ccp_id], move_command)

# Handle turns for Blade Runners
def handle_turn(ccp_id, severity):
    adjust_speed_command = {"client_type": "mcp", "message": "EXEC", "action": "SLOW", "turn_severity": severity}
    send_udp_message(ccp_ports[ccp_id], adjust_speed_command)

if __name__ == "__main__":
    start_mcp()
