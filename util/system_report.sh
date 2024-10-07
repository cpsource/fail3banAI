#!/bin/bash

# Create a directory to store the collected data
output_dir="system_info"
mkdir -p $output_dir

# Collect kernel version and OS information
echo "Collecting kernel version and OS information..."
uname -a > $output_dir/kernel_info.txt
cat /etc/os-release > $output_dir/os_info.txt
if command -v lsb_release > /dev/null; then
    lsb_release -a >> $output_dir/os_info.txt
fi

# Collect list of installed packages (Debian/Ubuntu systems)
if command -v dpkg > /dev/null; then
    echo "Collecting installed packages (dpkg)..."
    dpkg -l > $output_dir/installed_packages.txt
fi

# Collect list of installed packages (RedHat/CentOS/Fedora systems)
if command -v rpm > /dev/null; then
    echo "Collecting installed packages (rpm)..."
    rpm -qa > $output_dir/installed_packages_rpm.txt
fi

# Collect system logs
echo "Collecting system logs..."
dmesg > $output_dir/dmesg_log.txt
journalctl -xe > $output_dir/journalctl_log.txt

# Collect CPU and memory info
echo "Collecting CPU and memory info..."
cat /proc/cpuinfo > $output_dir/cpu_info.txt
cat /proc/meminfo > $output_dir/mem_info.txt

# Bundle all the info into a tar.gz file
echo "Bundling the collected data..."
tar -czvf system_info_bundle.tar.gz $output_dir

# Cleanup
rm -rf $output_dir

echo "System information bundle created: system_info_bundle.tar.gz"

