
import os
import sys
import subprocess
import ipaddress

class ManageIpset:
    def __init__(self):
        self.ipsetname = "ufw-blocklist-ipsum"
        self.ipset_exe = "/usr/sbin/ipset"
        self.project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
        if not self.project_root:
            raise EnvironmentError("Environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
        self.seedlist = self.project_root + "/control/" + "blacklist-4.ctl"

        # Check if ipset exists
        if not self.is_executable(self.ipset_exe):
            errmsg = f"{self.ipset_exe} is not executable"
            raise RuntimeError(errmsg)

    def is_executable(self, path):
        """Check if a file is executable"""
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def chain_exists(self, chain_name, table=None, iptables_cmd="iptables"):
        """Check if a chain exists in iptables"""
        table_arg = ["--table", table] if table else []
        result = subprocess.call([iptables_cmd, "-n", "--list", chain_name] + table_arg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def set_exists(self, setname):
        """Check if an ipset set exists"""
        result = subprocess.call([self.ipset_exe, "list", setname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result == 0

    def start(self, iptables_cmd="iptables"):
        """Start the ipset and iptables configuration"""
        if not self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "create", self.ipsetname, "hash:net", "family", "inet", "hashsize", "32768", "maxelem", "65536"])

        if not self.chain_exists("ufw-blocklist-input"):
            subprocess.run([iptables_cmd, "-N", "ufw-blocklist-input"])
            subprocess.run([iptables_cmd, "-A", "INPUT", "-m", "set", "--match-set", self.ipsetname, "src", "-j", "ufw-blocklist-input"])
            subprocess.run([iptables_cmd, "-A", "ufw-blocklist-input", "-p", "all", "-m", "limit",  "--limit 5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "'zDROP ufw-blocklist-input: '", "--log-level", "4"])
            subprocess.run([iptables_cmd, "-I", "ufw-blocklist-input", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP"])

        if not self.chain_exists("ufw-blocklist-output"):
            subprocess.run([iptables_cmd, "-N", "ufw-blocklist-output"])
            subprocess.run([iptables_cmd, "-A", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output"])
            subprocess.run([iptables_cmd, "-A", "ufw-blocklist-output", "-p", "all", "-m", "limit",  "--limit 5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "'zDROP ufw-blocklist-output: '", "--log-level", "4"])
            subprocess.run([iptables_cmd, "-I", "ufw-blocklist-output", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP"])

        if not self.chain_exists("ufw-blocklist-forward"):
            subprocess.run([iptables_cmd, "-N", "ufw-blocklist-forward"])
            subprocess.run([iptables_cmd, "-A", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward"])
            subprocess.run([iptables_cmd, "-A", "ufw-blocklist-forward", "-p", "all", "-m", "limit",  "--limit 5/min", "--limit-burst", "10", "-j", "LOG", "--log-prefix", "'zDROP ufw-blocklist-forward: '", "--log-level", "4"])
            subprocess.run([iptables_cmd, "-I", "ufw-blocklist-forward", "2", "-p", "all", "-s", "0.0.0.0/0", "-d", "0.0.0.0/0", "-j", "DROP"])

        # Add IP addresses to ipset
        with open(self.seedlist, 'r') as f:
            for ip in f.readlines():
                subprocess.run([self.ipset_exe, "add", self.ipsetname, ip.strip()])

    def stop(self, iptables_cmd="iptables"):
        """Stop the ipset and delete the chains and sets"""
        if self.chain_exists("ufw-blocklist-input"):
            subprocess.run([iptables_cmd, "-D", "INPUT", "-m", "set", "--match-set", self.ipsetname, "src", "-j", "ufw-blocklist-input"])
            subprocess.run([iptables_cmd, "-F", "ufw-blocklist-input"])
            subprocess.run([iptables_cmd, "-X", "ufw-blocklist-input"])

        if self.chain_exists("ufw-blocklist-output"):
            subprocess.run([iptables_cmd, "-D", "OUTPUT", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-output"])
            subprocess.run([iptables_cmd, "-F", "ufw-blocklist-output"])
            subprocess.run([iptables_cmd, "-X", "ufw-blocklist-output"])

        if self.chain_exists("ufw-blocklist-forward"):
            subprocess.run([iptables_cmd, "-D", "FORWARD", "-m", "set", "--match-set", self.ipsetname, "dst", "-j", "ufw-blocklist-forward"])
            subprocess.run([iptables_cmd, "-F", "ufw-blocklist-forward"])
            subprocess.run([iptables_cmd, "-X", "ufw-blocklist-forward"])

        if self.set_exists(self.ipsetname):
            subprocess.run([self.ipset_exe, "flush", self.ipsetname])
            subprocess.run([self.ipset_exe, "destroy", self.ipsetname])

    def status(self, iptables_cmd="iptables"):
        """Show the current status of the ipset and iptables and journalctl"""
        subprocess.run([self.ipset_exe, "list", self.ipsetname, "-t"])
        subprocess.run([iptables_cmd, "-L", "--line-numbers", "-nvx"])

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

    def flush_all(self, iptables_cmd="iptables"):
        """Flush all the sets and reset iptables accounting"""
        subprocess.run([self.ipset_exe, "flush", self.ipsetname])
        subprocess.run([iptables_cmd, "-Z", "INPUT"])
        subprocess.run([iptables_cmd, "-Z", "ufw-blocklist-input"])
        subprocess.run([iptables_cmd, "-Z", "OUTPUT"])
        subprocess.run([iptables_cmd, "-Z", "ufw-blocklist-output"])
        subprocess.run([iptables_cmd, "-Z", "FORWARD"])
        subprocess.run([iptables_cmd, "-Z", "ufw-blocklist-forward"])

def main():
    if os.geteuid() != 0:
        print("You must run this script as root.")
        sys.exit(1)

    if len(sys.argv) != 3:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()
    iptab = sys.argv[2].lower()
    
    manager = ManageIpset()

    if cmd == "start":
        manager.start(iptables_cmd=iptab)
    elif cmd == "stop":
        manager.stop(iptables_cmd=iptab)
    elif cmd == "status":
        manager.status(iptables_cmd=iptab)
    elif cmd == "flush-all":
        manager.flush_all(iptables_cmd=iptab)
    else:
        print_help()
        sys.exit(1)

def print_help():
    print("Usage: script.py {start|stop|status|flush-all} iptables_cmd")

# To invoke main when run directly
if __name__ == "__main__":
    main()

