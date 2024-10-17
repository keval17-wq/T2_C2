from utils import create_socket, send_message, receive_message, log_event
import time

# Checkpoint static configurations (simulating line break sensors and IR LED)
checkpoint_ports = {
    'CP01': 5001,
    'CP02': 5002,
    'CP03': 5003,
    'CP04': 5004,
    'CP05': 5005,
    'CP06': 5006,
    'CP07': 5007,
    'CP08': 5008,
    'CP09': 5009,
    'CP10': 5010
}

mcp_address = ('127.0.0.1', 2001)

def start_checkpoint(checkpoint_id):
    port = checkpoint_ports[checkpoint_id]
    sock = create_socket(port)
    print(f"Checkpoint {checkpoint_id} started on port {port}.")
    
    while True:
        print(f"Checkpoint {checkpoint_id} monitoring BRs...")
        # Simulate BR passing through
        time.sleep(5)  # Simulate time before TRIP (adjust as needed)
        send_trip_message(checkpoint_id, port)
        time.sleep(10)  # Delay to simulate next TRIP

def send_trip_message(checkpoint_id, port):
    message = {
        "client_type": "checkpoint",
        "client_id": checkpoint_id,
        "message": "TRIP",

    }
    send_message(mcp_address, message)
    log_event(f"TRIP at {checkpoint_id}", message)

if __name__ == "__main__":
    start_checkpoint('CP01')
