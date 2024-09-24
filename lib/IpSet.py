import ipaddress
from IpSet4 import IpSet4
from IpSet6 import IpSet6

class IpSet:
    def __init__(self, ipsetname4='ufw-blocklist-ipsum', ipsetname6='ufw-blocklist6-ipset'):
        # Initialize both IpSet4 and IpSet6
        self.ipset4 = IpSet4(ipsetname4)
        self.ipset6 = IpSet6(ipsetname6)

    def is_ipv6(self, addr):
        """Helper method to determine if the address is IPv6"""
        return isinstance(ipaddress.ip_address(addr), ipaddress.IPv6Address)

    def add(self, ip_address):
        """Adds an IP address to the appropriate ipset (IPv4 or IPv6)"""
        if self.is_ipv6(ip_address):
            print(f"Delegating to IpSet6 for IP: {ip_address}")
            self.ipset6.add(ip_address)
        else:
            print(f"Delegating to IpSet4 for IP: {ip_address}")
            self.ipset4.add(ip_address)

    def delete(self, ip_address):
        """Deletes an IP address from the appropriate ipset (IPv4 or IPv6)"""
        if self.is_ipv6(ip_address):
            print(f"Delegating to IpSet6 for IP: {ip_address}")
            self.ipset6.delete(ip_address)
        else:
            print(f"Delegating to IpSet4 for IP: {ip_address}")
            self.ipset4.delete(ip_address)

    def test(self, ip_address):
        """Tests if an IP address is present in the appropriate ipset (IPv4 or IPv6)"""
        if self.is_ipv6(ip_address):
            print(f"Delegating to IpSet6 for IP: {ip_address}")
            return self.ipset6.test(ip_address)
        else:
            print(f"Delegating to IpSet4 for IP: {ip_address}")
            return self.ipset4.test(ip_address)

    def start(self):
        """Starts both IPv4 and IPv6 ipsets"""
        print("Starting IpSet4 and IpSet6...")
        self.ipset4.start()
        #self.ipset6.start()

    def stop(self):
        """Stops both IPv4 and IPv6 ipsets"""
        print("Stopping IpSet4 and IpSet6...")
        self.ipset4.stop()
        #self.ipset6.stop()

# Example usage of IpSet
if __name__ == "__main__":
    ipset_manager = IpSet()

    # Start both ipsets
    ipset_manager.start()

    # Add an IPv4 and IPv6 address
    ipset_manager.add("192.168.1.100")
    ipset_manager.add("2001:0db8::ff00:42:8329")

    # Test if the IPs are present
    ipset_manager.test("192.168.1.100")
    ipset_manager.test("2001:0db8::ff00:42:8329")

    # Delete the IPs from the ipsets
    ipset_manager.delete("192.168.1.100")
    ipset_manager.delete("2001:0db8::ff00:42:8329")

    # Stop both ipsets
    ipset_manager.stop()

