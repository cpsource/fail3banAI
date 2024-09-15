# fail3ban-server

import sys
import os
import threading
import time
from datetime import datetime

#
# Allow our foundation classes to be loaded
#
# Get the absolute path of the current directory (the directory containing this script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the subdirectory to the system path
subdirectory_path = os.path.join(current_dir, 'lib')
sys.path.append(subdirectory_path)

# Now you can import modules from the subdirectory
import f3b_whitelist
import f3b_blacklist
import f3b_fail3baninit
import f3b_Iptables
import f3b_match_rule
import f3b_SectionParser
import f3b_ruleset
import f3b_config
import f3b_sqlite3_db
import f3b_DebugPrint
import f3b_matchRule

#
# Config values can be overwritten by config.ctl
#
# default value of debug
debug = False
# default value of pretend.
pretend = False

#
# routine to fold None into False
#
def check_var(var):
    return var if isinstance(var, bool) else (False if var is None else var)
# Test cases
#print(check_var(True))    # True
#print(check_var(False))   # False
#print(check_var(None))    # False
#print(check_var(42))      # 42 (since var is not None or bool)
#print(check_var("hello")) # "hello" (since var is not None or bool)

# A worker thread
def manage_bans(db_instance, iptables_class):
    """Manage bans by ensuring non-banned IPs are in iptables, and expired IPs are removed."""
    
    # Save ptr to database
    db_instance = db_instance
    # ipt allows us to manage iptables
    ipt = iptables_class()

    # 1. Initial step: ensure non-banned IPs are in iptables
    print("Ensuring non-banned IPs are in iptables...")
    non_banned_records = db_instance.get_expired_records()  # Method should return non-banned IPs
    for record in non_banned_records:
        ip_addr, is_ipv6, jail = record
        # Ensure the IP is in iptables
        if not ipt.is_in_chain(ip_addr):  # Assuming iptables class has this method
            ipt.add_chain_to_INPUT(ip_addr, jail)

    # 2. Loop forever to scan for expired bans
    while True:
        print("Scanning for expired bans...")
        
        # Query for expired bans
        expired_bans = db_instance.get_expired_records()  # Get expired IPs from database
        for record in expired_bans:
            ip_addr, is_ipv6, jail = record
            
            # Remove from iptables
            ipt.remove_chain(ip_addr)
            print(f"Removed IP {ip_addr} from iptables.")
            
            # Remove from the database
            db_instance.remove_record(ip_addr, jail)
            print(f"Removed IP {ip_addr} from database.")
        
        # Sleep for an hour
        print("Sleeping for 1 hour...")
        time.sleep(3600)

# Example usage in a thread
def start_manage_bans(db_instance):
    thread = threading.Thread(target=manage_bans, args=(db_instance, f3b_iptables.iptables))  # Or use mariaDB
    thread.start()

if __name__ == "__main__":
    # Create a Config instance and load the config.ctl file
    configClass = f3b_config.Config('config.ctl')
    configData = configClass.get_config_data()

    # Setup debugging print
    debugPrintClass = f3b_DebugPrint.DebugPrint(configClass)
    
    # Get pretend flag
    tmp_var = configData.get('pretend')
    if tmp_var is not None:
        debugPrintClass.print(f"pretending for this session is set to {tmp_var}")
    else:
        debugPrintClass.print(f"pretending for this session isset to {pretend}")
    # Get default_ban_time
    tmp_var = configData.get('default_ban_time')
    if tmp_var is not None:
        debugPrintClass.print(f"default ban time for this session is set to {tmp_var} minutes")
        default_ban_time = tmp_var
    else:
        default_ban_time = 1
        debugPrintClass.print(f"default ban time defaults to 1 minute")

    # sqlite3 initialization
    db_instance = f3b_sqlite3_db.SQLiteDB()
    if db_instance is not None:
        db_instance.initialize(configData.get('database_name'))
        if debug:
            debugPrintClass.print(f"sqlite3 database initialized","INFO")            
    else:
        debugPrintClass.print(f"can't initialize sqlite3 database initialized","ERROR")            
            
    # whitelist initialization
    wl = f3b_whitelist.Whitelist(configData)
    wl.whitelist_init()
    debugPrintClass.print("Whitelisted IPs:", wl.get_whitelist())

    # Initialize with debug=True to enable debug prints
    rs = f3b_ruleset.Ruleset(debug=False)
    # Example of retrieving a specific ruleset by filename (without .conf)
    trial_ruleset = 'test'
    specific_ruleset = rs.get_ruleset_by_filename(trial_ruleset)
    if specific_ruleset:
        debugPrintClass.print(f"Ruleset for '{trial_ruleset}': {specific_ruleset}")
    else:
        debugPrintClass.print("Ruleset not found for '{trial_ruleset}'",'ERROR')
