import socket
from utils import create_socket, receive_message, send_message, log_event
import time

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('192.168.1.101', 2002),
    'BR02': ('192.168.1.102', 2003),
    'BR03': ('192.168.1.103', 2004),
    'BR04': ('192.168.1.104', 2005),
    'BR05': ('192.168.1.105', 2006)
}

# Static port mapping for 10 stations, all acting as checkpoints
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

def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_socket(2001)  # MCP listens on port 2001
    print("MCP listening on port 2001")
    
    while True:
        print("Waiting for messages...")
        message, address = receive_message(mcp_socket)
        print(f"Message received from {address}")
        handle_message(address, message)

def handle_message(address, message):
    if message['client_type'] == 'ccp':
        print(f"Handling CCP message from {address}")
        handle_ccp_message(address, message)
    elif message['client_type'] == 'station':
        print(f"Handling Station message from {address}")
        handle_station_message(address, message)

def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']

    # Handle initial connection 'CCIN'
    if message['message'] == 'CCIN':
        print(f"CCP {ccp_id} has connected.")
        ack_message = {"client_type": "mcp", "message": "ACK", "status": "INITIALIZED"}
        send_message(address, ack_message)
        return

    # Handle status updates with 'current_block'
    if 'current_block' in message:
        current_block = message['current_block']
        
        # Check if the BR is approaching a station
        if 'station' in track_map[current_block]:
            station_id = track_map[current_block]['station']
            stop_at_station(ccp_id, station_id)
        
        # Check if there's a turn and handle speed accordingly
        if track_map[current_block].get('turn'):
            handle_turn(ccp_id, track_map[current_block]['turn_severity'])
    else:
        print(f"Message from CCP {ccp_id} does not include 'current_block'.")

def stop_at_station(ccp_id, station_id):
    # Send stop command to CCP (Blade Runner)
    stop_command = {"client_type": "mcp", "message": "EXEC", "action": "STOP"}
    send_message(ccp_ports[ccp_id], stop_command)
    
    print(f"BR {ccp_id} stopping at station {station_id}")
    
    # Open station doors
    control_station_doors(station_id, "OPEN")
    
    # Wait for a fixed time (simulating station stop)
    time.sleep(10)  # Stop time at station
    
    # Close station doors
    control_station_doors(station_id, "CLOSE")
    
    # Move to the next station
    next_block = track_map[current_block]['next_block']
    move_to_next_station(ccp_id, next_block)

def control_station_doors(station_id, action):
    # Send door control command to station
    door_command = {"client_type": "mcp", "message": "DOOR", "action": action}
    send_message(station_ports[station_id], door_command)

def move_to_next_station(ccp_id, next_block):
    # Command to move the BR to the next block
    move_command = {"client_type": "mcp", "message": "EXEC", "action": "MOVE_TO_NEXT_BLOCK"}
    send_message(ccp_ports[ccp_id], move_command)

def handle_turn(ccp_id, severity):
    # Handle a turn by adjusting speed
    adjust_speed_command = {"client_type": "mcp", "message": "EXEC", "action": "SLOW", "turn_severity": severity}
    send_message(ccp_ports[ccp_id], adjust_speed_command)

def handle_station_message(address, message):
    log_event("Station Message Received", message)
    station_id = message['client_id']
    print(f"Station message handled from {station_id}: {message}")
    # Handle station status, e.g., door opened/closed

if __name__ == "__main__":
    start_mcp()
