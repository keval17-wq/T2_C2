import socket
import time
from utils import create_socket, send_message, log_event

# Define the Stations and their ports
station_ports = {
    'ST01': ('127.0.0.1', 4001),
    'ST04': ('127.0.0.1', 4004),
    'ST07': ('127.0.0.1', 4007),
    'ST10': ('127.0.0.1', 4010)
}

mcp_address = ('127.0.0.1', 2000)  # MCP address and port

# Sequence numbers to track for each station
sequence_numbers = {
    'ST01': 1000,
    'ST04': 1000,
    'ST07': 1000,
    'ST10': 1000
}

# Function to update the sequence number for each station
def update_sequence_number(st_id):
    sequence_numbers[st_id] += 1
    return sequence_numbers[st_id]

# Function to send a TRIP message from a specific station
def send_trip_message(station_id):
    # Create the TRIP message
    trip_message = {
        "client_type": "STC",  # Station client type
        "message": "TRIP",
        "client_id": station_id,
        "sequence_number": update_sequence_number(station_id),
        "status": "ON"  # Simulating that the IR beam is broken (BR is at the station)
    }

    # Log the event for station
    log_event(f"Sending TRIP from {station_id}", trip_message)

    # Send the message to MCP
    send_message(mcp_address, trip_message)
    print(f"TRIP message sent from {station_id}: {trip_message}")

# Function to keep track of which station is next in line
current_station_index = 0
stations = ['ST04', 'ST07', 'ST10', 'ST01']

# Function to send the next TRIP message in the order
def send_next_trip_message():
    global current_station_index

    if current_station_index < len(stations):
        st_id = stations[current_station_index]
        send_trip_message(st_id)
        current_station_index += 1  # Move to the next station
    else:
        print("All stations have sent their TRIP messages.")
        current_station_index = 0  # Reset to the beginning if you want to loop again

# Main function to listen for user input and send TRIP messages
def start_station_simulator():
    print("Station simulator started. Type 'send' to trigger TRIP messages in order.")

    while True:
        user_input = input("Enter 'send' to send the next TRIP message: ").strip()
        if user_input.lower() == 'send':
            send_next_trip_message()
        else:
            print("Invalid input. Please enter 'send' to trigger the next TRIP message.")

if __name__ == "__main__":
    start_station_simulator()
