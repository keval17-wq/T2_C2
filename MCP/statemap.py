# experimental
from utils import create_socket, receive_message, send_message, log_event
import time

class brMap:
    # Class variable to hold track map
    track_map = {
        'block_1': {'station': 'ST01', 'next_block': 'block_2', 'turn': False, 'led': 'LED01', 'isOccupied': False, 'occupiedBy': None},
        'block_2': {'station': 'ST02', 'next_block': 'block_3', 'turn': False, 'led': 'LED02', 'is_checkpoint': True, 'isOccupied': False, 'occupiedBy': None},
        'block_3': {'station': 'ST03', 'next_block': 'block_4', 'turn': True, 'led': 'LED03', 'turn_severity': 0.5, 'isOccupied': False, 'occupiedBy': None},
        'block_4': {'station': 'ST04', 'next_block': 'block_5', 'turn': False, 'led': 'LED04', 'is_checkpoint': True, 'isOccupied': False, 'occupiedBy': None},
        'block_5': {'station': 'ST05', 'next_block': 'block_6', 'turn': False, 'led': 'LED05', 'isOccupied': False, 'occupiedBy': None},
        'block_6': {'station': 'ST06', 'next_block': 'block_7', 'turn': True, 'led': 'LED06', 'turn_severity': 0.7, 'is_checkpoint': True, 'isOccupied': False, 'occupiedBy': None},
        'block_7': {'station': 'ST07', 'next_block': 'block_8', 'turn': False, 'led': 'LED07', 'isOccupied': False, 'occupiedBy': None},
        'block_8': {'station': 'ST08', 'next_block': 'block_9', 'turn': False, 'led': 'LED08', 'is_checkpoint': True, 'isOccupied': False, 'occupiedBy': None},
        'block_9': {'station': 'ST09', 'next_block': 'block_10', 'turn': False, 'led': 'LED09', 'isOccupied': False, 'occupiedBy': None},
        'block_10': {'station': 'ST10', 'next_block': 'block_1', 'turn': False, 'led': 'LED10', 'isOccupied': False, 'occupiedBy': None}
    }

    # Class variable to hold ports
    ccp_ports = {
        'BR01': ('127.0.0.1', 2002),
        'BR02': ('127.0.0.1', 2003),
        'BR03': ('127.0.0.1', 2004),
        'BR04': ('127.0.0.1', 2005),
        'BR05': ('127.0.0.1', 2006)
    }

    # Takes item in track_map (block_XX), returns next block
    @classmethod
    def getNextBlock(cls, block):
        try:
            if block == "block_10":
                return cls.track_map['block_1']  # Loop around for block_10 to block_1
            elif block.startswith('block_'):
                # Split the block name to get the number part
                splitString = block.split("_", 1)
                block_num = int(splitString[1])  # Convert the block number to an integer
                next_block_num = block_num + 1  # Increment to the next block number
                
                # Construct the key for the next block
                next_block_key = f"block_{next_block_num}"
                return cls.track_map[next_block_key]  # Return the next block from the dictionary
        except KeyError:
            print(f"getNext call failed: {block} is not in track_map list of blocks")
            return None
    
    # Takes block name and BR, updates the occupancy and returns true if success, false otherwise
    @classmethod
    def updateOccupancy(cls, block, br):
        try:
            if block in cls.track_map and br in cls.ccp_ports:
                cls.track_map[block]['isOccupied'] = True
                cls.track_map[block]['occupiedBy'] = br
                return True
        except:
            print(f"{block} or {br} are not valid inputs")
            return False
    
    # Helper method to get block that is being occupied by BR currently
    @classmethod
    def getBladeRunnerOccupancy(cls, br):
        if br in cls.ccp_ports:
            for block, data in cls.track_map.items():
                if data.get('occupiedBy') == br:
                    return block
        return None
    
    
    
    

    


    
    
    

        



