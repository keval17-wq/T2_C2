import socket
import json
from datetime import datetime
from utils import create_udp_socket, receive_udp_message, send_udp_message, log_event

# Dictionary to store IDs and their corresponding ports
device_port_mapping = {}

def start_mcp():
    print("Starting MCP...")
    mcp_socket = create_udp_socket(2001)  # MCP listens on port 2001
    print("MCP listening on port 2001")
    
    try:
        while True:
            print("Waiting for messages...")
            message, address = receive_udp_message(mcp_socket)
            print(f"Message received from {address}")
            
            # Parse and handle the received message
            handle_message(address, message)
    except KeyboardInterrupt:
        print("MCP shutting down.")
    finally:
        # Close the socket
        mcp_socket.close()

def handle_message(address, message):
    try:
        # Parse the incoming data as JSON
        message = json.loads(message)
        
        # Extract device ID and client type from the JSON message
        client_type = message['client_type']
        client_id = message['client_id']
        timestamp = datetime.utcfromtimestamp(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Print received message details
        print(f"Received message from {client_type} ({client_id}) at {address[0]}:{address[1]}")
        print(f"Timestamp: {timestamp}")
        print(f"Message content: {message}")
        
        # Update the device-port mapping dictionary
        device_port_mapping[client_id] = address[1]

        # Print updated dictionary
        print(f"Updated device-port mapping: {device_port_mapping}")
        
        # Handle the message based on client type
        if client_type == 'ccp':
            print(f"Handling CCP message from {address}")
            handle_ccp_message(address, message)
        elif client_type == 'station':
            print(f"Handling Station message from {address}")
            handle_station_message(address, message)
        elif client_type == 'led_controller':
            print(f"Handling LED Controller message from {address}")
            handle_led_controller_message(address, message)
        else:
            print(f"Unknown client type: {client_type}")
    except json.JSONDecodeError as e:
        print(f"Received non-JSON message from {address[0]}:{address[1]}")
        print(f"Data: {message}")
        print(f"Error: {e}")
    except KeyError as e:
        print(f"Missing expected key in message: {e}")

def handle_ccp_message(address, message):
    log_event("CCP Message Received", message)
    print(f"CCP message handled: {message}")
    # Example: Send a command back to CCP on port 2002
    response = {
        "client_type": "mcp", 
        "message": "COMMAND", 
        "action": "EXECUTE",
        "client_id": "MCP01",  # Added client_id to response
        "timestamp": int(datetime.utcnow().timestamp())  # Added current timestamp to response
    }
    send_udp_message((address[0], 2002), response)  # Send command to CCP on port 2002

def handle_station_message(address, message):
    log_event("Station Message Received", message)
    print(f"Station message handled: {message}")
    # Example: Send a response to the station if needed, e.g., on port 2003
    response = {
        "client_type": "mcp",
        "message": "ACK",
        "client_id": "MCP01",  # Added client_id to response
        "timestamp": int(datetime.utcnow().timestamp())  # Added current timestamp to response
    }
    send_udp_message((address[0], 2003), response)  # Send response to the Station on port 2003

def handle_led_controller_message(address, message):
    log_event("LED Controller Message Received", message)
    print(f"LED Controller message handled: {message}")
    # Example: Send response to the LED controller if needed, e.g., on port 2004
    response = {
        "client_type": "mcp",
        "message": "ACK",
        "client_id": "MCP01",  # Added client_id to response
        "timestamp": int(datetime.utcnow().timestamp())  # Added current timestamp to response
    }
    send_udp_message((address[0], 2004), response)  # Send response to the LED Controller on port 2004

if __name__ == "__main__":
    start_mcp()
