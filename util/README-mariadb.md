The `audit: PROCTITLE` message you're seeing, such as:

```
audit: PROCTITLE proctitle="/usr/sbin/mariadbd"
```

is part of the audit subsystem (`auditd`) logging process information. This specific message is logging the **process title** of a program that triggered an audit event. Here's what each part means:

### Breakdown of the Message:

- **audit**: Indicates that this message is generated by the `auditd` subsystem, which logs various system events, including security-related actions.

- **PROCTITLE**: This indicates that the audit log is capturing the **process title**. The process title refers to the actual command and arguments used to invoke the process.

- **proctitle="/usr/sbin/mariadbd"**: This is the full path and command used to start the **MariaDB daemon (`mariadbd`)**. This means that the `mariadbd` process (MariaDB server) triggered an audit event, and the log is capturing the exact command that was executed to launch it.

### Why is This Being Logged?

The `PROCTITLE` field is included in audit logs to capture the **full command line** used to execute the process. This is useful for:

1. **Security Monitoring**: It helps administrators and security teams track which processes are running, how they were invoked, and what arguments were passed to them. This can be crucial for tracking malicious activity or investigating incidents.
  
2. **Compliance**: Many compliance frameworks (such as PCI-DSS or HIPAA) require auditing of process executions to detect unauthorized actions or process starts.

3. **Audit Rules**: It's possible that you have an audit rule that logs specific events related to the MariaDB process, or `auditd` may be set to log all process execution events.

For example, if you have an audit rule for process execution (such as `execve`), you will see `PROCTITLE` messages in the audit logs for each process that is started.

### Viewing Related Audit Events

If you'd like to view related audit events, you can use `ausearch` to search for events related to `mariadbd` or other processes:

```bash
sudo ausearch -sc execve | grep mariadbd
```

This will show audit events related to the `execve` system call, which is responsible for starting new processes, including `mariadbd`.

### Disabling Specific Audit Rules (If Not Needed)

If these messages are not relevant for your use case, and you want to reduce the audit noise, you can review your audit rules to see if specific rules are triggering this logging. Audit rules can be listed with:

```bash
sudo auditctl -l
```

If there are specific rules capturing `execve` calls or process starts for `mariadbd`, you can remove or adjust them as needed.

For example, to stop logging process executions, you could remove any rules related to `execve`:

```bash
sudo auditctl -d always,exit -F arch=b64 -S execve
```

But remember that disabling such audit rules may reduce the level of security monitoring.

In summary, the `PROCTITLE` message you're seeing is logged by `auditd` to track the execution of the MariaDB server (`mariadbd`). This is normal behavior for audit logging, especially if you're monitoring system processes or complying with security policies.