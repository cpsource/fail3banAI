
# How to Lock Changes to iptables in Ubuntu

**Question:**  
Is there any way through Ubuntu I can lock changes to iptables?

## Answer:

Yes, on Ubuntu (and other Linux distributions), you can "lock" changes to `iptables` to prevent unintended or unauthorized modifications. Here are a few methods you can use to protect the `iptables` rules:

### 1. **Make the `iptables` Command Read-Only for Non-Root Users**
Only users with root privileges can modify `iptables`, so ensuring proper permission management is crucial. 

### Steps:
- Ensure that only `root` can access the `iptables` command.
- If you're concerned about unauthorized changes from users with sudo access, you can limit the ability of certain users to run `iptables` commands via `sudo` by editing the `/etc/sudoers` file.

### 2. **Use `iptables-persistent` to Restore Rules on Boot**
You can make `iptables` rules persistent across reboots using `iptables-persistent`. This way, even if someone changes the `iptables` rules temporarily, they will revert to the saved version on the next reboot.

### Steps to Set Up `iptables-persistent`:
1. **Install `iptables-persistent`**:
   ```bash
   sudo apt-get install iptables-persistent
   ```

2. **Save the Current Rules**:
   ```bash
   sudo netfilter-persistent save
   ```

3. **Check the saved rules** in `/etc/iptables/rules.v4` (for IPv4) or `/etc/iptables/rules.v6` (for IPv6).

4. On reboot, the system will restore the saved rules automatically.

### 3. **Restrict Sudo Permissions for `iptables`**
You can restrict access to `iptables` for specific users or groups using the `/etc/sudoers` file.

#### Example to Deny `iptables` Use for Specific Users:

1. **Edit the sudoers file**:
   ```bash
   sudo visudo
   ```

2. **Deny access to `iptables` for specific users**:
   You can specify that a particular user or group cannot run the `iptables` command, even with `sudo`.
   
   For example, to block user `john` from running `iptables` commands:
   ```
   john ALL=(ALL) !/sbin/iptables
   ```

   This prevents `john` from running any `iptables` command using `sudo`.

### 4. **Make `iptables` Configuration Files Immutable**
To prevent changes to the `iptables` rule files themselves, you can make the configuration files immutable using the `chattr` command. This will prevent any user, including `root`, from modifying the files unless the immutable attribute is removed.

#### Steps:
1. **Make the `iptables` rule file immutable**:
   ```bash
   sudo chattr +i /etc/iptables/rules.v4
   sudo chattr +i /etc/iptables/rules.v6
   ```

2. **Remove immutability when needed** (if you ever need to modify the rules):
   ```bash
   sudo chattr -i /etc/iptables/rules.v4
   sudo chattr -i /etc/iptables/rules.v6
   ```

### 5. **Use `ufw` (Uncomplicated Firewall) for Easier Management**
If you want a higher-level interface to manage `iptables` rules, you can use `ufw` (Uncomplicated Firewall). Once `ufw` is configured, it manages the `iptables` rules for you, and manual changes to `iptables` will not persist if made directly.

#### Steps:
1. **Install and enable `ufw`**:
   ```bash
   sudo apt-get install ufw
   sudo ufw enable
   ```

2. **Configure firewall rules using `ufw` commands** rather than modifying `iptables` directly.

   Example to allow SSH:
   ```bash
   sudo ufw allow ssh
   ```

3. **Block changes to `ufw` using sudoers restrictions**, similar to how you'd restrict access to `iptables`.

### 6. **Use `auditd` to Monitor and Log Changes to `iptables`**
If you can't fully lock `iptables` but want to monitor changes, you can use the `auditd` (Linux Auditing System) to track any modifications to `iptables`.

#### Steps:
1. **Install `auditd`**:
   ```bash
   sudo apt-get install auditd
   ```

2. **Add a rule to monitor `iptables` changes**:
   Edit `/etc/audit/audit.rules` and add the following lines to track any usage of the `iptables` command:
   ```bash
   -a always,exit -F arch=b64 -S execve -F exe=/sbin/iptables -k iptables_changes
   ```

3. **Restart `auditd`**:
   ```bash
   sudo systemctl restart auditd
   ```

4. You can now track `iptables` command usage by viewing the logs:
   ```bash
   ausearch -k iptables_changes
   ```

### Summary:
- **Read-Only for Non-Root Users**: Ensure only root or trusted users have access to modify `iptables`.
- **Make Rules Persistent**: Use `iptables-persistent` to save and restore rules automatically on boot.
- **Restrict sudo permissions**: Use `/etc/sudoers` to block specific users or groups from using `iptables`.
- **Immutable Configuration**: Use `chattr +i` to make rule files immutable, preventing any changes unless explicitly allowed.
- **Monitor with `auditd`**: Track any modifications to `iptables` using the Linux auditing system.

By using one or a combination of these techniques, you can lock down your `iptables` setup and ensure that any changes made (either intentional or accidental) are reverted or prevented.

Let me know if you need further assistance or details!
