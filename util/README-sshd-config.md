### The SSH server configuration file on most Linux systems is located at:

```
/etc/ssh/sshd_config
```

You can edit it using your preferred text editor, such as `nano`:

```bash
sudo nano /etc/ssh/sshd_config
```

### Key Security Recommendations for `sshd_config`

1. **Disable Root Login**:
   Prevent direct root access via SSH. Instead, use a regular user and escalate privileges with `sudo`.

   **Setting**:
   ```bash
   PermitRootLogin no
   ```

2. **Use Key-Based Authentication**:
   Disable password authentication and enforce the use of SSH keys for login. This is more secure than password-based logins.

   **Settings**:
   ```bash
   PasswordAuthentication no
   PubkeyAuthentication yes
   ```

3. **Change the Default SSH Port**:
   While not a foolproof method, changing the default SSH port from `22` to a non-standard port can reduce automated attacks.

   **Setting**:
   ```bash
   Port <custom-port-number>
   ```

4. **Limit User Access**:
   Restrict which users or groups are allowed to log in via SSH.

   **Setting**:
   ```bash
   AllowUsers youruser1 youruser2
   ```
   Or limit access by groups:
   ```bash
   AllowGroups sshusers
   ```

5. **Disable SSH Protocol 1**:
   SSH Protocol 1 is outdated and insecure. Ensure only Protocol 2 is used.

   **Setting**:
   ```bash
   Protocol 2
   ```

6. **Enable Strong Encryption Algorithms**:
   Restrict the allowed ciphers, MACs, and key exchange algorithms to stronger options.

   **Settings**:
   ```bash
   Ciphers aes256-ctr,aes192-ctr,aes128-ctr
   MACs hmac-sha2-512,hmac-sha2-256
   KexAlgorithms curve25519-sha256,ecdh-sha2-nistp256
   ```

7. **Use a Login Grace Time**:
   Limit the time allowed for a user to authenticate after the connection has been initiated.

   **Setting**:
   ```bash
   LoginGraceTime 60
   ```

8. **Limit Maximum Authentication Attempts**:
   Reduce the number of failed login attempts allowed before the connection is dropped.

   **Setting**:
   ```bash
   MaxAuthTries 3
   ```

9. **Disable Empty Passwords**:
   Ensure users with empty passwords cannot log in via SSH.

   **Setting**:
   ```bash
   PermitEmptyPasswords no
   ```

10. **Limit Idle Sessions**:
    Automatically disconnect users after a period of inactivity.

    **Setting**:
    ```bash
    ClientAliveInterval 300
    ClientAliveCountMax 0
    ```

### After Editing:
1. Save the file and exit the text editor.
2. Restart the SSH service to apply the changes:

   ```bash
   sudo systemctl restart ssh
   ```

### Additional Security Tips:
- **Firewall**: Configure a firewall (e.g., `ufw`) to only allow SSH connections on your custom port or from specific IP addresses.
- **Fail2Ban**: Install and configure Fail2Ban to block IP addresses that exhibit malicious behavior (e.g., brute force attacks).

These changes will significantly enhance the security of your SSH server. Let me know if you need help implementing any of these!
