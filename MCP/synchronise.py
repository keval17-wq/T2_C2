class synchronise:
    previous_message = []

    def __init__(self, message):  # takes message for greater flexibility
        self.cur = 0
        pending_add_clientID = message["client_id"]
        pending_add_current_sequence = int(message["sequence_number"])  # Cast to int for consistency
        exists = any(entry["client_id"] == pending_add_clientID for entry in self.previous_message)

        if not exists:
            self.previous_message.insert(self.cur, {
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
                print(f"Client ID {pending_add_clientID} not found.")
        except Exception as e:
            print(f"Unable to update message: {e}")

if __name__ == "__main__":
    synchroniser = synchronise({"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1000"})
    synchroniser.update_sequences({"client_type": "CCP", "message": "CCIN", "client_id": "BR01", "sequence_number": "1001"})
    print(synchroniser.previous_message)
