
import os
import sys
import subprocess
import ipaddress

class ManageIpset6:
    def __init__(self):
        self.ipsetname = "ufw-blocklist6-ipsum"
        self.seedlist = "ipsum.7.txt"
        self.ipset_exe = "/usr/sbin/ipset"
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
        if not self.project_root:
            raise EnvironmentError("Environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
        # Check if executable ipset exists
        if not self.is_executable(self.ipset_exe):
            errmsg = f"{self.ipset_exe} is not executable"
            raise RuntimeError(errmsg)
        self.seedlist = self.project_root + "/control/blacklist.ctl"

    def is_executable(self, path):
        """Check if a file is executable"""
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def chain_exists(self, chain_name, table=None):
        """Check if a chain exists in ip6tables"""
        table_arg = ["--table", table] if table else []
        result = subprocess.call(["ip6tables", "-n", "--list", chain_name] + table_arg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def set_exists(self, setname):
        """Check if an ipset set exists"""
        result = subprocess.call([self.ipset_exe, "list", setname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def add_ip_addresses_to_ipset(self):
        """Add IPv6 addresses from seedlist to ipset, skipping comments and shrinking IPv6 addresses."""
        with open(self.seedlist, 'r') as f:
            for line in f.readlines():
                line = line.strip()

                # Skip comments or empty lines
                if not line or line.startswith('#'):
                    continue

                try:
                    # Parse the IP address
                    ip_obj = ipaddress.ip_address(line)

                    # If it's a valid IPv6 address, shrink it
                    if isinstance(ip_obj, ipaddress.IPv6Address):
                        line = ip_obj.compressed

                        # Add the IP to the ipset
                        subprocess.run([self.ipset_exe, "add", self.ipsetname, line])
                except ValueError:
                    # Skip invalid IP addresses
                    print(f"Invalid IPv6 address skipped: {line}")
    
    def start(self):
        """Start the ipset and ip6tables configuration"""
        if not self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "create", self.ipsetname, "hash:net", "family", "inet6", "hashsize", "32768", "maxelem", "65536"])

        if not self.chain_exists("ufw-blocklist-input"):
            subprocess.run(["ip6tables", "-N", "ufw-blocklist-input"])
            subprocess.run(["ip6tables", "-A", "INPUT", "-m", "set", "--match-set", self.ipsetname, "src", "-j", "ufw-blocklist-input"])

        if not self.chain_exists("ufw-blocklist-output"):
            subprocess.run(["ip6tables", "-N", "ufw-blocklist-output"])
            subprocess.run(["ip6tables", "-A", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output"])

        if not self.chain_exists("ufw-blocklist-forward"):
            subprocess.run(["ip6tables", "-N", "ufw-blocklist-forward"])
            subprocess.run(["ip6tables", "-A", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward"])

        # Add IP addresses to ipset
        self.add_ip_addresses_to_ipset()

    def stop(self):
        """Stop the ipset and delete the chains and sets"""
        if self.chain_exists("ufw-blocklist-input"):
            subprocess.run(["ip6tables", "-D", "INPUT", "-m", "set", "--match-set", self.ipsetname, "src", "-j", "ufw-blocklist-input"])
            subprocess.run(["ip6tables", "-F", "ufw-blocklist-input"])
            subprocess.run(["ip6tables", "-X", "ufw-blocklist-input"])

        if self.chain_exists("ufw-blocklist-output"):
            subprocess.run(["ip6tables", "-D", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output"])
            subprocess.run(["ip6tables", "-F", "ufw-blocklist-output"])
            subprocess.run(["ip6tables", "-X", "ufw-blocklist-output"])

        if self.chain_exists("ufw-blocklist-forward"):
            subprocess.run(["ip6tables", "-D", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward"])
            subprocess.run(["ip6tables", "-F", "ufw-blocklist-forward"])
            subprocess.run(["ip6tables", "-X", "ufw-blocklist-forward"])

        if self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "flush", self.ipsetname])
            subprocess.run([self.ipset_exe, "destroy", self.ipsetname])

    def status(self):
        """Show the current status of the ipset and ip6tables and journalctl"""
        subprocess.run([self.ipset_exe, "list", self.ipsetname, "-t"])
        subprocess.run(["/usr/sbin/ip6tables", "-L", "-nvx"])

        # this runs, but it takes too long, so let's skip it
        # The format of the call is different because subprocess.run doesn't handle pipes the same a bash shell
        if False:
            # Pipe the output of journalctl to grep and then to tail
            journalctl_proc = subprocess.Popen(["/usr/bin/journalctl"], stdout=subprocess.PIPE)
            grep_proc = subprocess.Popen(["/usr/bin/grep", "-i", "blocklist"], stdin=journalctl_proc.stdout, stdout=subprocess.PIPE)
            journalctl_proc.stdout.close()  # Allow journalctl to receive a SIGPIPE if grep exits
            tail_proc = subprocess.Popen(["/usr/bin/tail"], stdin=grep_proc.stdout)
            grep_proc.stdout.close()  # Allow grep to receive a SIGPIPE if tail exits
            tail_proc.communicate()

    def flush_all(self):
        """Flush all the sets and reset ip6tables accounting"""
        subprocess.run([self.ipset_exe, "flush", self.ipsetname])
        subprocess.run(["ip6tables", "-Z", "INPUT"])
        subprocess.run(["ip6tables", "-Z", "ufw-blocklist-input"])
        subprocess.run(["ip6tables", "-Z", "OUTPUT"])
        subprocess.run(["ip6tables", "-Z", "ufw-blocklist-output"])
        subprocess.run(["ip6tables", "-Z", "FORWARD"])
        subprocess.run(["ip6tables", "-Z", "ufw-blocklist-forward"])


def main():
    if os.geteuid() != 0:
        print("You must run this script as root.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    manager = ManageIpset6()

    if cmd == "start":
        manager.start()
    elif cmd == "stop":
        manager.stop()
    elif cmd == "status":
        manager.status()
    elif cmd == "flush-all":
        manager.flush_all()
    else:
        print_help()
        sys.exit(1)

def print_help():
    print("Usage: script.py {start|stop|status|flush-all}")

# To invoke main when run directly
if __name__ == "__main__":
    main()

