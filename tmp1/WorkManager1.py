import threading
import time

class WorkUnit:
    def __init__(self, function, args=None, kwargs=None, callback=None):
        self.function = function
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}
        self.callback = callback

    def execute(self):
        result = self.function(*self.args, **self.kwargs)
        if self.callback:
            self.callback(result)

class WorkManager:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def enqueue(self, work_unit):
        with self.condition:
            self.queue.append(work_unit)
            self.condition.notify()

    def dequeue(self):
        with self.condition:
            while not self.queue:
                self.condition.wait()
            return self.queue.pop(0)

def sample_task(data):
    print(f"Processing {data}")
    time.sleep(1)  # Simulate some work being done
    return f"Result of {data}"

def task_callback(result):
    print(f"Task completed with result: {result}")

def worker_thread(work_manager, thread_id):
    while True:
        work_unit = work_manager.dequeue()
        if work_unit is None:
            print(f"Worker thread {thread_id} shutting down.")
            break
        work_unit.execute()

def main():
    # Create a WorkManager instance
    work_manager = WorkManager()

    # Start worker threads
    num_workers = 3
    workers = []
    for i in range(num_workers):
        t = threading.Thread(target=worker_thread, args=(work_manager, i+1))
        t.start()
        workers.append(t)
        print(f"Worker thread {i+1} started.")

    # Enqueue some WorkUnits with kwargs example
    for i in range(10):
        data = f"data_{i}"
        work_unit = WorkUnit(
            function=sample_task,
            kwargs={'data': data},  # Using kwargs to pass arguments
            callback=task_callback
        )
        work_manager.enqueue(work_unit)
        print(f"Enqueued work unit with {data}")
        time.sleep(0.5)  # Simulate time between enqueuing tasks

    # Wait for all tasks to be processed
    while True:
        with work_manager.condition:
            if not work_manager.queue:
                break
        time.sleep(0.1)

    # Initiate shutdown
    print("Initiating shutdown.")
    work_manager.shutdown()

    # Wait for worker threads to finish
    for worker in workers:
        worker.join()
    print("All worker threads have been shut down.")

if __name__ == "__main__":
    main()

