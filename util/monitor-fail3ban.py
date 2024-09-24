#!/usr/bin/env python3

import os
#import subprocess
import tempfile
#import re
import ipaddress
import sys
from dotenv import load_dotenv
import subprocess
import signal
import threading
import ipaddress; is_ipv6 = lambda addr: isinstance(ipaddress.ip_address(addr), ipaddress.IPv6Address)

# Configure logging
import logging
# and some magic numbers for logging
FLAG_CRITICAL = 50
FLAG_ERROR = 40
FLAG_WARNING = 30
FLAG_INFO = 20
FLAG_DEBUG = 10
FLAG_NOSET = 0

# Extracted constants for log file name and format
LOG_FILE_NAME = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/" + "fail3ban.log"
# Set up the logging format to include file name and line number
LOG_FORMAT = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
# And our log id
LOG_ID = "fail3ban"

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
# Call the extracted function to configure logging
setup_logging()

# Create a named logger consistent with the log file name
logger = logging.getLogger(LOG_ID)

# load dotenv
try:
    # Attempt to load dotenv file using the environment variable
    dotenv_config = load_dotenv(f"{os.getenv('HOME')}/.env")
    logger.info("dotenv file loaded successfully.")
except Exception as e:
    # Handle any exceptions that may occur
    logger.error(f"An error occurred while loading dotenv: {e}")

#
# Load our python3 paths
#
# Get the FAIL3BAN_PROJECT_ROOT environment variable
project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
# Check if FAIL3BAN_PROJECT_ROOT is not set
if project_root is None:
    print("Error: The environment variable 'FAIL3BAN_PROJECT_ROOT' is not set.")
    sys.exit(1)  # Exit the program with an error code
# Construct the lib path
lib_path = os.path.join(project_root, 'lib')
# Add the constructed path to sys.path only if it's not already in sys.path
if lib_path not in sys.path:
    sys.path.append(lib_path)
    print(f"Added {lib_path} to the system path.")
else:
    print(f"{lib_path} is already in the system path.")

# Get the absolute path of the current directory (the directory containing this script)
#current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the subdirectory to the system path
#subdirectory_path = os.path.join(current_dir, '../lib')
#sys.path.append(subdirectory_path)

from PreviousJournalctl import PreviousJournalctl

# get HashedSet
import f3b_HashedSet

# get CountryCode
import f3b_CountryCodes

# get ShortenJournalString
import f3b_ShortenJournalString

# get database
import f3b_sqlite3_db

# get whitelist
import f3b_whitelist

# get GlobalShutdown
import f3b_GlobalShutdown

#
# Here's a double line that needs to be combined
# into one line, so we can process it effectively.
# I suggest we keep track of the previous line and
# combine them if the [digits] and [jail] are the same.
#

#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: error: kex_exchange_identification: Connection closed by remote host
#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: Connection closed by 104.152.52.121 port 51587

# Path to the temporary file in /tmp
#temp_file = tempfile.NamedTemporaryFile(delete=False, dir='/tmp', mode='w', prefix='journal_', suffix='.log')

import subprocess
import re
import time

def find_country(ip_address_string):
    attempts = 3  # Number of retry attempts
    sleep_time = 0.1  # Sleep for 100 milliseconds (0.1 seconds)

    for attempt in range(attempts):
        try:
            # Execute the 'whois' command for the given IP address
            tmp_result = subprocess.run(['whois', ip_address_string], capture_output=True, text=True)

            # Check if the command ran successfully
            if tmp_result.returncode != 0:
                raise Exception("Failed to run whois command.")

            # Search for the line starting with 'country:'
            match = re.search(r"^country:\s+(.+)$", tmp_result.stdout, re.MULTILINE | re.IGNORECASE)

            if match:
                # Extract and return the country code (everything after 'country:')
                tmp_country = match.group(1).strip()
                tmp_country_code = cc.get_country(tmp_country).strip()
                return tmp_country_code
            else:
                # Return None if no country line is found
                return None
        except Exception as e:
            if attempt < attempts - 1:  # If this isn't the last attempt, sleep and retry
                time.sleep(sleep_time)
            else:
                print(f"Error after {attempts} attempts: {e}")
                return None

def has_ip_address(input_string):
    """
    Checks if the input string contains an IPv4 or IPv6 address.
    
    Parameters:
        input_string (str): The string to check for IP addresses.
        
    Returns:
        bool: True if an IP address is found, False otherwise.
    """
    # Regular expression for IPv4 and IPv6 addresses
    ip_pattern = r"\[[0-9]+\]:.*\b((?:(?:\d{1,3}\.){3}\d{1,3})|(?:[a-fA-F0-9:]+))\b"
    
    # Search for the pattern in the input string
    rex = re.search(ip_pattern, input_string)
    if rex:
        #print(f"has_ip_address returns True {rex.group()}")
        return True
    #print("has_ip_address returns False")
    return False

def extract_log_info(log_line):
    """
    Extracts jail name, sequence number, and IP address from a log entry in the given order:
    jail -> sequence number -> IP address. Each subsequent search starts after the previous match.

    Parameters:
        log_line (str): The log entry as a string.
        
    Returns:
        tuple: (jail, sequence_number, [ip_type, ip_address])
            - jail: The jail name (e.g., sshd).
            - sequence_number: The sequence number from [] (as a string).
            - ip_info: A list containing the type of IP ('ipv4' or 'ipv6') and the IP address. 
              If no IP is found, this is None.
    """
    # Regex for jail name (word before '\[')
    jail_pattern = r"(\w+)\s*\["
    
    # Regex for sequence number inside []
    sequence_pattern = r"\[(\d+)\]"
    
    # Regex for IP address (IPv4 or IPv6) with word boundaries
    ip_pattern = r"\b((?:(?:\d{1,3}\.){3}\d{1,3})|(?:[a-fA-F0-9:]+))\b"
    
    # Start search from the beginning of the string
    current_position = 0
    
    # Step 1: Extract jail name (match up to the "[" but don't include it)
    jail_match = re.search(jail_pattern, log_line)
    jail = jail_match.group(1) if jail_match else None
    
    # Update the current position to just after the jail match
    if jail_match:
        current_position = jail_match.end() - 1  # Subtract 1 to handle overlap
    
    # Step 2: Extract sequence number (search only for digits inside brackets)
    sequence_match = re.search(sequence_pattern, log_line[current_position:])
    sequence_number = sequence_match.group(1) if sequence_match else None
    
    # Update the current position to just after the sequence number match
    saved_current_position = current_position
    if sequence_match:
        current_position += sequence_match.end() - 1  # Subtract 1 to handle overlap
        saved_current_position = current_position + 3 # skips the :<space>
       
    # Step 3: Extract IP address (start search after sequence number)
    ip_match = re.search(ip_pattern, log_line[current_position:])
    ip_info = [None, None, None]

    if ip_match:
        current_position += ip_match.start()
        saved_current_position_ip = current_position

        ip_str = ip_match.group(1)
        try:
            # Validate if it's a valid IP (IPv4 or IPv6)
            ip_obj = ipaddress.ip_address(ip_str)
            ip_type = "ipv6" if isinstance(ip_obj, ipaddress.IPv6Address) else "ipv4"
            ip_info = [ip_type, ip_str, saved_current_position_ip]
        except ValueError:
            # Not a valid IP address
            ip_info = [None, None, None]

    return jail, sequence_number, ip_info, saved_current_position

def cut(string):
    # Regex pattern to match [a-z-_]+\[[0-9]+\[
    pattern = r"[a-z-_\.]+\[[0-9]+\]:\s"
    match = re.search(pattern, string)
    
    if match:
        # Get the end position of the match and return the substring from there
        return string[match.end():]
    else:
        # If no match, return the original string
        return string

# Function to delete temporary files created by the script
def clean_temp_files():
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)
    #print("Cleaned up temporary files.")

# Function to check if a jail is enabled by searching for 'enabled = true' or 'enabled = false'
import re

# Function to check if a jail is enabled by searching for 'enabled = true' or 'enabled = false'
def is_jail_enabled(dir_name):
    jail_conf_file = os.path.join(dir_name, 'jail.d', f'{dir_name}.conf')
    
    # Debug: print the file being tested
    # print(f"Testing file: {jail_conf_file}")
    
    if os.path.isfile(jail_conf_file):
        with open(jail_conf_file, 'r') as conf:
            for xline in conf:
                # Remove comments (anything after #) and strip leading/trailing whitespace
                xline.split('#', 1)[0].strip()
                
                # Debug: print the processed line after removing comments and trimming
                # print(f"Processed line: {line}")
                
                # Check for 'enabled = true' with flexible spaces/tabs using regex
                if re.match(r'.*enabled.*=.*true.*', line):
                    # print("Found 'enabled = true'. Stopping search.")
                    return True  # Stop searching and return True
                
                # Check for 'enabled = false' and stop if found
                elif re.match(r'.*enabled.*=.*false.*', line):
                    # print("Found 'enabled = false'. Stopping search.")
                    return False  # Stop searching and return False
                
    return False  # Default to False if no 'enabled = true' was found


# Note: Unused

# Function to process each line from journalctl
def process_journalctl_line(zline):
    # Write the line to the temporary file
    with open(temp_file.name, 'a') as tempf:
        tempf.write(zline)
    
    # Flag to track if a match was found

    # Iterate over each subdirectory and run fail3ban-regex
    for zdir in os.listdir('.'):
        if os.path.isdir(zdir):
            # Check if jail is enabled
            if is_jail_enabled(zdir):
                # Create a temporary file for fail3ban-regex output
                with tempfile.NamedTemporaryFile(delete=False, mode='w', prefix='fail3ban_', suffix='.log') as regex_temp_file:
                    regex_temp_file_path = regex_temp_file.name
                
                # Run fail3ban-regex and redirect the output to the temp file
                try:
                    subprocess.run(['fail3ban-regex', temp_file.name, zdir],
                                   stdout=open(regex_temp_file_path, 'w'),
                                   stderr=subprocess.STDOUT,
                                   check=True)
                    
                    # Check the regex temp file for success (0 ignored, 1 matched)
                    with open(regex_temp_file_path, 'r') as f:
                        regex_output = f.read()
                        if '0 ignored' in regex_output and '1 matched' in regex_output:
                            print(f"OK: {dir}")

                except subprocess.CalledProcessError:
                    pass  # Fail silently on failure (no output)

                finally:
                    # Cleanup: remove the regex output temp file
                    os.remove(regex_temp_file_path)
            #else:
                #print(f"Skipping {dir}: Jail is not enabled")
    
    # If no match was found, remain silent as per the request

# Start journalctl -f
journalctl_proc = subprocess.Popen(['journalctl', '-f'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# track one line behind so we can combine them if necessary
#previous_line = None

# use new PreviousJournalctl class
prevs = PreviousJournalctl()
# and our HashedSet class
hs = f3b_HashedSet.HashedSet()
# and our country codes class
cc = f3b_CountryCodes.CountryCodes()
# and our ShortenJournalString
sjs = f3b_ShortenJournalString.ShortenJournalString()
# and our database
db = f3b_sqlite3_db.SQLiteDB()
db.reset_hazard_level()
db.show_threats()
# and GlobalShutdown
gs = f3b_GlobalShutdown.GlobalShutdown()
# get rid of stale control flag
gs.cleanup()

# our whitelist
wl = f3b_whitelist.WhiteList()
wl.whitelist_init()

def save_pid(pid_file):
    pid = os.getpid()  # Get the current process ID (PID)
    
    # Save the PID to the specified file
    try:
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        print(f"PID {pid} saved to {pid_file}")
    except PermissionError:
        print(f"Permission denied: Unable to write to {pid_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def remove_pid(pid_file):
    # Check if the PID file exists
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)  # Remove the PID file
            print(f"PID file {pid_file} removed successfully.")
        except PermissionError:
            print(f"Permission denied: Unable to remove {pid_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"PID file {pid_file} does not exist.")

# Save our pid
pid_file = '/tmp/monitor_fail3ban.pid'
save_pid(pid_file)

#
# signaling
#

# Create a global event object to signaling threads to stop
stop_event = threading.Event()

def handle_signal(signum, frame):
    print("Received SIGHUP signal.")
    # Add custom handling here, like reloading configuration
    # sys.exit(0) # Uncomment if you want the program to exit on SIGHUP
    stop_event.set() # Set the event, signaling all threads to stop
    gs.request_shutdown()
    
# Register the signal handler for SIGTERM, SIGHUP, etc.
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGHUP, handle_signal)

try:
    while not stop_event.is_set() and not gs.is_shutdown():
        # Process each line from journalctl -f
        for line in journalctl_proc.stdout:
            # Clean up previous temporary files
            #clean_temp_files()

            # should we exit ???
            if gs.is_shutdown():
                # yes
                break

            # Now save on our previous entries list
            prevs.add_entry(line)

            # combine
            result = prevs.combine()
            if result is not None:
                result = result.strip()
            else:
                print("result can't be None")
                sys.exit(0)
                
            # is there an ip address in result ???
            found_dict, shortened_str = sjs.shorten_string(result)
            if 'ip_address' in found_dict:
                ip_address = found_dict['ip_address']
                # debgging info
                #logging.debug(f"ip_address found by shorten_string is {ip_address}")
            else:
                # debgging info
                #logging.debug(f"no ip_address found, skipping line")
                # we are done if there is not ip_address, on to the next line
                continue

            # get country and bad_dude_status
            country = None
            bad_dude_status = "n/a"
            if ip_address is not None:
                country = find_country(ip_address)
                # is this ip address in HashedSet
                if hs.is_ip_in_set(ip_address) :
                    # yep, a really bad dude
                    bad_dude_status = True
                else:
                    # nope, but a bad dude anyway
                    bad_dude_status = False

            #  is ip_address in our whitelist ???
            ip_address_in_whitelist = None
            if ip_address is not None:
                # check that this ip is not in the whitelist
                if wl.is_whitelisted(ip_address) is True:
                    ip_address_in_whitelist = True
                else:
                    ip_address_in_whitelist = False                    

            # check hazard level from table threat_table in database
            hazard_level = "unk"
            tmp_flag, tmp_hazard_level = db.fetch_threat_level(shortened_str)
            # was the record found in the database ???
            if tmp_flag is True:
                # yes
                hazard_level = tmp_hazard_level
            else:
                pass

            # format message to be displayed
            formatted_string = (
                f"Line      : {result if result is not None else 'n/a'}\n"
                f"Dictionary: {found_dict if found_dict is not None else 'n/a'}\n"
                f"Shortened : {shortened_str if shortened_str is not None else 'n/a'}\n"
                f"BadDude   : {True if bad_dude_status else 'False'}\n"            
                f"Country   : {country if country is not None else 'n/a'}"
                f"InWhiteLst: {ip_address_in_whitelist if ip_address_in_whitelist is not None else 'n/a'}"
                f"InDB      : In DB: {tmp_flag} Hazard Level: {hazard_level}"
            )
            # and display it
            print(formatted_string)
            print("-" * 50)
        
            if False:
                # if we are debugging,
                if logger.getEffectiveLevel() <= FLAG_DEBUG :
                    # at this point, we'd want to check with ChatGPT to ascertain the hazard_level level
                    # then add to our threat database
                    db.insert_or_update_threat(shortened_str, 1, hazard_level)

            # done processing this line
            continue
        else:
            continue
        
except KeyboardInterrupt:
    logging.error("Script interrupted. Exiting...")
finally:
    remove_pid(pid_file)
    # Cleanup: close the temporary file and delete it
    #if os.path.exists(temp_file.name):
    #    temp_file.close()
    #    os.remove(temp_file.name)
    #    logging.debug(f"Temporary file {temp_file.name} removed.")
