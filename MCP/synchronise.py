#TO use: Instantiate synchronise object
#Update_sequences with a message
#use comparator to see whether the last message sent by the client 
#in the message's data was in the correct order

class synchronise:
    previous_message = []

    def __init__(self, message):  # takes message for greater flexibility
        self.cur = 0
        pending_add_clientID = message["client_id"]
        pending_add_current_sequence = int(message["sequence_number"])  # Cast to int for consistency
        exists = any(entry["client_id"] == pending_add_clientID for entry in self.previous_message)

        if not exists:
            self.previous_message.append({
                "client_id": pending_add_clientID,
                "current_sequence": pending_add_current_sequence,
                "previous_sequence": 0
            })
            self.cur += 1
        else:
            print(f"Client ID {pending_add_clientID} already exists in the previous_message list.")

    def update_sequences(self, message):
        try:
            pending_add_clientID = message["client_id"]
            pending_add_current_sequence = int(message["sequence_number"])  # Cast to int for consistency

            exists = any(entry["client_id"] == pending_add_clientID for entry in self.previous_message)
            if exists:
                index = next((i for i, entry in enumerate(self.previous_message) if entry["client_id"] == pending_add_clientID), None)
                
                pending_previous_message = self.previous_message[index]["current_sequence"]
                
                # Update the message
                self.previous_message[index] = {
                    "client_id": pending_add_clientID,
                    "current_sequence": pending_add_current_sequence,
                    "previous_sequence": pending_previous_message
                }
            else:
                print(f"Client ID {pending_add_clientID} not found. Adding to data structure.")
                self.previous_message.append({
                    "client_id": pending_add_clientID,
                    "current_sequence": pending_add_current_sequence,
                    "previous_sequence": 0
                })
                self.cur += 1

        except Exception as e:
            print(f"Unable to update message: {e}")

    # Function that compares messages
    def sequence_number_comparator(self, message):
        index = next((i for i, entry in enumerate(self.previous_message) if entry["client_id"] == message["client_id"]), None)
        if index is None:
            print(f"Client ID {message['client_id']} not found.")
            return

        thisEntry = self.previous_message[index]
        if int(thisEntry["current_sequence"]) == int(thisEntry["previous_sequence"]) + 1:
            print("yay!")
        else:
            print("oh no!")


if __name__ == "__main__":

    # Initialize synchroniser class
    synchroniser = synchronise({"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1000"})
    
    # Updating the same client with new sequences
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1001"})
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1002"})

    # Adding a new client and updating sequences
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1001"})
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1002"})

    # Compare sequences for a client
    synchroniser.sequence_number_comparator({"client_id": "BR02"})
    print(synchroniser.previous_message)

    synchroniser.sequence_number_comparator({"client_id": "BR02"})
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1001"})
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR02", "sequence_number": "1005"})
    synchroniser.sequence_number_comparator({"client_id": "BR02"})