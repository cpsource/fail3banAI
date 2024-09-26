import threading
import time
import sys
import logging

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
            
    def show(self):
        print(f"WorkUnit: function = {function}")
        if callback is not None:
            print(f"WorkUnit: callback = {callback}")
        if kwargs is not None:
            for key, value in kwargs.items():
                print(f"{key} = {value}")
        
class WorkManager:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.shutdown_flag = False

    def enqueue(self, work_unit):
        with self.condition:
            self.queue.append(work_unit)
            self.condition.notify()

    def dequeue(self):
        with self.condition:
            while not self.queue and not self.shutdown_flag:
                self.condition.wait()
            if self.shutdown_flag and not self.queue:
                return None
            return self.queue.pop(0)

    def shutdown(self):
        with self.condition:
            self.shutdown_flag = True
            self.condition.notify_all()

            
class WorkController:
    def __init__(self, num_workers=3):
        # Create a named logger consistent with the log file name
        self.logger = logging.getLogger("fail3ban")
        # Create a WorkManager instance
        self.work_manager = WorkManager()
        # Start worker threads
        self.workers = []
        for i in range(num_workers):
            t = threading.Thread(target=self.worker_thread, args=(self.work_manager,i+1))
            t.start()
            self.workers.append(t)
            self.logger.debug(f"Worker thread {i+1} started.")

    def worker_thread(self, work_manager, thread_id):
        print(f"Worker thread {thread_id} starting. Checking work queue.")
        while True:
            work_unit = work_manager.dequeue()
            if work_unit is None:
                self.logger.debug(f"Worker thread {thread_id} shutting down.")
                break
            work_unit.execute()
            
    def enqueue(self, work_unit):
        self.work_manager.enqueue(work_unit)
        self.logger.debug(f"Enqueued work")

    def wait_for_all_tasks_to_complete(self):
        # Wait for all tasks to be processed
        while True:
            with self.work_manager.condition:
                if not self.work_manager.queue:
                    break
                time.sleep(0.1)

    def initiate_shutdown(self):
        # Initiate shutdown
        self.logger.debug("Initiating shutdown.")
        self.work_manager.shutdown()

    def wait_for_worker_threads_to_finish(self):
        # Wait for worker threads to finish
        for worker in self.workers:
            worker.join()
        self.logger.debug("All worker threads have been shut down.")

# used for debugging        
def task_callback(result):
    print(f"Task completed with result: {result}")

# used for debugging
def sample_task(data):
    print(f"Processing {data}")
    time.sleep(1)  # Simulate some work being done
    return f"Result of {data}"

def main():
    # Create work controller
    wc = WorkController()

    # Enqueue some WorkUnits with kwargs example
    for i in range(10):
        data = f"data_{i}"
        wc.enqueue(sample_task, data, task_callback)
        print(f"Enqueued work unit with {data}")
        time.sleep(0.5)  # Simulate time between enqueuing tasks

    # Wait for all tasks to be processed
    wc.wait_for_all_tasks_to_complete()

    # Initiate shutdown
    wc.initiate_shutdown()

    # Wait for worker threads to finish
    wc.wait_for_worker_threads_to_finish()

if __name__ == "__main__":
    main()
