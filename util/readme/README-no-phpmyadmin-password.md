Question: If you've forgotten the password to phpmyadmin, how do you delete the database and start again

Answer:

The error message you're encountering, `mysqli::real_connect(): (HY000/1045): Access denied for user 'phpmyadmin'@'localhost' (using password: YES)`, typically means that the `phpmyadmin` user account is unable to authenticate with the provided credentials (password).

Here are steps you can take to resolve this issue:

### 1. **Verify the Correct User and Password:**
   - Make sure you're using the correct username and password. If the `phpmyadmin` user password has been changed or forgotten, you'll need to reset it.

### 2. **Reset the Password for the `phpmyadmin` User:**

   Since phpMyAdmin is just a web interface for MySQL/MariaDB, you can reset the password for the `phpmyadmin` user by accessing MySQL/MariaDB directly from the command line.

   **Step-by-Step Instructions:**

   1. **Log into MySQL/MariaDB as Root**:
      Open your terminal (or command prompt if using Windows) and log into MySQL or MariaDB using the root user:
      ```bash
      mysql -u root -p
      ```

   2. **Check the `phpmyadmin` User Exists**:
      You can check if the `phpmyadmin` user exists by running the following query:
      ```sql
      SELECT user, host FROM mysql.user WHERE user = 'phpmyadmin';
      ```

   3. **Reset the Password**:
      If the `phpmyadmin` user exists, reset its password:
      ```sql
      ALTER USER 'phpmyadmin'@'localhost' IDENTIFIED BY 'new_password';
      ```
      Replace `'new_password'` with the actual password you want to set.

   4. **Flush Privileges**:
      After resetting the password, flush the privileges to apply changes:
      ```sql
      FLUSH PRIVILEGES;
      ```

   5. **Exit the MySQL/MariaDB Prompt**:
      ```bash
      exit
      ```

### 3. **Update the phpMyAdmin Configuration File (if needed):**

   If the password for the `phpmyadmin` user was changed, you might also need to update the `config.inc.php` file used by phpMyAdmin to reflect the new password.

   1. **Locate the `config.inc.php` file**:
      The `config.inc.php` file is usually located in the phpMyAdmin installation directory. On most systems, it's typically found in:
      - **Linux**: `/etc/phpmyadmin/` or `/usr/share/phpmyadmin/`
      - **Windows**: `C:\xampp\phpMyAdmin\`
   
   2. **Edit the `config.inc.php` File**:
      Open the `config.inc.php` file in a text editor and look for the following line (or similar):
      ```php
      $cfg['Servers'][$i]['password'] = 'your_password';
      ```
      Replace `'your_password'` with the new password you just set for the `phpmyadmin` user.

   3. **Save the File** and restart your web server (Apache or Nginx) if necessary:
      ```bash
      sudo systemctl restart apache2   # For Apache
      sudo systemctl restart nginx     # For Nginx
      ```

### 4. **Verify the Permissions for the `phpmyadmin` User**:

   Ensure the `phpmyadmin` user has the necessary privileges:
   ```sql
   SHOW GRANTS FOR 'phpmyadmin'@'localhost';
   ```

   If the `phpmyadmin` user lacks privileges to access databases, you can grant them necessary permissions:
   ```sql
   GRANT ALL PRIVILEGES ON phpmyadmin.* TO 'phpmyadmin'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 5. **Clear phpMyAdmin Cookies:**
   Sometimes, old session cookies might cause authentication issues. Clear your browser cookies or try accessing phpMyAdmin in incognito/private browsing mode.

### 6. **Try Logging into phpMyAdmin Again:**
   Now try logging into phpMyAdmin using the new password you set for the `phpmyadmin` user.

### Summary of Steps:
1. Log into MySQL as root.
2. Reset the `phpmyadmin` user password.
3. Flush privileges.
4. Update the `config.inc.php` file with the new password (if necessary).
5. Restart the web server (Apache or Nginx).
6. Clear browser cookies or cache.

Let me know if you need further assistance!
