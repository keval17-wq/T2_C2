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
    #mcp_socket = create_socket(port)
    client_id = command['client_id']
    
    # Set the correct sequence number before sending the command
    command['sequence_number'] = update_sequence_number(client_id)
    send_message((LOCAL_HOST, mcp_port), command)
    print(f"Sent test command to MCP: {command}")
   # mcp_socket.close()

# Test case function to validate communication for each type
def run_test_case(component_type, ports, ack_message):
    for client_id, (host, port) in ports.items():
        ack = ack_message.copy()
        ack['client_id'] = client_id
        start_component(port, ack, component_type)

# Start listening for CCP, STC, and CPC on their respective ports
def start__acknowledgement_test():
    # Run tests for CCP (Blade Runners)
    run_test_case("CCP", ccp_ports, {"client_type": "CCP", "message": "AKEX", "sequence_number": 0})

    # Run tests for STC (Stations)
    run_test_case("STC", station_ports, {"client_type": "STC", "message": "AKEX", "sequence_number": 0})

    # Run tests for CPC (Checkpoints)
    run_test_case("CPC", checkpoint_ports, {"client_type": "CPC", "message": "AKEX", "sequence_number": 0})

    # Simulate sending test commands to MCP from different clients
   
    test_acknowledge_commands = [ #list of commands to test that they are recognised and  an acknowledgment is sent back from MCP, simply
    # CCP messages
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1000"}, # Init message with CCP clients
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1000"},
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR03", "sequence_number": "1000"},
    
    # STAT messages from BR01
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "ERR", "sequence_number": "1001"}, # error status value from CCP
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "STOPC", "sequence_number": "1002"}, # BR stopped unexpectedly
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "STOPO", "sequence_number": "1003"}, # BR stopped unexpectedly with door open
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "FSLOWC", "sequence_number": "1004"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "FFASTC", "sequence_number": "1005"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "RSLOWC", "sequence_number": "1006"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "status": "OFLN", "sequence_number": "1007"},
    
    {"client_type": "STC", "message": "STIN", "client_id": "ST01", "sequence_number": "2000"}, # Initialization with ST01
    
    # TRIP Messages from STC01
    {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2001", "status": "ON"},
    {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2002", "status": "OFF"},
    {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2003", "status": "ERR"},
    
    # Checkpoint initialization
    {"client_type": "CPC", "message": "CPIN", "client_id": "CP01", "sequence_number": "3000"},
    
    # Checkpoint status messages
    {"client_type": "CPC", "message": "TRIP", "client_id": "CP01", "sequence_number": "3001", "status": "ON"},
    {"client_type": "CPC", "message": "TRIP", "client_id": "CP01", "sequence_number": "3002", "status": "OFF"},
    {"client_type": "CPC", "message": "TRIP", "client_id": "CP01", "sequence_number": "3003", "status": "ERR"},
] 
    test_station_stopping_commands = [ #these are the commands in the station stopping protocol from the clients, in order
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1000"},
    {"client_type": "STC", "message": "STIN", "client_id": "ST01", "sequence_number": "2000"},
    
    {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2001", "status": "ON"},
    {"client_type": "CCP", "message": "AKEX", "client_id": "BR01", "sequence_number": "1001"},
    {"client_type": "STC", "message": "AKEX", "client_id": "ST01", "sequence_number": "2002"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "sequence_number": "1002", "status": "STOPC"},
    {"client_type": "CCP", "message": "AKEX", "client_id": "BR01", "sequence_number": "1003"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "sequence_number": "1004", "status": "STOPO"},
    {"client_type": "STC", "message": "STAT", "client_id": "ST01", "sequence_number": "2003", "status": "ONOPEN"},
    {"client_type": "CCP", "message": "AKEX", "client_id": "BR01", "sequence_number": "1005"},
    {"client_type": "STC", "message": "STAT", "client_id": "ST01", "sequence_number": "2004", "status": "ON"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "sequence_number": "1006", "status": "STOPC"},
    {"client_type": "STC", "message": "AKEX", "client_id": "ST01", "sequence_number": "2005"},
    {"client_type": "CCP", "message": "AKEX", "client_id": "BR01", "sequence_number": "1007"},
    {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "sequence_number": "1008", "status": "FFASTC"},
    {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2006", "status": "OFF"},
]
    
    test_startup_commands = [
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1000"},
    {"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1000"},
    {"client_type": "STC", "message": "STIN", "client_id": "ST01", "sequence_number": "2000"},
     {"client_type": "CPC", "message": "CPIN", "client_id": "CP01", "sequence_number": "3000"},
     
     {"client_type": "CCP", "message": "AKEX", "client_id": "BR01", "sequence_number": "1001"},
     {"client_type": "STC", "message": "TRIP", "client_id": "ST01", "sequence_number": "2001"},
     {"client_type": "CCP", "message": "STAT", "client_id": "BR01", "sequence_number": "1002", "status": "STOPC"},
     {"client_type": "CCP", "message": "AKEX", "client_id": "BR02", "sequence_number": "1001"},
     {"client_type": "CPC", "message": "TRIP", "client_id": "CP01", "sequence_number": "3001", "status": "ON"},
     {"client_type": "CCP", "message": "STAT", "client_id": "BR02", "sequence_number": "1002", "status": "STOPC"},
   
    ]

   

    # Send commands to MCP to simulate test cases
    for command in test_acknowledge_commands: # use the other data structure ' test_station_stopping_commands' to test station stop protocol
        if command["client_type"] == "CCP":
            send_test_command(ccp_ports[command["client_id"]][1], command)
        elif command["client_type"] == "STC":
            send_test_command(station_ports[command["client_id"]][1], command)
        elif command["client_type"] == "CPC":
            send_test_command(checkpoint_ports[command["client_id"]][1], command)
        time.sleep(1)  # Allow time for processing

    
    print("Test run completed")

if __name__ == "__main__":
    start__acknowledgement_test()
