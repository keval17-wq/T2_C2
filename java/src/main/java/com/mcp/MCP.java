package main.java.com.mcp;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class MCP {
    private static final int MCP_PORT = 2001;

    public static void main(String[] args) {
        try {
            // Create a DatagramSocket to listen on the specified port
            DatagramSocket socket = new DatagramSocket(MCP_PORT);
            System.out.println("MCP is listening on port " + MCP_PORT);

            // Buffer to receive incoming packets
            byte[] buffer = new byte[1024];

            while (true) {
                // Create a DatagramPacket to receive incoming data
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);

                // Receive the packet
                socket.receive(packet);

                // Extract data from the packet
                String received = new String(packet.getData(), 0, packet.getLength());
                System.out.println("Received: " + received);

                // Get the sender's address and port
                InetAddress senderAddress = packet.getAddress();
                int senderPort = packet.getPort();

                // Send a response
                String response = "Acknowledged: " + received;
                byte[] responseData = response.getBytes();
                DatagramPacket responsePacket = new DatagramPacket(responseData, responseData.length, senderAddress, senderPort);
                socket.send(responsePacket);

                System.out.println("Response sent to " + senderAddress + ":" + senderPort);
            }
        } catch (Exception e) {
            System.out.println("Error in MCP: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
