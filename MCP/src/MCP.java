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
    public Map<String, ClientInfo> addressMap = new HashMap<String , ClientInfo>();

    private final Map<String, PendingMessage> pendingMessages = new HashMap<>();
    private final StateManager stateManager = new StateManager();
    private final CommandProcessor commandProcessor = new CommandProcessor(stateManager, new Logger());

    public static void main(String[] args) {
        new MCP().start();
    }

    public void start() {
        try (DatagramSocket socket = new DatagramSocket(MCP_PORT)) {
            Logger.log("MCP is listening on port " + MCP_PORT);
            byte[] buffer = new byte[BUFFER_SIZE];

            while (true) {
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                handleMessage(packet, packet.getAddress(), packet.getPort(), socket);
            }
        } catch (Exception e) {
            Logger.logError("Error in MCP: " + e.getMessage());
        }
    }

    private void handleMessage(DatagramPacket pack, InetAddress senderAddress, int senderPort, DatagramSocket socket) {
        
        try{
            //update map with info here TODO
            Command c = commandProcessor.parseCommand(pack);
            
            String response = commandProcessor.processCommand(c, senderAddress); //This Logic needs to be CHANGED
            sendResponse(response, senderAddress, senderPort, socket); //send command to processor here
            addressMap.put(c.getClientId(), new ClientInfo(senderAddress, senderPort));//Map client ID and senderaddress/port
            //try to send command to host here
        //process command returns the string message that should be sent. not in full JSON format yet
        //as the command processor needs to be flehsed out to create each command and message type. So for now only
        //returns a single vary basic string
        }

        catch (Exception e){
            System.out.println("Failed to build a response in handleMessage");
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
            Logger.logError("Error sending response: " + e.getMessage());
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
                    Logger.log("Retransmitting message ID: " + pendingMessage.messageId);
                    pendingMessage.socket.send(pendingMessage.packet);
                    pendingMessage.retries++;
                } catch (Exception e) {
                    Logger.logError("Error retransmitting message: " + e.getMessage());
                }
            } else {
                Logger.logError("Max retries reached for message ID: " + pendingMessage.messageId + ". Giving up.");
                pendingMessages.remove(pendingMessage.messageId);
                this.cancel();
            }
        }
    }
}