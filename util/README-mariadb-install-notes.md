To install **MariaDB** (an open-source database management system and a popular drop-in replacement for MySQL) on Ubuntu, follow these steps:

### 1. **Update the Package List**
Before installing MariaDB, ensure your package list is up-to-date:

```bash
sudo apt update
```

### 2. **Install MariaDB**
Install MariaDB with the following command:

```bash
sudo apt install mariadb-server
```

This will install both the MariaDB server and client.

### 3. **Start and Enable MariaDB**
After installation, MariaDB should start automatically. To ensure it's running and configured to start on boot, run:

```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

To check the status of the MariaDB service, use:

```bash
sudo systemctl status mariadb
```

### 4. **Run the Security Script**
MariaDB comes with a security script that helps you set up secure defaults, like removing test databases and setting a root password.

Run the script:

```bash
sudo mysql_secure_installation
```

During the process, you'll be asked several questions:

- **Set root password?**: You can set the MariaDB root password here.
- **Remove anonymous users?**: You should answer **Y** (Yes) to improve security.
- **Disallow root login remotely?**: Typically, you should say **Y** (Yes) unless you need remote root access.
- **Remove test database and access to it?**: Say **Y** (Yes).
- **Reload privilege tables now?**: Say **Y** (Yes).

### 5. **Test MariaDB Installation**

To log in to the MariaDB server, use the following command:

```bash
sudo mysql -u root -p
```

This will prompt you for the MariaDB root password that you set up during the `mysql_secure_installation` step. Once logged in, you’ll get a MariaDB prompt where you can run SQL commands.

### 6. **Optional: Create a New Database and User**

Once logged in to the MariaDB shell, you can create a new database and user as follows:

1. **Create a database**:
   ```sql
   CREATE DATABASE mydatabase;
   ```

2. **Create a new user and grant privileges**:
   Replace `username` and `password` with your desired values:
   ```sql
   CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON mydatabase.* TO 'username'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Exit MariaDB**:
   ```sql
   exit;
   ```

### 7. **Enable Remote Access (Optional)**

If you need MariaDB to accept remote connections, you can modify its configuration.

1. Open the MariaDB configuration file:
   ```bash
   sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
   ```

2. Find the line that says `bind-address` and change it to `0.0.0.0` to allow all remote connections:

   ```bash
   bind-address = 0.0.0.0
   ```

3. Restart MariaDB for the changes to take effect:
   ```bash
   sudo systemctl restart mariadb
   ```

**Important**: Ensure your firewall is configured to allow traffic on MariaDB's default port (3306) if you enable remote access.

### 8. **Firewall Configuration (Optional)**

If you're using a firewall like `ufw`, allow MariaDB through the firewall:

```bash
sudo ufw allow mysql
```

### 9. **Verify the Installation**

You can check the version of MariaDB installed with:

```bash
mariadb --version
```

You can also log into MariaDB to confirm it's working properly:

```bash
sudo mysql -u root -p
```

You should now have MariaDB successfully installed and running on your system!

Let me know if you need any further assistance.
