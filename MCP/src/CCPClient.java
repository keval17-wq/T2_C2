
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Timer;
import java.util.TimerTask;
import com.google.gson.*;


public class CCPClient {
    private static final int CCP_PORT = 3000; // Port number for CCP
    private static final String MCP_ADDRESS = "127.0.0.1"; // MCP address (could be different)
    private static final int MCP_PORT = 2001; // MCP port number
    private static final int INTERVAL = 5000; // Interval in milliseconds (5 seconds)

    private final DatagramSocket socket;
    private final InetAddress mcpAddress;
    private final Gson gson;

    public CCPClient() throws Exception {
        // Initialize the socket and Gson instance
        this.socket = new DatagramSocket(CCP_PORT);
        this.mcpAddress = InetAddress.getByName(MCP_ADDRESS);
        this.gson = new Gson();
    }

    public static void main(String[] args) {
        try {
            CCPClient ccp = new CCPClient();
            ccp.startSendingCommands();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void startSendingCommands() {
        Timer timer = new Timer();
        timer.schedule(new SendCommandTask(), 0, INTERVAL); // Start immediately, then repeat every INTERVAL
    }

    private class SendCommandTask extends TimerTask {
        @Override
        public void run() {
            try {
                Command command = createCommand();
                String json = gson.toJson(command);
                sendCommand(json);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        private Command createCommand() {
            // Create a Command object with example data
            return new Command(
                "ccp", // clientType
                "START", // message
                "CCP001", // clientId
                System.currentTimeMillis() / 1000L, // timestamp (current Unix timestamp)
                "START", // action
                "ACTIVE", // status
                null // stationId (optional)
            );
        }

        private void sendCommand(String json) {
            try {
                byte[] data = json.getBytes();
                DatagramPacket packet = new DatagramPacket(data, data.length, mcpAddress, MCP_PORT);
                socket.send(packet);
                System.out.println("Sent command: " + json);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
