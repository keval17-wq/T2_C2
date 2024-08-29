package main.java.com.mcp;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class CCP {

    private static final String MCP_IP = "137.111.13.126";  // Replace with your MCP's IP address
    private static final int MCP_PORT = 2001;               // The port MCP is listening on

    public static void main(String[] args) {
        try (DatagramSocket socket = new DatagramSocket()) {
            // Initialize communication with the MCP
            sendCommand(socket, "CCIN", "CC01");

            // Wait for acknowledgment or further commands from MCP
            receiveResponse(socket);

            // Send status update to MCP
            sendCommand(socket, "STAT", "CC01", "STOPPED");

            // Receive further instructions from MCP
            receiveResponse(socket);

        } catch (Exception e) {
            System.out.println("Error in CCP: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void sendCommand(DatagramSocket socket, String commandType, String clientId) throws Exception {
        sendCommand(socket, commandType, clientId, "");
    }

    private static void sendCommand(DatagramSocket socket, String commandType, String clientId, String status) throws Exception {
        // Prepare the message in the defined JSON structure
        String message = String.format(
            "{ \"client_type\": \"ccp\", \"message\": \"%s\", \"client_id\": \"%s\", \"timestamp\": \"%d\", \"status\": \"%s\" }",
            commandType, clientId, System.currentTimeMillis(), status
        );

        // Send the message to the MCP
        InetAddress mcpAddress = InetAddress.getByName(MCP_IP);
        byte[] buffer = message.getBytes();
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length, mcpAddress, MCP_PORT);
        socket.send(packet);
        System.out.println("Message sent to MCP: " + message);
    }

    private static void receiveResponse(DatagramSocket socket) throws Exception {
        // Prepare to receive the response from the MCP
        byte[] receiveBuffer = new byte[1024];
        DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);

        // Receive the response from the MCP
        socket.receive(receivePacket);
        String response = new String(receivePacket.getData(), 0, receivePacket.getLength());
        System.out.println("Received from MCP: " + response);
    }
}
