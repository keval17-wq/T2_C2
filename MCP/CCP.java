import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class CCP {
    private static final int MCP_PORT = 2001;
    private static final int CCP_PORT = 2002;
    private static DatagramSocket ccpSocket;

    public static void main(String[] args) {
        String ccpId = "BR01";
        startCCP(ccpId);
    }

    public static void startCCP(String ccpId) {
        System.out.println("Starting CCP for Blade Runner " + ccpId + "...");
        try {
            ccpSocket = new DatagramSocket(CCP_PORT); // Using port 2002 to listen and send messages
            sendInitialization(ccpId);

            while (true) {
                System.out.println("Waiting for MCP commands...");
                byte[] buffer = new byte[1024];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                ccpSocket.receive(packet);
                String message = new String(packet.getData(), 0, packet.getLength());
                handleMCPCommand(message);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void sendInitialization(String ccpId) {
        try {
            String initMessage = "{\"client_type\": \"ccp\", \"message\": \"CCIN\", \"client_id\": \"" + ccpId + "\"}";
            System.out.println("Sending initialization message to MCP: " + initMessage);
            byte[] messageBytes = initMessage.getBytes();
            InetAddress mcpAddress = InetAddress.getByName("127.0.0.1"); // Replace with MCP IP address
            DatagramPacket packet = new DatagramPacket(messageBytes, messageBytes.length, mcpAddress, MCP_PORT);
            ccpSocket.send(packet);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void handleMCPCommand(String message) {
        logEvent("MCP Command Received", message);
        System.out.println("Executing MCP command: " + message);
    }

    public static void logEvent(String event, String message) {
        // Implement your logging logic here
        System.out.println(event + ": " + message);
    }
}
