Catching `fork` and `exec` system calls with `auditd` can be very useful for tracking process creation and command execution. Here's how you can do it:

### 1. **Install and Configure Auditd**
Ensure that the `auditd` service is installed and running on your system.

```bash
sudo apt install auditd
sudo systemctl start auditd
sudo systemctl enable auditd
```

### 2. **Define Audit Rules for fork/exec**

You can create custom rules in `auditd` to monitor `fork` and `execve` system calls. These rules are typically stored in `/etc/audit/rules.d/`.

#### Monitoring `fork` and `vfork`
`fork` and `vfork` are system calls responsible for creating processes.

```bash
sudo auditctl -a always,exit -F arch=b64 -S fork -S vfork -k process_creation
```

#### Monitoring `execve`
The `execve` system call is used to execute programs. You can audit it like this:

```bash
sudo auditctl -a always,exit -F arch=b64 -S execve -k exec_events
```

- `-a always,exit`: This adds a rule to audit on every exit of the specified system call.
- `-F arch=b64`: This filters for 64-bit architecture (you can also use `arch=b32` for 32-bit).
- `-S`: This specifies the system call (`fork`, `vfork`, `execve`).
- `-k`: This is the key you can use to search for specific events in the audit logs.

### 3. **Make the Rules Persistent**
To make these rules persist across reboots, add them to the `/etc/audit/rules.d/audit.rules` file:

```bash
-w /usr/bin/fork -p x -k process_creation
-w /usr/bin/vfork -p x -k process_creation
-w /usr/bin/execve -p x -k exec_events
```

### 4. **Check Audit Logs**
Audit logs can be checked using `ausearch` or `auditctl`:

- Search for `execve` calls:

```bash
sudo ausearch -k exec_events
```

- Search for `fork` and `vfork` events:

```bash
sudo ausearch -k process_creation
```

### 5. **Restart auditd**
After making changes to the audit rules, restart the `auditd` service:

```bash
sudo systemctl restart auditd
```

With this setup, you will be able to monitor and log every `fork` and `execve` system call, capturing process creation and command execution events.
