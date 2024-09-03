# T2_C2
## Server code for MCP

### Calibration
Whenever the BR is put on the track, it will be a part of the calibration where it will run and hit the first station so we will know what station it is at currently. 
Second, when the BR connects, the second BR02 will get on the track and will receive the acknowledgment along with the start mechanism, which will end at the next station as well, as all the IR will be on until all the BRs have been put on the track. 
Until we get all the BRs and their station location, we will not start the session, meaning the actual trains start to move all at once. This is just the station calibration phase.

## MCP Server Features, Capabilities, and Progress
This document outlines the features and capabilities of the Master Control Program (MCP) server for the Blade Runner project. The capabilities are organized into 'Working', 'Ongoing', and 'Not Implemented' sections based on their current state. Each feature includes a percentage of completion, what has been done, what remains, and reasons if not fully implemented.

### 1. Working Features

#### MCP can manage connections (100%)
- **Status**: The MCP can handle multiple incoming connections from CCPs, stations, and LED controllers. It listens for these connections on a designated UDP port (2001).

#### MCP can log events and statuses (100%)
- **Status**: The MCP can log all significant events, including connection statuses, command executions, and error reports, for monitoring and debugging purposes.

### 2. Ongoing Features

#### MCP can initiate communication (50%)
- **What’s Done**: The MCP can send basic initialization acknowledgments to CCPs.
- **What’s Missing**: The MCP needs to handle full initialization sequences for stations and LED controllers, including error handling or confirmation mechanisms. Reinitialization in case of communication failures also needs to be managed.

#### MCP can track Blade Runner positions (40%)
- **What’s Done**: The MCP can receive and log status updates from CCPs that include positional data.
- **What’s Missing**: The MCP needs to actively maintain a real-time map of the track, update Blade Runner positions dynamically, and prevent potential collisions using this data. Integration with block occupancy management is also required.

#### MCP can manage Blade Runner speed (30%)
- **What’s Done**: The MCP has a basic framework for sending speed-related commands (e.g., SLOW, FAST) to CCPs.
- **What’s Missing**: The MCP needs advanced logic to adjust speed based on track conditions, such as approaching stations or curves. The system should also handle speed transitions smoothly and integrate with collision prevention.

#### MCP can receive and process status updates (40%)
- **What’s Done**: The MCP can log status updates from CCPs, stations, and LED controllers.
- **What’s Missing**: The MCP needs to implement advanced processing of these updates, such as triggering specific actions based on statuses (e.g., stopping a Blade Runner if a station is occupied). It also needs to detect anomalies in status reports and respond appropriately.

### 3. Not Implemented Features

#### MCP can prevent collisions (0%)
- **Status**: The MCP can manage block occupancy by ensuring that no two Blade Runners occupy the same block at the same time. It can send stop commands to CCPs if a potential collision is detected.
- **Reason**: The logic for managing block occupancy and detecting potential collisions has not yet been developed. This involves creating and maintaining a real-time map of block usage and implementing conditional logic to issue stop commands when necessary.

#### MCP can coordinate stopping at stations (0%)
- **Status**: The MCP can coordinate the stopping of Blade Runners at stations by processing line break sensor data and sending commands to CCPs to slow down Blade Runners to station speed.
- **Reason**: The integration of line break sensors and the associated logic to slow down Blade Runners at the right moment is still under development. The MCP needs to be able to interpret sensor data and send timely stop commands to CCPs.

#### MCP can control doors at stations and Blade Runners (0%)
- **Status**: The MCP can send commands to CCPs and stations to open or close doors, ensuring synchronized passenger ingress and egress.
- **Reason**: The functionality for door control, including sending open/close commands and ensuring synchronization between stations and Blade Runners, is not yet implemented. This will require the development of command sequences and confirmation mechanisms.

#### MCP can control IR and regular LEDs (0%)
- **Status**: The MCP can manage the state of IR LEDs and regular LEDs at checkpoints and stations, signaling when blocks are occupied and when a Blade Runner should stop.
- **Reason**: The development of the LED control logic is pending. This involves sending on/off commands to LED controllers and ensuring the LEDs' states are accurately reflected in the system's operational logic.

#### MCP can handle errors and reconnections (0%)
- **Status**: The MCP can detect connection losses with any CCP, station, or LED controller. It can attempt to reconnect with the lost connection and issue emergency stop commands if reconnection fails.
- **Reason**: Error handling and reconnection logic are not yet implemented. This will require the MCP to monitor connection statuses actively, attempt to re-establish lost connections, and issue emergency commands if reconnection is not successful.

#### MCP can initiate system-wide actions (0%)
- **Status**: The MCP can initiate system-wide actions such as emergency stops for all Blade Runners or resetting LED states, based on the current operational needs and any detected issues.
- **Reason**: The capability to initiate system-wide actions is not yet in place. This will involve creating a centralized control mechanism within the MCP that can override all components in case of an emergency or system failure.

## Enhanced Version

### 1. Handle Full Init
- **Action Items**:
  - Develop initialization sequences for stations.
  - Implement initialization for LED controllers.
  - Include error handling if communication fails during initialization.
  - Implement retry mechanisms for failed initializations.

### 2. Track Mapping
- **Action Items**:
  - Implement dynamic tracking of Blade Runner positions.
  - Develop and maintain a real-time map of the track.
  - Integrate block occupancy information into the map.
  - Update the map based on status reports from CCPs and sensors.

### 3. Speed Control Logic
- **Action Items**:
  - Refine the speed control commands (SLOW, FAST, STOP) for Blade Runners.
  - Implement smooth speed transitions based on track conditions.
  - Add logic for speed adjustments when approaching stations or curves.
  - Test and validate the speed control under different scenarios.

### 4. Advanced Status Processing
- **Action Items**:
  - Implement logic to trigger actions based on status updates from CCPs and stations.
  - Develop conditions for actions like stopping Blade Runners at occupied stations.
  - Test the status processing with various edge cases (e.g., unexpected stops, sensor failures).
  - Implement logging and alerts for critical status changes.

### 5. Error Handling & Reconnection
- **Action Items**:
  - Develop error detection mechanisms for lost connections.
  - Implement logging for connection failures.
  - Create reconnection logic that retries connections after a failure.
  - Develop emergency stop commands in case reconnection fails.

### 6. System-wide Actions
- **Action Items**:
  - Develop the ability to issue emergency stop commands across all CCPs.
  - Implement commands for resetting all LED states.
  - Test system-wide commands to ensure they override individual commands as needed.
  - Create a centralized control mechanism within the MCP for issuing these commands.

### 7. Collision Prevention
- **Action Items**:
  - Implement block occupancy logic to prevent multiple Blade Runners from entering the same block.
  - Develop stop commands based on block occupancy status.
  - Test the collision prevention system under different operational conditions.
  - Integrate collision prevention with the dynamic track map.

### 8. Door Control Logic
- **Action Items**:
  - Develop commands for opening and closing doors at stations and on Blade Runners.
  - Ensure synchronization between station doors and Blade Runner doors.
  - Implement logic for handling doors in case of system errors.
  - Test the door control logic in various scenarios, including emergencies.

### 9. LED Control Logic
- **Action Items**:
  - Develop control logic for turning IR and regular LEDs on and off at checkpoints and stations.
  - Ensure the LED states are accurately reflected in the MCP's operational logic.
  - Test LED controls under different conditions, such as block occupancy and station stops.
  - Implement a fallback mechanism in case of LED control failures.
