package main.java.com.mcp;

public class MCP {

    public static void main(String[] args) {
        boolean testMode = false; // Set to true for testing, false for normal operation

        // Initialize the modules
        ConnectionManager connectionManager = new ConnectionManager();

        // Start the MCP and begin listening for connections
        connectionManager.start();

        if (testMode) {
            runTests(connectionManager);
        }
    }

    private static void runTests(ConnectionManager connectionManager) {
        System.out.println("Running tests...");

        // Simulate receiving a START command
        CommandProcessor commandProcessor = new CommandProcessor();
        System.out.println("Test 1: START command");
        commandProcessor.processCommand("START");

        // Simulate receiving a STOP command
        System.out.println("Test 2: STOP command");
        commandProcessor.processCommand("STOP");

        // Simulate receiving a STATUS command
        System.out.println("Test 3: STATUS command");
        commandProcessor.processCommand("STATUS");

        // Simulate receiving an unknown command
        System.out.println("Test 4: Unknown command");
        commandProcessor.processCommand("UNKNOWN");

        // Simulate a connection (fake it by calling the ClientHandler directly)
        System.out.println("Test 5: Simulate a connection");
        simulateConnection(connectionManager);

        System.out.println("All tests completed.");
    }

    private static void simulateConnection(ConnectionManager connectionManager) {
        // Since we can't actually open a socket in this test, we'll simulate the connection handling
        try {
            // Simulate a client sending commands
            String[] simulatedCommands = {"START", "STOP", "STATUS", "INVALID"};

            for (String command : simulatedCommands) {
                System.out.println("Simulating command: " + command);
                connectionManager.new ClientHandler(null).runTestCommand(command);
            }

        } catch (Exception e) {
            System.out.println("Error during simulated connection: " + e.getMessage());
        }
    }
}
