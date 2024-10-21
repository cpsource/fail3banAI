
u can control how much **auditd**'s logs end up in **journalctl** by configuring **auditd** itself and adjusting the logging policies in **systemd** and **rsyslog** (if applicable). Here are the steps to fine-tune how **auditd** interacts with **journalctl**:

### 1. **Control Logging via auditd Configuration:**

The **auditd** service controls what kind of audit logs are generated. The **auditd** logs can end up in `journalctl` depending on how it's configured to write to the system logs.

#### Modify the `/etc/audit/auditd.conf` file:
This file contains the configuration for **auditd** logging. To control how much is logged to **syslog** (which journalctl collects):

- **`log_format = RAW`**: (Default) Logs in the native audit format, which is more detailed.
- **`log_format = ENRICHED`**: Adds more human-readable context.
- **`log_format = NOLOG`**: Disables logging of audit logs to syslog entirely, meaning they will not show up in `journalctl`.

You can also control how **auditd** handles syslog with:

```bash
# Enable or disable sending audit logs to syslog (and thus journalctl).
write_logs = yes
log_format = RAW

# To disable sending audit logs to syslog entirely (prevents logs from showing up in journalctl):
write_logs = no
```

After making changes to `/etc/audit/auditd.conf`, restart the **auditd** service:

```bash
sudo service auditd restart
```

### 2. **Control Logs via systemd Configuration:**

Since **auditd** logs can end up in `journalctl` via **systemd**, you can manage **systemd** logging behavior by adjusting the **`systemd-journald`** configuration.

#### Modify `/etc/systemd/journald.conf`:
You can tweak how system logs are handled by editing the `journald.conf` file. Some useful options include:

- **`Storage=`**: Controls where journal logs are stored. You can set it to `volatile` (stored only in memory) or `persistent` (stored on disk).
- **`MaxRetentionSec=`**: Limits how long logs are kept.
- **`MaxLevelStore=`**: Controls the highest priority log level that will be stored (e.g., `info`, `warning`, `debug`).

Example:

```bash
[Journal]
Storage=persistent
MaxLevelStore=warning
```

This configuration would store only messages with a log level of `warning` or higher in the journal.

After modifying `journald.conf`, restart the **systemd-journald** service to apply the changes:

```bash
sudo systemctl restart systemd-journald
```

### 3. **Control Logs via rsyslog Configuration (Optional)**:

If you're using **rsyslog** to forward logs from **auditd** to the journal (which may be the case in some configurations), you can limit what is forwarded.

#### Modify `/etc/rsyslog.conf` or `/etc/rsyslog.d/*.conf`:
Adjust the logging rules to control what logs are sent to the system journal.

For example, you can prevent **auditd** logs from being sent to syslog (and thus journalctl) with a filter like this:

```bash
:programname, isequal, "auditd" stop
```

This tells **rsyslog** to stop processing logs from **auditd**, which prevents them from being forwarded to the journal.

After editing the configuration, restart **rsyslog**:

```bash
sudo service rsyslog restart
```

### 4. **Limit Audit Logs in Journalctl by Level:**

If you want to reduce the volume of **auditd** logs specifically in `journalctl`, you can use filtering options when querying the logs, for example:

```bash
journalctl -p warning -u auditd
```

This shows only **auditd** logs at the `warning` level or higher.

### Summary:
- Control **auditd** log formatting and behavior by editing `/etc/audit/auditd.conf`. Use `write_logs = no` to prevent **auditd** logs from going to syslog (and thus `journalctl`).
- Adjust **systemd-journald** logging behavior by editing `/etc/systemd/journald.conf`.
- Optionally adjust **rsyslog** if it's used to forward **auditd** logs.
- Use `journalctl`'s filtering options to query logs by priority level.

By combining these methods, you can control how much **auditd** logging ends up in **journalctl** and manage the volume of logs effectively.
