import socket
import threading
from utils import create_udp_socket, receive_udp_message, send_udp_message, log_event

# Default port numbers for each CCP
ccp_ports = {
    'BR1': 3001,
    'BR2': 3002,
    'BR3': 3003,
    'BR4': 3004,
    'BR5': 3005
}

def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_udp_socket(2001)
    print("MCP listening on port 2001")
    
    # Start a separate thread for handling user commands
    command_thread = threading.Thread(target=handle_user_commands)
    command_thread.daemon = True  # Make it a daemon thread so it exits when the main program ends
    command_thread.start()

    while True:
        print("Waiting for messages...")
        message, address = receive_udp_message(mcp_socket)
        print(f"Message received from {address}")
        handle_message(address, message)

def handle_message(address, message):
    if message['client_type'] == 'ccp':
        print(f"Handling CCP message from {address}")
        handle_ccp_message(address, message)
    elif message['client_type'] == 'station':
        print(f"Handling Station message from {address}")
        handle_station_message(address, message)
    elif message['client_type'] == 'led_controller':
        print(f"Handling LED Controller message from {address}")
        handle_led_controller_message(address, message)

def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    print(f"CCP message handled: {message}")

    if message['message'] == "CCIN":
        print(f"CCP {message['client_id']} initialized at {address}.")
        # Update the CCP ports mapping if needed

def send_mcp_command(action, ccp_id):
    if ccp_id in ccp_ports:
        port = ccp_ports[ccp_id]
        address = ('127.0.0.1', port)  # Replace '127.0.0.1' with the actual IP address if needed
        command = {"client_type": "mcp", "message": "COMMAND", "action": action.upper()}
        send_udp_message(address, command)
        print(f"{action.capitalize()} command sent to CCP {ccp_id} at {address}")
    else:
        print(f"Error: CCP with ID {ccp_id} has not been initialized. Please ensure the CCP has initialized before sending commands.")

def handle_station_message(address, message):
    log_event("Station Message Received", message)
    print(f"Station message handled: {message}")

def handle_led_controller_message(address, message):
    log_event("LED Controller Message Received", message)
    print(f"LED Controller message handled: {message}")

def handle_user_commands():
    while True:
        ccp_id = input("Enter CCP ID to send command (e.g., BR1): ").strip()
        action = input(f"Send command to CCP {ccp_id} (start/stop/move): ").strip().lower()
        if action in ["start", "stop", "move"]:
            send_mcp_command(action, ccp_id)
        else:
            print("Invalid command. Please enter 'start', 'stop', or 'move'.")

if __name__ == "__main__":
    start_mcp()
