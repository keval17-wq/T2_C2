from utils import create_udp_socket, send_udp_message, receive_udp_message, log_event

def start_led_controller(controller_id):
    print(f"Starting LED Controller {controller_id}...")
    controller_socket = create_udp_socket(2004)  # Using port 2001 to listen and send messages
    send_initialization(controller_socket, controller_id)

    while True:
        print("Waiting for MCP commands...")
        message, _ = receive_udp_message(controller_socket)
        handle_mcp_command(message)

def send_initialization(socket, controller_id):
    init_message = {
        "client_type": "led_controller",
        "message": "LCIN",
        "client_id": controller_id
    }
    print(f"Sending initialization message to MCP: {init_message}")
    send_udp_message(("127.0.0.1", 2001), init_message) # Replace it with MCP IP address

def handle_mcp_command(message):
    log_event("MCP Command Received", message)
    print(f"Executing LED command: {message}")

if __name__ == "__main__":
    start_led_controller("LED01")
