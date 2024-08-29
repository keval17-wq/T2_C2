package main.java.com.mcp;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.HashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

public class MCP {
    private static final int MCP_PORT = 2001;
    private static final int BUFFER_SIZE = 1024;
    private static final int ACK_TIMEOUT = 3000; // 3 seconds for acknowledgment timeout

    private final Map<String, PendingMessage> pendingMessages = new HashMap<>();

    public static void main(String[] args) {
        new MCP().start();
    }

    public void start() {
        try (DatagramSocket socket = new DatagramSocket(MCP_PORT)) {
            System.out.println("MCP is listening on port " + MCP_PORT);
            byte[] buffer = new byte[BUFFER_SIZE];

            while (true) {
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                handleMessage(new String(packet.getData(), 0, packet.getLength()), packet.getAddress(), packet.getPort(), socket);
            }
        } catch (Exception e) {
            System.err.println("Error in MCP: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void handleMessage(String message, InetAddress senderAddress, int senderPort, DatagramSocket socket) {
        if (message.startsWith("ACK")) {
            pendingMessages.remove(message.split(":")[1].trim());
            System.out.println("Acknowledgment received.");
        } else {
            sendResponse("Acknowledged: " + message, senderAddress, senderPort, socket);
        }
    }

    private void sendResponse(String response, InetAddress recipientAddress, int recipientPort, DatagramSocket socket) {
        try {
            String messageId = String.valueOf(System.currentTimeMillis());
            byte[] responseData = (response + " ID:" + messageId).getBytes();
            DatagramPacket responsePacket = new DatagramPacket(responseData, responseData.length, recipientAddress, recipientPort);
            socket.send(responsePacket);

            PendingMessage pendingMessage = new PendingMessage(responsePacket, socket, messageId);
            pendingMessages.put(messageId, pendingMessage);

            new Timer().schedule(new RetransmissionTask(pendingMessage), ACK_TIMEOUT, ACK_TIMEOUT);
        } catch (Exception e) {
            System.err.println("Error sending response: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static class PendingMessage {
        DatagramPacket packet;
        DatagramSocket socket;
        String messageId;
        int retries = 0;

        PendingMessage(DatagramPacket packet, DatagramSocket socket, String messageId) {
            this.packet = packet;
            this.socket = socket;
            this.messageId = messageId;
        }
    }

    private class RetransmissionTask extends TimerTask {
        private final PendingMessage pendingMessage;

        RetransmissionTask(PendingMessage pendingMessage) {
            this.pendingMessage = pendingMessage;
        }

        @Override
        public void run() {
            if (!pendingMessages.containsKey(pendingMessage.messageId)) {
                this.cancel();
                return;
            }

            if (pendingMessage.retries < 3) {
                try {
                    System.out.println("Retransmitting message ID: " + pendingMessage.messageId);
                    pendingMessage.socket.send(pendingMessage.packet);
                    pendingMessage.retries++;
                } catch (Exception e) {
                    System.err.println("Error retransmitting message: " + e.getMessage());
                    e.printStackTrace();
                }
            } else {
                System.out.println("Max retries reached for message ID: " + pendingMessage.messageId + ". Giving up.");
                pendingMessages.remove(pendingMessage.messageId);
                this.cancel();
            }
        }
    }
}
