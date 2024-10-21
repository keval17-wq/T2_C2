import socket
import time
from utils import create_socket, send_message, log_event

# Define the Checkpoints and their ports
checkpoint_ports = {
    'CP01': ('127.0.0.1', 5001),
    'CP04': ('127.0.0.1', 5004),
    'CP07': ('127.0.0.1', 5007),
    'CP10': ('127.0.0.1', 5010)
}

mcp_address = ('127.0.0.1', 2000)  # MCP address and port

# Sequence numbers to track for each checkpoint
sequence_numbers = {
    'CP01': 1000,
    'CP04': 1000,
    'CP07': 1000,
    'CP10': 1000
}

# Function to update the sequence number for each checkpoint
def update_sequence_number(cp_id):
    sequence_numbers[cp_id] += 1
    return sequence_numbers[cp_id]

# Function to send a TRIP message from a specific checkpoint
def send_trip_message(checkpoint_id):
    # Create the TRIP message
    trip_message = {
        "client_type": "CPC",  # Checkpoint client type
        "message": "TRIP",
        "client_id": checkpoint_id,
        "sequence_number": update_sequence_number(checkpoint_id),
        "status": "ON"  # Simulating that the IR beam is broken (BR is at the checkpoint)
    }

    # Log the event for checkpoint
    log_event(f"Sending TRIP from {checkpoint_id}", trip_message)

    # Send the message to MCP
    send_message(mcp_address, trip_message)
    print(f"TRIP message sent from {checkpoint_id}: {trip_message}")

# Function to keep track of which checkpoint is next in line
current_checkpoint_index = 0
checkpoints = ['CP04', 'CP07', 'CP10', 'CP01']

# Function to send the next TRIP message in the order
def send_next_trip_message():
    global current_checkpoint_index

    if current_checkpoint_index < len(checkpoints):
        cp_id = checkpoints[current_checkpoint_index]
        send_trip_message(cp_id)
        current_checkpoint_index += 1  # Move to the next checkpoint
    else:
        print("All checkpoints have sent their TRIP messages.")
        current_checkpoint_index = 0  # Reset to the beginning if you want to loop again

# Main function to listen for user input and send TRIP messages
def start_checkpoint_simulator():
    print("Checkpoint simulator started. Type 'send' to trigger TRIP messages in order.")

    while True:
        user_input = input("Enter 'send' to send the next TRIP message: ").strip()
        if user_input.lower() == 'send':
            send_next_trip_message()
        else:
            print("Invalid input. Please enter 'send' to trigger the next TRIP message.")

if __name__ == "__main__":
    start_checkpoint_simulator()
