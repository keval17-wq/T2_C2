from utils import create_socket, send_message, receive_message, log_event
import time

MCP_IP = '127.0.0.1'
MCP_PORT = 2000

sequence_number = 1000

def start_ccp(ccp_id):
    print(f"Starting CCP for Blade Runner {ccp_id}...")
    ccp_socket = create_socket(3005)  # Use port 3005 for BR05
    send_initialization(ccp_socket, ccp_id)

    while True:
        print("Waiting for MCP commands...")
        message, _ = receive_message(ccp_socket)
        handle_mcp_command(message, ccp_id)

def update_sequence_number():
    global sequence_number
    sequence_number += 1
    return sequence_number

def send_initialization(socket, ccp_id):
    init_message = {
        "client_type": "CCP",
        "message": "CCIN",
        "client_id": ccp_id,
        "sequence_number": update_sequence_number()
    }
    print(f"Sending initialization message to MCP: {init_message}")
    send_message((MCP_IP, MCP_PORT), init_message)

def handle_mcp_command(message, ccp_id):
    log_event("MCP Command Received", message)

    action = message.get('action')

    if action == "START":
        handle_start(ccp_id)
    elif action == "STOP":
        handle_stop(ccp_id)
    elif action == "MOVE_TO_NEXT_BLOCK":
        handle_move_to_next_block(ccp_id)
    elif action == "SLOW":
        handle_slow(ccp_id, message.get('turn_severity', 0))
    elif action == "EMERGENCY_STOP":
        handle_emergency_stop(ccp_id)
    elif action == "DOOR":
        handle_door_control(message['action'], ccp_id)
    elif action == "TRIP":
        handle_trip_signal(ccp_id)
    else:
        print(f"Unknown command received: {message}")

    send_acknowledgment(message['sequence_number'], ccp_id)

def send_acknowledgment(received_sequence, ccp_id):
    ack_message = {
        "client_type": "CCP",
        "message": "AKEX",
        "client_id": ccp_id,
        "sequence_number": received_sequence
    }
    print(f"Sending acknowledgment to MCP: {ack_message}")
    send_message((MCP_IP, MCP_PORT), ack_message)

def handle_start(ccp_id):
    print(f"BR {ccp_id} starting as per MCP command.")
    send_status_update(ccp_id, "FFASTC")

def handle_stop(ccp_id):
    print(f"BR {ccp_id} stopping as per MCP command.")
    send_status_update(ccp_id, "STOPC")

def handle_move_to_next_block(ccp_id):
    print(f"BR {ccp_id} moving to the next block as per MCP command.")
    send_status_update(ccp_id, "moved_to_next_block")

def handle_slow(ccp_id, severity):
    print(f"BR {ccp_id} slowing down for turn with severity {severity}.")
    send_status_update(ccp_id, f"slowed_for_turn_severity_{severity}")

def handle_emergency_stop(ccp_id):
    print(f"BR {ccp_id} performing emergency stop as per MCP command.")
    send_status_update(ccp_id, "emergency_stopped")

def handle_door_control(action, ccp_id):
    print(f"BR {ccp_id} doors are being {action} as per MCP command.")
    send_status_update(ccp_id, f"doors_{action}")

def handle_trip_signal(ccp_id):
    print(f"BR {ccp_id} trip sensor activated.")
    send_status_update(ccp_id, "trip_sensor_activated")

def send_status_update(ccp_id, status):
    status_message = {
        "client_type": "CCP",
        "message": "STAT",
        "client_id": ccp_id,
        "sequence_number": update_sequence_number(),
        "status": status
    }
    print(f"Sending status update to MCP: {status_message}")
    send_message((MCP_IP, MCP_PORT), status_message)

if __name__ == "__main__":
    start_ccp("BR05")
