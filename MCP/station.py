import socket
import time
from utils import create_socket, send_message, log_event

# Define the Stations and their ports
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

mcp_address = ('127.0.0.1', 2000)  # MCP address and port

# Sequence numbers to track for each station
seq_numbers = {station_id: 1000 for station_id in station_ports.keys()}

# Set to keep track of initialized stations
initialized_stations = set()

# Function to update the sequence number for each station
def update_sequence_number(st_id):
    seq_numbers[st_id] += 1
    return seq_numbers[st_id]

# Function to send an initialization message from a station
def send_initialization_message(station_id):
    init_message = {
        "client_type": "STC",  # Station client type
        "message": "STIN",
        "client_id": station_id,
        "sequence_number": update_sequence_number(station_id)
    }
    send_message(mcp_address, init_message)
    print(f"Initialization message sent from {station_id}: {init_message}")
    initialized_stations.add(station_id)

# Function to send a TRIP message from a specific station
def send_trip_message(station_id):
    # Check if the station has been initialized
    if station_id not in initialized_stations:
        print(f"Station {station_id} has not been initialized. Cannot send TRIP message.")
        return

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

# Main function to interact with the user
def start_station_simulator():
    print("Station simulator started.")

    # Initialize specific stations
    stations_to_initialize = ['ST01', 'ST03', 'ST04', 'ST05']
    for station_id in stations_to_initialize:
        if station_id in station_ports:
            send_initialization_message(station_id)
            time.sleep(0.1)  # Small delay to avoid overwhelming the MCP
        else:
            print(f"Station {station_id} is not a valid station ID.")

    print("Stations initialized: ", ', '.join(initialized_stations))
    print("You can now send TRIP messages by entering the station ID (e.g., ST01).")
    print("Enter 'exit' to quit the simulator.")

    while True:
        user_input = input("Enter station ID to send TRIP message: ").strip().upper()
        if not user_input:
            continue

        if user_input == 'EXIT':
            print("Exiting station simulator.")
            break
        elif user_input in initialized_stations:
            send_trip_message(user_input)
        elif user_input in station_ports:
            print(f"Station {user_input} has not been initialized. Cannot send TRIP message.")
        else:
            print(f"Invalid station ID: {user_input}. Please enter a valid station ID.")

if __name__ == "__main__":
    start_station_simulator()


# import socket
# import time
# from utils import create_socket, send_message, log_event

# # Define the Stations and their ports
# station_ports = {
#     'ST01': ('127.0.0.1', 4001),
#     'ST04': ('127.0.0.1', 4004),
#     'ST07': ('127.0.0.1', 4007),
#     'ST10': ('127.0.0.1', 4010)
# }

# mcp_address = ('127.0.0.1', 2000)  # MCP address and port

# # Sequence numbers to track for each station
# seq_numbers = {
#     'ST01': 1000,
#     'ST04': 1000,
#     'ST07': 1000,
#     'ST10': 1000,
#     'ST02': 1000,
#     'ST05': 1000,
#     'ST08': 1000,
    
# }

# # Function to update the sequence number for each station
# def update_sequence_number(st_id):
#     seq_numbers[st_id] += 1
#     return seq_numbers[st_id]

# # Function to send a TRIP message from a specific station
# def send_trip_message(station_id):
#     # Create the TRIP message
#     trip_message = {
#         "client_type": "STC",  # Station client type
#         "message": "TRIP",
#         "client_id": station_id,
#         "sequence_number": update_sequence_number(station_id),
#         "status": "ON"  # Simulating that the IR beam is broken (BR is at the station)
#     }

#     # Log the event for station
#     log_event(f"Sending TRIP from {station_id}", trip_message)

#     # Send the message to MCP
#     send_message(mcp_address, trip_message)
#     print(f"TRIP message sent from {station_id}: {trip_message}")

# # Function to keep track of which station is next in line
# current_station_index = 0
# stations = ['ST04', 'ST07', 'ST10', 'ST01', 'ST05', 'ST08', 'ST01', 'ST02' ]

# # Function to send the next TRIP message in the order
# def send_next_trip_message():
#     global current_station_index

#     if current_station_index < len(stations):
#         st_id = stations[current_station_index]
#         send_trip_message(st_id)
#         current_station_index += 1  # Move to the next station
#     else:
#         print("All stations have sent their TRIP messages.")
#         current_station_index = 0  # Reset to the beginning if you want to loop again

# # Main function to listen for user input and send TRIP messages
# def start_station_simulator():
#     print("Station simulator started. Type 'send' to trigger TRIP messages in order.")

#     while True:
#         user_input = input("Enter 'send' to send the next TRIP message: ").strip()
#         if user_input.lower() == 'send':
#             send_next_trip_message()
#         else:
#             print("Invalid input. Please enter 'send' to trigger the next TRIP message.")

# if __name__ == "__main__":
#     start_station_simulator()
