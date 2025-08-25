import queue

class MessageBroker:
    def __init__(self):
        """Initializes a simple in-memory message queue."""
        self.message_queue = queue.Queue()
        print("Message Broker initialized.")

    def publish(self, agent_name, message):
        """An agent publishes a message to the queue."""
        full_message = {"sender": agent_name, "content": message}
        self.message_queue.put(full_message)
        print(f"Message Broker: Received message from {agent_name}.")

    def subscribe(self):
        """Retrieves the next message from the queue for a listening agent."""
        if not self.message_queue.empty():
            message = self.message_queue.get()
            print(f"Message Broker: Dispatching message -> {message['content']}")
            return message
        return None