package main.java.com.mcp;

import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ConnectionManager {

  private static final int MCP_PORT = 2000;
  private ExecutorService executorService;
  private List<Socket> ccpConnections; // List of connected CCP clients
  private List<Socket> stationConnections; // List of connected station clients
  private List<Socket> ledControllerConnections; // List of connected LED controller clients

  public ConnectionManager() {
    executorService = Executors.newCachedThreadPool();
    ccpConnections = new ArrayList<>();
    stationConnections = new ArrayList<>();
    ledControllerConnections = new ArrayList<>();
  }

  // The start() method which is responsible for starting the server
  public void start() {
    try (ServerSocket serverSocket = new ServerSocket(MCP_PORT)) {
      System.out.println("MCP is listening on port " + MCP_PORT);

      while (true) {
        Socket socket = serverSocket.accept();
        System.out.println("New connection established");

        // Determine the type of connection
        String clientType = identifyClientType(socket);
        if (clientType != null) {
          switch (clientType) {
            case "CCP":
              ccpConnections.add(socket);
              System.out.println("CCP connected.");
              break;
            case "Station":
              stationConnections.add(socket);
              System.out.println("Station connected.");
              break;
            case "LEDController":
              ledControllerConnections.add(socket);
              System.out.println("LED Controller connected.");
              break;
            default:
              System.out.println("Unknown client type.");
              socket.close(); // Close the connection if client type is unknown
              continue;
          }
        }

        executorService.submit(new ClientHandler(socket, clientType));
      }

    } catch (IOException e) {
      System.out.println("Error while setting up the MCP server: " + e.getMessage());
      e.printStackTrace();
    }
  }

  // Method to identify the client type based on an initial message
  private String identifyClientType(Socket socket) {
    try (InputStream inputStream = socket.getInputStream()) {
      byte[] buffer = new byte[1024];
      int bytesRead = inputStream.read(buffer);
      if (bytesRead > 0) {
        String initialMessage = new String(buffer, 0, bytesRead).trim();
        return initialMessage;
      }
    } catch (IOException e) {
      System.out.println("Error identifying client type: " + e.getMessage());
    }
    return null;
  }

  // Optionally, you could also implement a stop method if needed
  public void stop() {
    System.out.println("Stopping ConnectionManager...");
    executorService.shutdown();
  }

  // Inner class for handling client connections
  public class ClientHandler implements Runnable {
    private Socket socket;
    private String clientType;
    private CommandDispatcher commandDispatcher;

    public ClientHandler(Socket socket, String clientType) {
      this.socket = socket;
      this.clientType = clientType;
      this.commandDispatcher = new CommandDispatcher();
    }

    @Override
    public void run() {
      try (InputStream inputStream = socket.getInputStream()) {
        byte[] buffer = new byte[1024];
        int bytesRead;

        while ((bytesRead = inputStream.read(buffer)) != -1) {
          String command = new String(buffer, 0, bytesRead).trim();
          System.out.println("Received command: " + command);
          commandDispatcher.dispatchCommand(clientType, command);
        }
      } catch (IOException e) {
        System.out.println("Error handling client connection: " + e.getMessage());
      }
    }

    // Simulated method for testing without a real socket
    public void runTestCommand(String command) {
      CommandProcessor commandProcessor = new CommandProcessor();
      commandProcessor.processCommand(command);
    }
  }
}
