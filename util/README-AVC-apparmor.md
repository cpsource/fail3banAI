The messages you're seeing in `journalctl -f` are related to AppArmor, specifically indicating that an operation was denied based on AppArmor profiles. These messages are being logged by `auditd` and are related to the `snapd` service.

If you'd like to stop these specific messages from appearing in `journalctl`, you have a few options:

### 1. **Suppress AppArmor Messages in auditd Configuration**

You can configure `auditd` to stop logging specific messages related to AppArmor. This involves adding a rule to ignore these events.

1. Open or create the `/etc/audit/rules.d/audit.rules` file:

   ```bash
   sudo nano /etc/audit/rules.d/audit.rules
   ```

2. Add a rule to ignore messages from AppArmor:

   ```bash
   -a never,exit -F subj_type=apparmor
   ```

3. Restart `auditd` to apply the changes:

   ```bash
   sudo systemctl restart auditd
   ```

This will prevent AppArmor messages from being sent to `auditd`, and as a result, they will not show up in `journalctl`.

### 2. **Disable Logging for Specific Snap Profile**

The issue might be related to the `snapd` AppArmor profile. If you are comfortable with changing AppArmor profiles, you could modify the `snapd` profile to allow the denied operation or adjust the profile settings to be less restrictive. However, this approach is more complex and could affect the security of your system.

1. Locate the AppArmor profile for the snap (in this case, `snap-confine`):
   ```bash
   sudo aa-status
   ```

2. Modify or update the AppArmor profile to stop logging or to allow the specific capability (`perfmon` in this case). For example, adding a capability line in the profile might prevent the logging, but this could lower security.

3. Reload the AppArmor profile:
   ```bash
   sudo systemctl reload apparmor
   ```

### 3. **Filter Journalctl Output**

If you don't want to change audit or AppArmor settings but just want to stop these messages from appearing in `journalctl`, you can filter them out with:

```bash
journalctl -f | grep -v "AVC apparmor"
```

This will filter out any line containing "AVC apparmor", so you won’t see these messages.

### 4. **Change AppArmor to Complain Mode (Less Secure)**
If you want AppArmor to log these events without blocking them, you can change its mode to "complain", which allows all actions but logs violations.

```bash
sudo aa-complain /snap/snapd/usr/lib/snapd/snap-confine
```

This will stop AppArmor from blocking the operation, but it may still log the attempt in a less critical manner.

### 5. **Allow the Capability (If You Trust It)**
If the message is related to a capability (like `perfmon` in this case), and you trust the application trying to access it, you can allow this capability in the AppArmor profile:

1. Open the relevant AppArmor profile (located in `/etc/apparmor.d/`).
2. Add a line like the following, depending on the capability you want to allow:
   ```bash
   capability perfmon,
   ```
3. Reload AppArmor:
   ```bash
   sudo apparmor_parser -r /etc/apparmor.d/your-profile
   ```

However, be cautious with this, as it affects system security. 

These steps should help you manage or filter the `auditd` and AppArmor logs according to your needs.
