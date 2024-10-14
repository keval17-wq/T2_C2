import socket
import threading
from utils import create_socket, receive_message, send_message, log_event
import time
from statemachine import stateMachine

# Static port mapping for CCPs (Blade Runners)
ccp_ports = {
    'BR01': ('127.0.0.1', 2002),
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

# Track map for block management, handling turns and checkpoints
track_map = {
    'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False, 'led': 'LED01'},
    'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False,'led': 'LED02', 'is_checkpoint': True},
    'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True,'led': 'LED03', 'turn_severity': 0.5},
    'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False, 'led': 'LED04','is_checkpoint': True},
    'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False, 'led': 'LED05'},
    'block_6': {'station': 'ST06', 'next_block': 'block_7', 'turn': True, 'led': 'LED06', 'turn_severity': 0.7, 'is_checkpoint': True},
    'block_7': {'station': 'ST07', 'next_block': 'block_8', 'turn': False, 'led': 'LED07'},
    'block_8': {'station': 'ST08', 'next_block': 'block_9', 'turn': False, 'led': 'LED08', 'is_checkpoint': True},
    'block_9': {'station': 'ST09', 'next_block': 'block_10', 'turn': False, 'led': 'LED09'},
    'block_10': {'station': 'ST10', 'next_block': 'block_1', 'turn': False, 'led': 'LED10'}
}

# Track occupancy to map which block is occupied by which BR
track_occupancy = {}

# Start MCP server and emergency handler thread
def start_mcp():
    state_machine = stateMachine(ccp_ports, station_ports, track_map, track_occupancy)
    print("Starting MCP...")
    mcp_socket = create_socket(2001)  # MCP listens on port 2001
    print("MCP listening on port 2001")

    # Start the emergency command thread
    emergency = threading.Thread(target= state_machine.emergency_command_handler)
    emergency.daemon = True  # Ensure this thread stops when the main program exits
    emergency.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_message(mcp_socket)
        print(f"Message received from {address}")
        state_machine.handle_message(address, message) #message handoff here


if __name__ == "__main__":
    start_mcp()
