import threading

class MessageWorkUnit:
    def __init__(self, message_string):
        self.message_string = message_string
        
    def execute(self):
        # Stub for later expansion, currently prints the message
        print(f"Executing message: {self.message_string}")
    
    def get_message_string(self):
        # Returns the message string in a controlled way
        return self.message_string

class MessageManager:
    def __init__(self, queues=("Default",)):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)  # guards self.queues
        self.shutdown_flag = False
        self.queues = {queue: [] for queue in queues}

        # Ensure "Default" queue is present
        if "Default" not in self.queues:
            self.queues["Default"] = []

    def enqueue(self, message_string, message_queue="Default"):
        with self.condition:
            # Check if the queue exists, if not create it
            if message_queue not in self.queues:
                self.queues[message_queue] = []
            
            work_unit = MessageWorkUnit(message_string)
            self.queues[message_queue].append(work_unit)
            self.condition.notify()

    def dequeue(self, message_queue="Default"):
        with self.condition:
            while not self.queues[message_queue] and not self.shutdown_flag:
                self.condition.wait()

            if self.shutdown_flag and not self.queues[message_queue]:
                return None

            return self.queues[message_queue].pop(0)

    def is_enqueued(self, message_queue="Default"):
        with self.condition:
            return len(self.queues[message_queue])

    def shutdown(self):
        with self.condition:
            self.shutdown_flag = True
            self.condition.notify_all()

# Test the MessageManager class with multiple queues
if __name__ == "__main__":
    # Create a message manager instance with custom queues
    manager = MessageManager(queues=("Default", "HighPriority", "LowPriority"))

    # Enqueue some messages to different queues
    manager.enqueue("Message 1", message_queue="Default")
    manager.enqueue("Urgent Task", message_queue="HighPriority")
    manager.enqueue("Background Job", message_queue="LowPriority")

    # Dequeue and process messages from "HighPriority"
    work_unit = manager.dequeue(message_queue="HighPriority")
    if work_unit:
        work_unit.execute()
        print(f"Dequeued message: {work_unit.get_message_string()} from HighPriority")

    # Dequeue and process messages from "Default"
    work_unit = manager.dequeue(message_queue="Default")
    if work_unit:
        work_unit.execute()
        print(f"Dequeued message: {work_unit.get_message_string()} from Default")

    # Check if there are messages in "LowPriority"
    print("Messages enqueued in LowPriority:", manager.is_enqueued(message_queue="LowPriority"))

    # Dequeue and process messages from "LowPriority"
    work_unit = manager.dequeue(message_queue="LowPriority")
    if work_unit:
        work_unit.execute()
        print(f"Dequeued message: {work_unit.get_message_string()} from LowPriority")

    # Simulate shutdown
    manager.shutdown()

