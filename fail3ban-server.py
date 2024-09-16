# fail3ban-server

import sys
import os
import threading
import time
from datetime import datetime
import time
import logging

# Define the stop_event as a threading.Event before starting thread
stop_event = threading.Event()

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
import f3b_iptables
#import f3b_match_rule
#import f3b_SectionParser
#import f3b_ruleset
import f3b_config
import f3b_sqlite3_db
import f3b_matchRule

# Extracted constants for log file name and format
LOG_FILE_NAME = "fail3ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_ID = "fail3ban"

#
# Config values can be overwritten by config.ctl
#
# default value of debug
debug = False
# default value of pretend.
pretend = False

# Extracted function to set up logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE_NAME),
            logging.StreamHandler()
        ]
    )
# Create a named logger consistent with the log file name
#logger = logging.getLogger(LOG_ID)

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

#
# A worker thread - periodically, we scan the database for
# expired bans. If we find any, we remove them from iptables
#
def manage_bans(stop_event):
    """Manage bans by ensuring non-banned IPs are in iptables, and expired IPs are removed."""

    # Get our logger - use global logger
    logger.debug("manage_bans thread started")
    
    # Create a new database instance. (For thread safety with SQLite3, each thread needs their own)
    db_instance = f3b_sqlite3_db.SQLiteDB()
    if db_instance is not None:
        logger.debug(f"sqlite3 database initialized")
    else:
        logger.error(f"can't initialize sqlite3 database")            
        sys.exit(1)

    # ipt allows us to manage iptables
    ipt = f3b_iptables.Iptables()
    
    # 1. Initial step: ensure non-banned IPs are in iptables
    logger.debug("Ensuring non-banned IPs are in iptables...")
    non_banned_records = db_instance.get_non_expired_records()  # Method should return non-banned IPs
    for record in non_banned_records:
        ip_addr, is_ipv6, jail = record
        # Ensure the IP is in iptables
        if not ipt.is_in_chain(ip_addr):  # Assuming iptables class has this method
            ipt.add_chain_to_INPUT(ip_addr, jail, "server")

    # 2. Loop forever or told to stop. Scan for expired bans and remove them
    while not stop_event.is_set():
        logger.debug("Scanning for expired bans...")
        
        # Query for expired bans
        expired_bans = db_instance.get_expired_records()  # Get expired IPs from database
        for record in expired_bans:
            ip_addr, is_ipv6, jail = record

            logger.debug(f"Expired: record = {record}")

            if False:
                # Remove from iptables $$$ needs something like unjail(ip,ipv6-flag,jail,extra)
                ipt.remove_chain(ip_addr, "server")
                logger.debug(f"Removed IP {ip_addr} from iptables.")
            
                # Remove from the database
                db_instance.remove_record(ip_addr, jail)
                logger.debug(f"Removed IP {ip_addr} from database.")

        # wait around in dribs and drabs so we can be responsive to a stop_event
        iteration = 0
        #RESOLUTION = 4 # 4 is every 15 secondes (debugging), 1 is once a minute (production)
        while not stop_event.is_set() and iteration < 60:
            iteration += 1
            # Sleep for an hour
            #logger.debug("Sleeping for 1 hour...")
            time.sleep(1)
        logger.debug(f"awakened from sleep, iterations remaining {iteration}")
    logger.debug("thread manage_bans is returning")
    
if __name__ == "__main__":
    # setup logging
    setup_logging()
    # Create a named logger consistent with the log file name
    logger = logging.getLogger(LOG_ID)
    
    # And show logger for debugging
    logger.debug(f"__main__: logger = {logger}")
    
    # Create a Config instance and load the config.ctl file
    cc = f3b_config.Config('config.ctl')
    configData = cc.get_config_data()

    # Get config values
    tmp_var = configData.get('pretend')
    if tmp_var is not None:
        logger.debug(f"pretending for this session is set to {tmp_var}")
    else:
        logger.debug(f"pretending for this session isset to {pretend}")
    # Get default_ban_time
    tmp_var = configData.get('default_ban_time')
    if tmp_var is not None:
        logger.debug(f"default ban time for this session is set to {tmp_var} minutes")
        default_ban_time = tmp_var
    else:
        default_ban_time = 1
        logger.debug(f"default ban time defaults to 1 minute")

    # sqlite3 initialization. We just open it to be sure it's in good shape
    db_instance = f3b_sqlite3_db.SQLiteDB()
    if db_instance is not None:
        logger.debug(f"sqlite3 database initialized")
        db_instance.close()
        db_instance = None
    else:
        logger.debug(f"can't initialize sqlite3 database initialized")            
            
    # whitelist initialization
    wl = f3b_whitelist.WhiteList(configData)
    wl.whitelist_init()
    logger.debug(f"Whitelisted IPs: {wl.get_whitelist()}")
    # put them into INPUT table
    wl.add_whitelist_to_iptables()

    # blacklist initializaiton
    bl = f3b_blacklist.BlackList()
    bl.blacklist_init()
    #IPS = f"Blacklisted IPs: {bl.get_blacklist()}"
    logger.debug(f"Blacklisted IPs: {bl.get_blacklist()}")
    # Add them into INPUT table
    bl.add_blacklist_to_iptables()

    # nap for a bit
    time.sleep(0.1)

    # lets show our iptables at this point (should be full)
    wl.show_iptables()

    # lets cleanup iptables
    wl.remove_iptables_from_input()
    bl.remove_blacklisted_ip_tables_from_input()

    # nap for a bit
    time.sleep(0.1)

    # lets show our iptables again (should be empty)
    wl.show_iptables()

    # start scanning database for expired bans
    thread = threading.Thread(target=manage_bans, args=(stop_event,))  # Or use mariaDB
    thread.start()

    # run for a bit
    time.sleep(90)

    # Signal thread manage_bans to stop
    stop_event.set()

    # Wait for thread
    thread.join()
    logger.debug("thread manage_bans stopped cleanly")
    
    # exit for now
    sys.exit(0)
    
    # Initialize with debug=True to enable debug prints
    rs = f3b_ruleset.Ruleset(debug=False)
    # Example of retrieving a specific ruleset by filename (without .conf)
    trial_ruleset = 'test'
    specific_ruleset = rs.get_ruleset_by_filename(trial_ruleset)
    if specific_ruleset:
        logger.debug(f"Ruleset for '{trial_ruleset}': {specific_ruleset}")
    else:
        logger.debug("Ruleset not found for '{trial_ruleset}'",'ERROR')
