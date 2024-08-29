package main.java.com.mcp;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class CCP {

    private static final String MCP_IP = "127.0.0.1";  // Replace with the MCP's IP address
    private static final int MCP_PORT = 2001;           // The port MCP is listening on

    public static void main(String[] args) {
        try {
            // Create a DatagramSocket for sending and receiving data
            DatagramSocket socket = new DatagramSocket();

            // Prepare the message to be sent to the MCP
            String message = "Hello from CCP";
            byte[] buffer = message.getBytes();

            // Send the message to the MCP
            InetAddress mcpAddress = InetAddress.getByName(MCP_IP);
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length, mcpAddress, MCP_PORT);
            socket.send(packet);
            System.out.println("Message sent to MCP: " + message);

            // Prepare to receive the response from the MCP
            byte[] receiveBuffer = new byte[1024];
            DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);

            // Receive the response from the MCP
            socket.receive(receivePacket);
            String response = new String(receivePacket.getData(), 0, receivePacket.getLength());
            System.out.println("Received from MCP: " + response);

            // Close the socket
            socket.close();

        } catch (Exception e) {
            System.out.println("Error in CCP: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
