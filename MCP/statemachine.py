#assumptions: everything has been initialised correctly
from utils import create_socket, receive_message, send_message, log_event
import time

class stateMachine:
 
 def __init__(self, ccp_ports, station_ports, track_map, track_occupancy ):
    #initialise class variables
  self.ccp_ports = ccp_ports
  self.station_ports = station_ports
  self.track_map = track_map
  self.track_occupancy = track_occupancy

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
            elif target.startswith("ST"):
                # send command to specific station
                send_command_to_station(target, action)
            else:
                print("Invalid target. Use 'BR01' or 'ALL'.")
        else:
            print("Invalid input format. Use 'BR01 START' or 'ALL STOP'.")
    except Exception as e:
        print(f"Error processing command: {e}")

# Broadcast a command to all CCPs
def broadcast_command(self, action):
    command = {"client_type": "mcp", "message": "EXEC", "action": action.upper()}
    for ccp_id, address in self.ccp_ports.items():
        send_message(address, command)
    print(f"Broadcast command '{action}' sent to all CCPs.")

# Send a specific command to a single BR
def send_command_to_br(self, br_id, action):
    if br_id in self.ccp_ports:
        command = {"client_type": "mcp", "message": "EXEC", "action": action.upper()}
        send_message(self.ccp_ports[br_id], command)
        print(f"Command '{action}' sent to {br_id}.")
    else:
        print(f"BR ID {br_id} not recognized.")
        
def send_command_to_station(self, target_id, action):
    if target_id in self.station_ports:
        command = {"client_type": "mcp", "message": "IRLD", "action": action.upper()}
        send_message(self.station_ports[target_id], command)
        print(f"Command '{action}' sent to {target_id}.")
    else:
        print(f"ST ID {target_id} not recognized.")

# Handle incoming message by client type
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


def handle_ccp_message(self, address, message):
    log_event("CCP Message Received", message)
    ccp_id = message['client_id']

    if message['message'] == 'CCIN':
        # Handle initialization: Send ACK first
        print(f"CCP {ccp_id} initialized.")
        ack_command = {"client_type": "mcp", "message": "ACK", "status": "RECEIVED"}
        send_message(self.ccp_ports[ccp_id], ack_command)  # Acknowledge initialization
    
   # STATUS message from CCP and likewise MCP response
    if message['message'] == 'STAT':
        print(f"CCP stat acknowledged but not implemented")
        ack_command = {"client_type": "mcp", "message": "AKST", "status": "RECEIVED"}
    

def handle_station_message(self, address, message):
    station_id = message['station']

    if message['message'] == 'STIN':
        print(f"STIN  acknowledged but not implemented")
        ack_command = {"client_type": "mcp", "message": "AKIN", "status": "RECEIVED"}

    if message['message'] == 'TRIP':
        #This is where the inter client communication occurs
        print(f"TRIP  acknowledged but not implemented")
        ack_command = {"client_type": "mcp", "message": "AKTR", "status": "RECEIVED"}
        handle_TRIP(message)

#right now, focus on trip command. As a very important command, TRIP
#provokes changes
        
def handle_TRIP(self, message):
    #talks to all necessary clients
    


# Broadcast START command to all BRs to continue to the next station
def broadcast_start(self):
    start_command = {"client_type": "mcp", "message": "EXEC", "action": "START"}
    for ccp_id, address in self.ccp_ports.items():
        send_message(address, start_command)
    print(f"START command broadcasted to all CCPs.")

### one function that defers to each scenario
  
