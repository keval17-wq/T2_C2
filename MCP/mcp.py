import socket
from utils import create_udp_socket, receive_udp_message, send_udp_message, log_event

def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_udp_socket(2001)  # MCP listens on port 2001
    print("MCP listening on port 2001")
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
    # Example: Send a command back to CCP on port 2002
    response = {"client_type": "mcp", "message": "COMMAND", "action": "EXECUTE"}
    send_udp_message((address[0], 2002), response)  # Send command to CCP on port 2002
    

def handle_station_message(address, message):
    log_event("Station Message Received", message)
    print(f"Station message handled: {message}")
    # Send response to the station if needed, e.g., on port 2003

def handle_led_controller_message(address, message):
    log_event("LED Controller Message Received", message)
    print(f"LED Controller message handled: {message}")
    # Send response to the LED controller if needed, e.g., on port 2004

if __name__ == "__main__":
    start_mcp()
