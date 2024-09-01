import socket
import time

def handle_mcp_command(command, writer):
    # Example: Handle commands sent by MCP based on the track layout
    if command == "SPED FORWARD":
        print("CCP: Moving carriage forward.")
        # Implement logic to move carriage forward
    elif command == "SPED STOP":
        print("CCP: Stopping carriage.")
        # Implement logic to stop carriage
    elif command == "DOOR OPEN":
        print("CCP: Opening carriage doors.")
        # Implement logic to open doors
    elif command == "DOOR CLOSE":
        print("CCP: Closing carriage doors.")
        # Implement logic to close doors
    else:
        print("CCP: Received unknown command.")

def main():
    hostname = "127.0.0.1"  # MCP server address
    port = 2001  # Ensure this matches the server port

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((hostname, port))
            print("CCP connected to MCP")

            writer = s.makefile('w')
            reader = s.makefile('r')

            # Send initial identification
            writer.write("CCP\n")
            writer.flush()

            # Simulate sending carriage status updates to MCP
            writer.write("Carriage entering Block1\n")
            writer.flush()
            print("CCP sent: Carriage entering Block1")

            time.sleep(2)

            writer.write("Carriage arriving at Station B\n")
            writer.flush()
            print("CCP sent: Carriage arriving at Station B")

            # Keep the connection open and listen for commands
            while True:
                command = reader.readline().strip()
                if command:
                    print(f"CCP received command: {command}")
                    handle_mcp_command(command, writer)

    except socket.gaierror as ex:
        print(f"Server not found: {ex}")
    except socket.error as ex:
        print(f"I/O error: {ex}")
    except KeyboardInterrupt:
        print("Thread interrupted")

if __name__ == "__main__":
    main()