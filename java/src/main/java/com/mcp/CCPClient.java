package main.java.com.mcp;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

public class CCPClient {
    public static void main(String[] args) {
        String serverAddress = "localhost"; // MCP's IP address
        int serverPort = 2000; // MCP's listening port

        try (Socket socket = new Socket(serverAddress, serverPort)) {
            System.out.println("Connected to MCP");

            // Send a simple message to MCP
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            out.println("Hello MCP, this is CCP");

            // Close the connection after sending the message
            socket.close();
            System.out.println("Connection closed");

        } catch (IOException e) {
            System.out.println("Error connecting to MCP: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
