import time
from utils import create_socket, send_message, receive_message, log_event

station_ports = {
    'ST01': 4001,
    'ST02': 4002,
    'ST03': 4003,
    'ST04': 4004,
    'ST05': 4005,
    'ST06': 4006,
    'ST07': 4007,
    'ST08': 4008,
    'ST09': 4009,
    'ST10': 4010
}

mcp_address = ('127.0.0.1', 2001)

def start_station(station_id):
    port = station_ports[station_id]
    sock = create_socket(port)
    print(f"Station {station_id} listening on port {port}.")

    while True:
        print(f"Waiting for MCP commands at {station_id}...")
        message, _ = receive_message(sock)
        handle_mcp_command(station_id, message)

def handle_mcp_command(station_id, message):
    if message['message'] == "DOOR":
        action = message['action']
        log_event(f"Station {station_id} Door Action", action)
        print(f"Station {station_id}: Door {action}")
        # Simulate door action
        if action == "OPEN":
            time.sleep(3)  # Simulate opening time
        elif action == "CLOSE":
            time.sleep(3)  # Simulate closing time
    if message['message'] == "IRLD": # Method to handle off and on LED commands from MCP
        action = message['action']
        log_event(f"Station {station_id} IRLD Action", action)
        print(f"Station {station_id}: IRLD {action}")
        if action == "ON":
         print(f"LED Turned ON at {station_id}" )
        elif action == "OFF":
         print(f"LED Turned OFF at {station_id}" )

if __name__ == "__main__":
    start_station('ST01')
