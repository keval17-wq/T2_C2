
import java.net.DatagramPacket;
import java.net.InetAddress;
import com.google.gson.*;

public class CommandProcessor {
    private final StateManager stateManager;
    private final Logger logger;

    public CommandProcessor(StateManager stateManager, Logger logger) {
        this.stateManager = stateManager;
        this.logger = logger;
    }

   

    public String processCommand(Command command, InetAddress senderAddress) { //Process command and update state
        String response = "Invalid Command"; //remember we have to call parse command
        //first, then we call process command! better modularity
        //and get the clienttype so we can handle diferent types
        //this needs to send an ENTIRE json command string

        //if statemetns for each client type

        switch (command.getStatus()) { //just get the ACTION part here
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

    public Command parseCommand(DatagramPacket packet){
    Command command = new Command();

        try{
        String com = new String(packet.getData(), 0, packet.getLength());
        Gson gson = new Gson();
         command = gson.fromJson(com, Command.class);
        }

        catch (Exception e) {
            e.printStackTrace();
            return null; // or handle the error appropriately
        }
return command;
//now we have an object that nicely can get each field
    }
}