import time
import os
import sys

class Checkpoint:
    def __init__(self, file_path='checkpoint.ctl'):
        #print("Checkpoint.__init__, {file_path}")
        self.file_path = file_path
        self.last_write_time = None
        self.cached_datestr = None
        
    def get(self):
        #print("Checkpoint.get()")
        """Returns the date string from the checkpoint.ctl file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                datestr = f.read().strip()
                return datestr
        else:
            return None
    
    def set(self, datestr):
        #print(f"Checkpoint.set({datestr})")
        """Sets the date string to the file, with caching logic to delay writing."""
        current_time = time.time()

        # If it's been less than 15 seconds since the last write, cache the data
        if self.last_write_time is None:
            self.write_to_file(datestr)
            self.last_write_time = current_time
        else:
            if self.last_write_time and (current_time - self.last_write_time) < 15:
                self.cached_datestr = datestr
            else:
                self.write_to_file(datestr)
                self.last_write_time = current_time
                self.cached_datestr = None  # Reset cache
        
    def write_to_file(self, datestr):
        """Writes the date string to the checkpoint file."""
        with open(self.file_path, 'w') as f:
            f.write(datestr+"\n")
    
    def flush_cache(self):
        """If there is cached data and more than 15 seconds have passed, write the cached data."""
        if self.cached_datestr and (time.time() - self.last_write_time) >= 15:
            self.write_to_file(self.cached_datestr)
            self.cached_datestr = None
            self.last_write_time = time.time()

# Example usage:
if __name__ == "__main__":
    checkpoint = Checkpoint()

    # Get the date string from the file
    date_str = checkpoint.get()
    print(f"Current checkpoint date: {date_str}")

    # Set a new date string
    checkpoint.set("2024-09-27 12:45:00")

    # Simulate waiting to flush cache
    time.sleep(16)
    checkpoint.flush_cache()

    # Display
    print(f"Cached Time: {checkpoint.get()}")
    
