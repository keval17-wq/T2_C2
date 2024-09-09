from utils import create_udp_socket, send_udp_message, receive_udp_message, log_event

def start_ccp(ccp_id):
    print(f"Starting CCP for Blade Runner {ccp_id}...")
    ccp_socket = create_udp_socket(3003)  # Using port 2001 to listen and send messages
    send_initialization(ccp_socket, ccp_id)

    while True:
        print("Waiting for MCP commands...")
        message, _ = receive_udp_message(ccp_socket)
        handle_mcp_command(message)

def send_initialization(socket, ccp_id):
    init_message = {
        "client_type": "ccp",
        "message": "CCIN",
        "client_id": ccp_id
    }
    print(f"Sending initialization message to MCP: {init_message}")
    send_udp_message(("127.0.0.1", 2001), init_message) # Replace it with MCP IP address

def handle_mcp_command(message):
    log_event("MCP Command Received", message)
    print(f"Executing MCP command: {message}")

if __name__ == "__main__":
    start_ccp("BR3")
