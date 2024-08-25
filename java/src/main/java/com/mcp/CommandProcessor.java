package main.java.com.mcp;

public class CommandProcessor {

    public void processCommand(String command) {
        switch (command.toUpperCase()) {
            case "START":
                System.out.println("Received START command. Initiating BR movement.");
                // Logic to start BR movement
                break;

            case "STOP":
                System.out.println("Received STOP command. Halting BR movement.");
                // Logic to stop BR movement
                break;

            case "STATUS":
                System.out.println("Received STATUS command. Reporting system status.");
                // Logic to report system status
                break;

            default:
                System.out.println("Received unknown command: " + command);
                // Handle unknown commands
                break;
        }
    }
}
