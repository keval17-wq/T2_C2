import socket
import threading
import time
import logging

class TrackNetwork:
    def __init__(self):
        self.stations = {}
        self.checkpoints = {}
        self.blocks = {}
        self.carriages = {}

    def add_station(self, name):
        self.stations[name] = {}

    def add_checkpoint(self, name):
        self.checkpoints[name] = {}

    def add_block(self, name):
        self.blocks[name] = {'led_state': False}

    def connect(self, from_node, to_node, distance, speed_limit):
        # Implement connection logic
        pass

    def print_track(self):
        # Implement track printing logic
        pass

    def add_carriage(self, carriage_id, initial_block):
        self.carriages[carriage_id] = initial_block

    def get_block(self, block_name):
        return self.blocks.get(block_name)

class MCPServer:
    def __init__(self, port):
        self.port = port
        self.track_network = TrackNetwork()
        self.carriage_locations = {}
        self.load_track_configuration()
        self.initialize_carriages()

    def load_track_configuration(self):
        self.track_network.add_station("A")
        self.track_network.add_checkpoint("Checkpoint1")
        self.track_network.add_station("B")
        self.track_network.add_checkpoint("Checkpoint2")

        for i in range(1, 11):
            self.track_network.add_block(f"Block{i}")

        self.track_network.connect("A", "Checkpoint1", 2, 0.3)
        self.track_network.connect("Checkpoint1", "B", 3, 1.0)
        self.track_network.connect("Checkpoint1", "A", 2, 0.3)
        self.track_network.connect("B", "Checkpoint2", 4, 0.0)
        self.track_network.connect("Checkpoint2", "Checkpoint1", 3, 1.0)

        self.track_network.print_track()

    def initialize_carriages(self):
        for i in range(1, 6):
            carriage_id = f"BR{i}"
            initial_block = f"Block{i}"
            self.track_network.add_carriage(carriage_id, initial_block)
            self.carriage_locations[carriage_id] = initial_block

        print("Carriages initialized:")
        self.track_network.print_track()

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', self.port))
            server_socket.listen()
            print(f"MCP is listening on port {self.port}")

            while True:
                conn, addr = server_socket.accept()
                print(f"Connected to client at {addr}")
                threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        with conn:
            client_type = conn.recv(1024).decode().strip()
            print(f"Client type: {client_type}")

            if client_type == "CCP":
                self.handle_ccp_client(conn)
            elif client_type == "ESP32":
                self.handle_esp32_client(conn)
            elif client_type == "LED_CONTROLLER":
                self.handle_led_controller_client(conn)

    def handle_ccp_client(self, conn):
        while True:
            message = conn.recv(1024).decode().strip()
            if not message:
                break
            print(f"MCP received from CCP: {message}")

            message_parts = message.split(" ")
            if len(message_parts) < 5:
                print(f"Invalid message format received from CCP: {message}")
                continue

            if message.startswith("Carriage entering "):
                carriage_id = message_parts[2]
                new_block = message_parts[4]
                self.carriage_locations[carriage_id] = new_block
                print(f"Updated location for {carriage_id}: {new_block}")
                self.handle_block_transition(carriage_id, new_block)
            elif message == "Carriage stopped":
                print("Carriage stopped as per protocol.")

    def handle_esp32_client(self, conn):
        while True:
            message = conn.recv(1024).decode().strip()
            if not message:
                break
            print(f"MCP received from ESP32: {message}")

            if message.startswith("Carriage detected at Block"):
                block_name = message.split(" ")[3]
                print(f"Handling carriage detection at {block_name}")
                self.handle_ir_sensor_detection(block_name)

    def handle_led_controller_client(self, conn):
        while True:
            message = conn.recv(1024).decode().strip()
            if not message:
                break
            # Handle any incoming data if needed

        print("LED Controller connection closed manually.")

    def handle_block_transition(self, carriage_id, new_block):
        previous_block = self.carriage_locations.get(carriage_id)
        if previous_block and previous_block != new_block:
            self.track_network.get_block(previous_block)['led_state'] = False
            self.send_command_to_led_controller(f"TURN_OFF_LED at {previous_block}")

            self.track_network.get_block(new_block)['led_state'] = True
            self.send_command_to_led_controller(f"TURN_ON_LED at {new_block}")

            print(f"Handled block transition for {carriage_id} from {previous_block} to {new_block}")

    def handle_ir_sensor_detection(self, block_name):
        block = self.track_network.get_block(block_name)
        if block:
            block['led_state'] = True
            self.send_command_to_led_controller(f"TURN_ON_LED at {block_name}")

            block_number = int(block_name[5:])
            if block_number > 1:
                previous_block_name = f"Block{block_number - 1}"
                previous_block = self.track_network.get_block(previous_block_name)
                if previous_block:
                    previous_block['led_state'] = False
                    self.send_command_to_led_controller(f"TURN_OFF_LED at {previous_block_name}")

    def send_command_to_led_controller(self, command):
        print(f"MCP would send command to LED Controller: {command}")

if __name__ == "__main__":
    server = MCPServer(port=2001)
    server.start_server()