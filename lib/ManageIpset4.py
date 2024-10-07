
import os
import sys
import subprocess
import ipaddress

class ManageIpset4:
    def __init__(self):
        self.ipsetname = "ufw-blocklist-ipsum"
        self.ipset_exe = "/usr/sbin/ipset"
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
        if not self.project_root:
            raise EnvironmentError("Environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
        #self.seedlist = self.project_root + "/control/" + "blacklist-4.ctl"
        self.seedlist = self.project_root + "/control/master-blacklist.ctl"

        # Check if ipset exists
        if not self.is_executable(self.ipset_exe):
            errmsg = f"{self.ipset_exe} is not executable"
            raise RuntimeError(errmsg)

    def is_executable(self, path):
        """Check if a file is executable"""
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def chain_exists(self, chain_name):
        """Check if a chain exists in iptables"""
        result = subprocess.call(["iptables", "-n", "--list", chain_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def set_exists(self, setname):
        """Check if an ipset set exists"""
        result = subprocess.call([self.ipset_exe, "list", setname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def add_ip_addresses_to_ipset(self):
        return
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
                    if isinstance(ip_obj, ipaddress.IPv4Address):
                        line = ip_obj.compressed

                        # Add the IP to the ipset
                        subprocess.run([self.ipset_exe, "add", self.ipsetname, line])
                except ValueError:
                    # Skip invalid IP addresses
                    print(f"Invalid IPv6 address skipped: {line}")
    
    def start(self):
        """Start the ipset and iptables configuration"""
        if not self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "create", self.ipsetname, "hash:net", "family", "inet", "hashsize", "32768", "maxelem", "65536"])

        if not self.chain_exists("ufw-blocklist-input"):
            # Create the chain if it doesn't exist
            subprocess.run(["iptables", "-N", "ufw-blocklist-input"], check=True)
    
            # Append the rule to INPUT to jump to ufw-blocklist-input chain for the IP set
            subprocess.run([
                "iptables", "-A", "INPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-input" ], check=True)
    
            # Add the logging rule to the ufw-blocklist-input chain
            subprocess.run([
                "iptables", "-A", "ufw-blocklist-input", "-p", "all", "-m", "limit", "--limit", "5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "zDROP ufw-blocklist-input: ", "--log-level", "4" ], check=True)
    
            # Insert the DROP rule into the ufw-blocklist-input chain
            subprocess.run([
                "iptables", "-I", "ufw-blocklist-input", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP" ], check=True)

        if not self.chain_exists("ufw-blocklist-output"):
            # Create the chain if it doesn't exist
            subprocess.run(["iptables", "-N", "ufw-blocklist-output"], check=True)
    
            # Append the rule to OUTPUT to jump to ufw-blocklist-output chain for the IP set
            subprocess.run([
                "iptables", "-A", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output" ], check=True)
    
            # Add the logging rule to the ufw-blocklist-output chain
            subprocess.run([
                "iptables", "-A", "ufw-blocklist-output", "-p", "all", "-m", "limit", "--limit", "5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "zDROP ufw-blocklist-output: ", "--log-level", "4" ], check=True)
    
            # Insert the DROP rule into the ufw-blocklist-output chain
            subprocess.run([
                "iptables", "-I", "ufw-blocklist-output", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP" ], check=True)

        if not self.chain_exists("ufw-blocklist-forward"):
            # Create the chain if it doesn't exist
            subprocess.run(["iptables", "-N", "ufw-blocklist-forward"], check=True)
    
            # Append the rule to FORWARD to jump to ufw-blocklist-forward chain for the IP set
            subprocess.run([
                "iptables", "-A", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward" ], check=True)
    
            # Add the logging rule to the ufw-blocklist-forward chain
            subprocess.run([
                "iptables", "-A", "ufw-blocklist-forward", "-p", "all", "-m", "limit", "--limit", "5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "zDROP ufw-blocklist-forward: ", "--log-level", "4"], check=True)
    
            # Insert the DROP rule into the ufw-blocklist-forward chain
            subprocess.run([
                "iptables", "-I", "ufw-blocklist-forward", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP"], check=True)

        #sys.exit(0)
        
        # Add IP addresses to ipset
        self.add_ip_addresses_to_ipset()

    def stop(self):
        """Stop the ipset and delete the chains and sets"""

        if self.chain_exists("ufw-blocklist-input"):
            subprocess.run(["iptables", "-D", "INPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-input"])
            subprocess.run(["iptables", "-F", "ufw-blocklist-input"])
            subprocess.run(["iptables", "-X", "ufw-blocklist-input"])

        if self.chain_exists("ufw-blocklist-output"):
            subprocess.run(["iptables", "-D", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output"])
            subprocess.run(["iptables", "-F", "ufw-blocklist-output"])
            subprocess.run(["iptables", "-X", "ufw-blocklist-output"])

        if self.chain_exists("ufw-blocklist-forward"):
            subprocess.run(["iptables", "-D", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward"])
            subprocess.run(["iptables", "-F", "ufw-blocklist-forward"])
            subprocess.run(["iptables", "-X", "ufw-blocklist-forward"])

        if self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "flush", self.ipsetname])
            subprocess.run([self.ipset_exe, "destroy", self.ipsetname])

    def status(self):
        """Show the current status of the ipset and iptables and journalctl"""
        subprocess.run([self.ipset_exe, "list", self.ipsetname, "-t"])
        subprocess.run(["/usr/sbin/iptables", "-L", "--line-numbers", "-nvx"])

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
        """Flush all the sets and reset iptables accounting"""
        subprocess.run([self.ipset_exe, "flush", self.ipsetname])
        subprocess.run(["iptables", "-Z", "INPUT"])
        subprocess.run(["iptables", "-Z", "ufw-blocklist-input"])
        subprocess.run(["iptables", "-Z", "OUTPUT"])
        subprocess.run(["iptables", "-Z", "ufw-blocklist-output"])
        subprocess.run(["iptables", "-Z", "FORWARD"])
        subprocess.run(["iptables", "-Z", "ufw-blocklist-forward"])


def main():
    if os.geteuid() != 0:
        print("You must run this script as root.")
        sys.exit(1)

    if len(sys.argv) != 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    manager = ManageIpset4()

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

