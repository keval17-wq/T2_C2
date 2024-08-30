import java.util.HashMap;
import java.util.Map;

public class StateManager {
    private final Map<String, String> componentStates = new HashMap<>();

    public void updateState(String componentId, String state) {
        componentStates.put(componentId, state);
        Logger.log("Updated state of " + componentId + " to " + state);
    }

    public String getState(String componentId) {
        return componentStates.getOrDefault(componentId, "UNKNOWN");
    }
}