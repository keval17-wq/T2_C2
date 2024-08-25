# T2_C2
Server code for MCP

Current Capabilities of the Code:
Here’s what the current implementation can do across all files:

1. MCP.java
Initialization: Starts the MCP and begins listening for connections on port 2000.
Test Mode: Provides a mode to simulate and test command processing without real clients.
Connection Management: Interfaces with the ConnectionManager to handle incoming client connections.
2. ConnectionManager.java
Server Setup: Starts a server on port 2000, listening for incoming connections.
Connection Differentiation: Identifies whether a new connection is from a CCP, Station, or LED Controller based on an initial identification message.
Client Handling: Creates a new ClientHandler for each connection to process commands received from clients.
Command Handling Simulation: In test mode, simulates the handling of commands without needing an actual network socket.
3. CommandDispatcher.java
Command Routing: Routes received commands to the appropriate subsystem based on the client type (CCP, Station, or LED Controller).
Subsystem Command Handling: Provides placeholders to implement specific command handling logic for CCPs, Stations, and LED Controllers.
Next Steps:
Implement Real Command Processing: Build out the logic within CommandDispatcher to handle specific commands like turning on/off an LED, starting/stopping a Blade Runner, or opening/closing a station door.
Addressing Components Individually: Use the specific IP addresses and ports defined in the network setup to direct commands to individual components.
Connection Management Enhancement: Ensure that the MCP maintains persistent connections with all components and handles reconnections, timeouts, or failures as per the requirements.