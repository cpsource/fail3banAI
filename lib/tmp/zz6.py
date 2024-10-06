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
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)  # guards self.queue
        self.shutdown_flag = False

    def enqueue(self, message_string):
        with self.condition:
            work_unit = MessageWorkUnit(message_string)
            self.queue.append(work_unit)
            self.condition.notify()

    def dequeue(self):
        with self.condition:
            while not self.queue and not self.shutdown_flag:
                self.condition.wait()
            if self.shutdown_flag and not self.queue:
                return None
            return self.queue.pop(0)

    def is_enqueued(self):
        with self.condition:
            return len(self.queue)

    def shutdown(self):
        with self.condition:
            self.shutdown_flag = True
            self.condition.notify_all()

# Test the MessageManager class
if __name__ == "__main__":
    # Create a message manager instance
    manager = MessageManager()

    # Enqueue some messages
    manager.enqueue("Message 1")
    manager.enqueue("Message 2")

    # Check how many messages are enqueued
    print("Messages enqueued:", manager.is_enqueued())  # Output: 2

    # Dequeue and execute messages
    work_unit = manager.dequeue()
    if work_unit:
        work_unit.execute()
        print(f"Dequeued message: {work_unit.get_message_string()}")

    # Check enqueued messages again
    print("Messages enqueued:", manager.is_enqueued())  # Output: 1

    # Dequeue and execute another message
    work_unit = manager.dequeue()
    if work_unit:
        work_unit.execute()
        print(f"Dequeued message: {work_unit.get_message_string()}")

    # Check enqueued messages again (should be 0 now)
    print("Messages enqueued:", manager.is_enqueued())  # Output: 0

