from utils import create_udp_socket, send_udp_message, receive_udp_message, log_event

def start_station(station_id):
    print(f"Starting Station {station_id}...")
    station_socket = create_udp_socket(2003)  # Using port 2001 to listen and send messages
    send_initialization(station_socket, station_id)

    while True:
        print("Waiting for MCP commands...")
        message, _ = receive_udp_message(station_socket)
        handle_mcp_command(message)

def send_initialization(socket, station_id):
    init_message = {
        "client_type": "station",
        "message": "STIN",
        "client_id": station_id
    }
    print(f"Sending initialization message to MCP: {init_message}")
    send_udp_message(("127.0.0.1", 2001), init_message) # Replace it with MCP IP address

def handle_mcp_command(message):
    log_event("MCP Command Received", message)
    print(f"Executing MCP command at Station {message}")

if __name__ == "__main__":
    start_station("ST01")
