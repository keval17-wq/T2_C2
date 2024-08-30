

public class CommandDispatcher {

    public void dispatchCommand(String clientType, String command) {
        switch (clientType) {
            case "CCP":
                handleCCPCommand(command);
                break;
            case "Station":
                handleStationCommand(command);
                break;
            case "LEDController":
                handleLEDControllerCommand(command);
                break;
            default:
                System.out.println("Unknown client type: " + clientType);
                break;
        }
    }

    private void handleCCPCommand(String command) {
        // Implement CCP-specific command handling logic here
        System.out.println("Handling CCP command: " + command);
    }

    private void handleStationCommand(String command) {
        // Implement Station-specific command handling logic here
        System.out.println("Handling Station command: " + command);
    }

    private void handleLEDControllerCommand(String command) {
        // Implement LED Controller-specific command handling logic here
        System.out.println("Handling LED Controller command: " + command);
    }
}