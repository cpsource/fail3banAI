To enable and configure the **No-IP** Dynamic DNS (DDNS) service on your Ubuntu box, follow these steps:

### 1. **Install No-IP DUC (Dynamic Update Client)**

No-IP provides a Dynamic Update Client (DUC) that you can install to keep your dynamic IP address updated.

#### Step 1: Install the Required Packages
First, install the required packages to build the No-IP DUC software:

```bash
sudo apt update
sudo apt install build-essential libcurl4-openssl-dev
```

#### Step 2: Download No-IP DUC
Go to the No-IP website to download the latest DUC version. You can download the No-IP DUC tarball directly using `wget`:

```bash
cd /usr/local/src
sudo wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz
```

#### Step 3: Extract the No-IP DUC
Extract the tarball:

```bash
sudo tar xzf noip-duc-linux.tar.gz
cd noip-2.1.9-1  # Adjust version number if needed
```

#### Step 4: Compile and Install
Now, compile and install the No-IP DUC client:

```bash
sudo make
sudo make install
```

During the installation, it will ask for your **No-IP account email** and **password**, along with the hostnames you want to update. Make sure you've registered an account at [No-IP](https://www.noip.com/) and created a hostname before this step.

### 2. **Configure No-IP Client**

Once installed, you'll need to configure the No-IP client to automatically start on boot and periodically update your dynamic IP.

#### Step 1: Start the No-IP Client Manually
You can start the No-IP client manually using:

```bash
sudo /usr/local/bin/noip2
```

Check if it’s running:

```bash
sudo /usr/local/bin/noip2 -S
```

This will show the status of the client and any hostnames it is monitoring.

#### Step 2: Auto-Start No-IP on Boot
To enable No-IP DUC to start automatically on boot, you can create a systemd service.

1. **Create a systemd service file**:

   ```bash
   sudo nano /etc/systemd/system/noip2.service
   ```

2. **Add the following content to the file**:

   ```ini
   [Unit]
   Description=No-IP Dynamic DNS Update Client
   After=network.target

   [Service]
   Type=forking
   ExecStart=/usr/local/bin/noip2
   ExecReload=/usr/local/bin/noip2 -S
   ExecStop=/usr/local/bin/noip2 -K
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**:

   ```bash
   sudo systemctl enable noip2
   sudo systemctl start noip2
   ```

4. **Check the status** to ensure it's running:

   ```bash
   sudo systemctl status noip2
   ```

### 3. **Verify No-IP Client**

To ensure that the No-IP client is working correctly, you can check your No-IP dashboard to verify that your IP address has been updated.

You can also use this command to check the logs:

```bash
tail -f /var/log/syslog | grep noip2
```

### 4. **Troubleshooting**

If you encounter issues or want to manually stop or restart the No-IP client, you can use these commands:

- **Stop the client**:
  ```bash
  sudo systemctl stop noip2
  ```

- **Restart the client**:
  ```bash
  sudo systemctl restart noip2
  ```

Let me know if you need more details or assistance!
