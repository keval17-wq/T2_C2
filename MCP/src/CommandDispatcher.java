

public class CommandDispatcher {

    public void dispatchCommand(Command command) {
        switch (Command.get(command.clientType)) {
            case "ccp":
                handleCCPCommand(command);
                break;
            case "station":
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

    private void handleCCPCommand(Command command) {
        // Implement CCP-specific command handling logic here
        //handle each payload here
        //update mapping, 
        
    }

    private void handleStationCommand(Command command) {
        // Implement Station-specific command handling logic here
        //update block system
        
        System.out.println("Handling Station command: " + command);
    }

    private void handleLEDControllerCommand(Command command) {
        // Implement LED Controller-specific command handling logic here
        System.out.println("Handling LED Controller command: " + command);
    }
}