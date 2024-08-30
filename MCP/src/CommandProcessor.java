
import java.net.InetAddress;

public class CommandProcessor {
    private final StateManager stateManager;
    private final Logger logger;

    public CommandProcessor(StateManager stateManager, Logger logger) {
        this.stateManager = stateManager;
        this.logger = logger;
    }

    public String processCommand(String command, InetAddress senderAddress) {
        String response = "Invalid Command";

        switch (command.toUpperCase()) {
            case "START":
                response = "BR Started";
                stateManager.updateState(senderAddress.getHostAddress(), "STARTED");
                break;
            case "STOP":
                response = "BR Stopped";
                stateManager.updateState(senderAddress.getHostAddress(), "STOPPED");
                break;
            case "STATUS":
                response = "Current State: " + stateManager.getState(senderAddress.getHostAddress());
                break;
            case "DOOR OPEN":
                response = "Doors Opened";
                stateManager.updateState(senderAddress.getHostAddress(), "DOOR_OPENED");
                break;
            case "DOOR CLOSE":
                response = "Doors Closed";
                stateManager.updateState(senderAddress.getHostAddress(), "DOOR_CLOSED");
                break;
            case "IRLD ON":
                response = "IR LED On";
                stateManager.updateState(senderAddress.getHostAddress(), "IRLD_ON");
                break;
            case "IRLD OFF":
                response = "IR LED Off";
                stateManager.updateState(senderAddress.getHostAddress(), "IRLD_OFF");
                break;
            default:
                logger.log("Unknown command received: " + command);
                break;
        }

        logger.log("Processed command: " + command + " from " + senderAddress.getHostAddress());
        return response;
    }
}