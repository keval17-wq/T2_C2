from utils import create_socket, send_message, receive_message, log_event

import time


class LEDControllerManager:
    def __init__(self, track_map):
        self.track_map = track_map
        self.led_sockets = {}  # Dictionary to hold sockets for each LED

        # Create a socket for each LED and start listening
        for block, data in self.track_map.items():
            led = data.get('led')
            if led:
                self.start_led_controller(led)

    def start_led_controller(self, controller_id):
        portnum = 3000 + len(self.led_sockets)  # Assign a unique port number for each LED
        sock = create_socket(portnum)
        self.led_sockets[controller_id] = sock  # Store the socket

        print(f"LED Controller {controller_id} listening on port {portnum}.")
        self.run_led_controller(sock, controller_id)

    def run_led_controller(self, sock, controller_id):
        while True:
            print(f"Waiting for commands at {controller_id}...")
            try:
                message, _ = receive_message(sock)  # Receive message for this LED controller
                self.handle_led_command(controller_id, message)  # Process the command
            except Exception as e:
                print(f"Error receiving message for {controller_id}: {e}")

    def handle_led_command(self, controller_id, message):
        log_event(f"LED Command Received for {controller_id}", message)
        print(f"Executing command for {controller_id}: {message}")

        # Handle different LED commands here (e.g., ON, OFF)
        if 'action' in message:
            action = message['action']
            if action == "ON":
                print(f"Turning on LED {controller_id}")
            elif action == "OFF":
                print(f"Turning off LED {controller_id}")
            # Add more actions as needed

# Example usage
if __name__ == "__main__":
    track_map = {
        'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False, 'led': 'LED01'},
        'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False, 'led': 'LED02'},
        'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True, 'led': 'LED03'},
        'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False, 'led': 'LED04'},
        'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False, 'led': 'LED05'},
    }

    led_controller_manager = LEDControllerManager(track_map)