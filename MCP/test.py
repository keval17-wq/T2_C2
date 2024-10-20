import socket
import threading
import time
from utils import create_socket, receive_message, send_message, log_event

# Localhost IP for testing
LOCAL_HOST = '127.0.0.1'

# Static port mapping for Blade Runners (CCPs) on localhost
ccp_ports = {
    'BR01': (LOCAL_HOST, 2002),
    'BR02': (LOCAL_HOST, 2003),
    'BR03': (LOCAL_HOST, 2004),
    'BR04': (LOCAL_HOST, 2005),
    'BR05': (LOCAL_HOST, 2006)
}

# Static port mapping for Stations (STCs) on localhost
station_ports = {
    'ST01': (LOCAL_HOST, 4001),
    'ST02': (LOCAL_HOST, 4002),
    'ST03': (LOCAL_HOST, 4003),
    'ST04': (LOCAL_HOST, 4004),
    'ST05': (LOCAL_HOST, 4005),
    'ST06': (LOCAL_HOST, 4006),
    'ST07': (LOCAL_HOST, 4007),
    'ST08': (LOCAL_HOST, 4008),
    'ST09': (LOCAL_HOST, 4009),
    'ST10': (LOCAL_HOST, 4010)
}

# Static port mapping for Checkpoints (CPCs) on localhost
checkpoint_ports = {
    'CP01': (LOCAL_HOST, 5001),
    'CP02': (LOCAL_HOST, 5002),
    'CP03': (LOCAL_HOST, 5003),
    'CP04': (LOCAL_HOST, 5004),
    'CP05': (LOCAL_HOST, 5005),
    'CP06': (LOCAL_HOST, 5006),
    'CP07': (LOCAL_HOST, 5007),
    'CP08': (LOCAL_HOST, 5008),
    'CP09': (LOCAL_HOST, 5009),
    'CP10': (LOCAL_HOST, 5010)
}

# Ports the MCP is listening to
mcp_port = 2000

# Track sequence numbers per client
sequence_numbers = {
    'BR01': 1000,
    'BR02': 1000,
    'BR03': 1000,
    'BR04': 1000,
    'BR05': 1000,
    'ST01': 2000,
    'ST02': 2000,
    'ST03': 2000,
    'ST04': 2000,
    'ST05': 2000,
    'CP01': 3000,
    'CP02': 3000,
    'CP03': 3000,
    'CP04': 3000,
    'CP05': 3000
}

# Update the sequence number for each client
def update_sequence_number(client_id):
    if client_id in sequence_numbers:
        sequence_numbers[client_id] += 1
        return sequence_numbers[client_id]
    return None

# Create socket and listen on a specific port
def start_component(port, expected_message, component_type):
    component_socket = create_socket(port)

    def listen_for_mcp():
        while True:
            try:
                message, address = receive_message(component_socket)
                client_id = message['client_id']
                print(f"{component_type} on port {port} received message: {message}")
                
                # Verify sequence number is correct
                expected_sequence = sequence_numbers[client_id]
                if message['sequence_number'] == expected_sequence:
                    log_event(f"Correct sequence number for {client_id}", message)
                else:
                    log_event(f"Sequence number mismatch for {client_id}: expected {expected_sequence}, got {message['sequence_number']}", message)

                # Send the expected acknowledgment back to MCP with updated sequence number
                updated_sequence = update_sequence_number(client_id)
                expected_message['sequence_number'] = updated_sequence
                send_message(address, expected_message)
                print(f"Acknowledgment sent from port {port}: {expected_message}")
            except Exception as e:
                print(f"Error on port {port}: {e}")

    thread = threading.Thread(target=listen_for_mcp)
    thread.daemon = True
    thread.start()
    return thread

# Send test command to MCP
def send_test_command(port, command):
    mcp_socket = create_socket()
    client_id = command['client_id']
    
    # Set the correct sequence number before sending the command
    command['sequence_number'] = update_sequence_number(client_id)
    send_message((LOCAL_HOST, mcp_port), command)
    print(f"Sent test command to MCP: {command}")
    mcp_socket.close()

# Test case function to validate communication for each type
def run_test_case(component_type, ports, ack_message):
    for client_id, (host, port) in ports.items():
        ack = ack_message.copy()
        ack['client_id'] = client_id
        start_component(port, ack, component_type)

# Start listening for CCP, STC, and CPC on their respective ports
def start_test():
    # Run tests for CCP (Blade Runners)
    run_test_case("CCP", ccp_ports, {"client_type": "CCP", "message": "AKEX", "sequence_number": 0})

    # Run tests for STC (Stations)
    run_test_case("STC", station_ports, {"client_type": "STC", "message": "AKEX", "sequence_number": 0})

    # Run tests for CPC (Checkpoints)
    run_test_case("CPC", checkpoint_ports, {"client_type": "CPC", "message": "AKEX", "sequence_number": 0})

    # Simulate sending test commands to MCP from different clients
    test_commands = [
        {"client_type": "CCP", "message": "CCIN", "client_id": "BR01"},
        {"client_type": "STC", "message": "DOOR", "client_id": "ST01", "action": "OPEN"},
        {"client_type": "CPC", "message": "TRIP", "client_id": "CP01", "status": "ON"}
    ]

    # Send commands to MCP to simulate test cases
    for command in test_commands:
        if command["client_type"] == "CCP":
            send_test_command(ccp_ports[command["client_id"]][1], command)
        elif command["client_type"] == "STC":
            send_test_command(station_ports[command["client_id"]][1], command)
        elif command["client_type"] == "CPC":
            send_test_command(checkpoint_ports[command["client_id"]][1], command)

    time.sleep(5)  # Allow time for processing
    print("Test run completed")

if __name__ == "__main__":
    start_test()
