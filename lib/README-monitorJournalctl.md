# monitorJournalctl.py

This Python script provides functionality to monitor and manage systemd journal logs in real-time using the `journalctl` command. It defines a class `MonitorJournalctl` which allows starting, reading, and stopping the monitoring of these logs.

## Features

- **Start Monitoring**: This feature uses the `journalctl` command to follow and display log messages in real-time.
- **Retrieve Log Records**: Fetches the next available log entry from the journal.
- **Stop Monitoring**: Ensures that the journal monitoring process is terminated gracefully or forcefully if needed.

## Class and Methods

### `MonitorJournalctl`

#### `__init__(self)`

The constructor initializes the `MonitorJournalctl` instance and sets the `self.process` attribute to `None`.

#### `start_monitoring(self)`

Starts a subprocess that runs `journalctl -f` to fetch logs in real-time. It attempts to start the subprocess and handles exceptions if the process fails to start.

**Usage:**

```python
monitor = MonitorJournalctl()
monitor.start_monitoring()
```

#### `get_next_record(self)`

Reads and returns the next log entry from the subprocess's standard output. It raises a `RuntimeError` if called before `start_monitoring()`.

**Usage:**

```python
record = monitor.get_next_record()
print(record)
```

#### `stop_monitoring(self)`

Stops the monitoring by terminating the `journalctl` subprocess. It sends a `SIGTERM` signal initially and falls back to `SIGKILL` if the process does not terminate within a specified timeout.

**Usage:**

```python
monitor.stop_monitoring()
```

### Example Usage

An example usage of the `MonitorJournalctl` class is provided with this script. It demonstrates starting the monitor, fetching five log entries, and then stopping the monitor.

```python
if __name__ == "__main__":
    monitor = MonitorJournalctl()
    monitor.start_monitoring()

    # Fetch and print 5 log records
    for _ in range(5):
        record = monitor.get_next_record()
        print(f"Log: {record}")

    monitor.stop_monitoring()
```

## Requirements

- The script must be run with permissions that allow executing `sudo journalctl`, typically requiring `sudo` access.
- Python 3.x
- A system with systemd and journalctl installed.

## Error Handling

- Errors during the subprocess start, log reading, or stopping processes are caught and printed to the standard output.
- If `get_next_record` is called without starting the monitoring, a `RuntimeError` is raised.

This script provides a simple interface for monitoring system logs, which can be extended or integrated into larger system management solutions.

