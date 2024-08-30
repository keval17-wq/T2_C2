public class Command {
    private String clientType;  // Specifies the type of client (e.g., ccp, station, checkpoint)
    private String message;     // The type of message or command being sent (e.g., AKIN, STAT, EXEC, DOOR, IRLD)
    private String clientId;    // The unique identifier for the client sending or receiving the message
    private long timestamp;     // Unix timestamp indicating when the command was generated
    private String action;      // Specific action to be taken (optional) (e.g., START, STOP, OPEN, CLOSE, etc.)
    private String status;      // The status or condition being reported or queried (optional)
    private String stationId;   // Unique identifier for stations (optional, used in specific messages)

    // Constructor
    public Command(String clientType, String message, String clientId, long timestamp, 
                   String action, String status, String stationId) {
        this.clientType = clientType;
        this.message = message;
        this.clientId = clientId;
        this.timestamp = timestamp;
        this.action = action;
        this.status = status;
        this.stationId = stationId;
    }

    public Command()
{
    this.clientType = clientType;
        this.message = "";
        this.clientId = "";
        this.timestamp = 8008;
        this.action = "";
        this.status = "";
        this.stationId = "";
}
    // Getters and Setters
    public String getClientType() {
        return clientType;
    }

    public void setClientType(String clientType) {
        this.clientType = clientType;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getClientId() {
        return clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getStationId() {
        return stationId;
    }

    public void setStationId(String stationId) {
        this.stationId = stationId;
    }

    // Override toString for easy printing
    @Override
    public String toString() {
        return "Command{" +
                "clientType='" + clientType + '\'' +
                ", message='" + message + '\'' +
                ", clientId='" + clientId + '\'' +
                ", timestamp=" + timestamp +
                ", action='" + action + '\'' +
                ", status='" + status + '\'' +
                ", stationId='" + stationId + '\'' +
                '}';
    }
}

