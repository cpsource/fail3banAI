#!/usr/bin/env python3

import os
#import subprocess
import tempfile
#import re
import ipaddress
import sys

# Configure logging
import logging

# Extracted constants for log file name and format
LOG_FILE_NAME = "monitor_fail2ban.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
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
logger = logging.getLogger("fail3ban")

#
# Load our foundation classes
#
# Get the absolute path of the current directory (the directory containing this script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the subdirectory to the system path
subdirectory_path = os.path.join(current_dir, 'lib')
sys.path.append(subdirectory_path)

import previousJournalctl

#
# Here's a double line that needs to be combined
# into one line, so we can process it effectively.
# I suggest we keep track of the previous line and
# combine them if the [digits] and [jail] are the same.
#

#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: error: kex_exchange_identification: Connection closed by remote host
#Journalctl line: Sep 13 12:46:37 ip-172-26-10-222 sshd[172070]: Connection closed by 104.152.52.121 port 51587

# Path to the temporary file in /tmp
temp_file = tempfile.NamedTemporaryFile(delete=False, dir='/tmp', mode='w', prefix='journal_', suffix='.log')

import subprocess
#import f3b_blacklist
#import re

# country codes
country_code_to_country_name = {
    "AF": "Afghanistan",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BR": "Brazil",
    "BN": "Brunei",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "CV": "Cabo Verde",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CO": "Colombia",
    "KM": "Comoros",
    "CD": "Congo (Democratic Republic)",
    "CG": "Congo (Republic)",
    "CR": "Costa Rica",
    "CI": "Côte d'Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "SZ": "Eswatini",
    "ET": "Ethiopia",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GR": "Greece",
    "GD": "Grenada",
    "GU": "Guam",
    "GT": "Guatemala",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (North)",
    "KR": "Korea (South)",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Laos",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macau",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "MX": "Mexico",
    "FM": "Micronesia",
    "MD": "Moldova",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PL": "Poland",
    "PT": "Portugal",
    "QA": "Qatar",
    "RO": "Romania",
    "RU": "Russia",
    "RW": "Rwanda",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syria",
    "TW": "Taiwan",
    "TJ": "Tajikistan",
    "TZ": "Tanzania",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States of America",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Vietnam",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe"
}


def find_country(ip_address_string):
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
            cc = match.group(1).strip()
            country = country_code_to_country_name.get(cc,cc)
            return country
        else:
            # Return None if no country line is found
            return None
    except Exception as e:
        print(f"Error: {e}")
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

def combine(prev_str, cur_str):
    """
    :param prev_str: The previous string to be combined.
    :param cur_str: The current string from which a portion will be extracted and combined with prev_str.
    :return: A new string which is a combination of prev_str and a portion of cur_str starting from the found index.
    """
    idx = cur_str.find(']: ')
    combined_str = prev_str + " " + cut(cur_str[idx+3:])
    return combined_str

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


# Function to process each line from journalctl
def process_journalctl_line(zline):
    # Write the line to the temporary file
    with open(temp_file.name, 'a') as tempf:
        tempf.write(zline)
    
    # Flag to track if a match was found

    # Iterate over each subdirectory and run fail2ban-regex
    for zdir in os.listdir('.'):
        if os.path.isdir(zdir):
            # Check if jail is enabled
            if is_jail_enabled(zdir):
                # Create a temporary file for fail2ban-regex output
                with tempfile.NamedTemporaryFile(delete=False, mode='w', prefix='fail2ban_', suffix='.log') as regex_temp_file:
                    regex_temp_file_path = regex_temp_file.name
                
                # Run fail2ban-regex and redirect the output to the temp file
                try:
                    subprocess.run(['fail2ban-regex', temp_file.name, zdir],
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
prevs = previousJournalctl.PreviousJournalctl()

try:
    # Process each line from journalctl -f
    for line in journalctl_proc.stdout:
        # Clean up previous temporary files
        clean_temp_files()

        # Now save
        prevs.add_entry(line)

        # Now, call prev_entry and check if it returns the correct match
        result = prevs.prev_entry()

        country_code = None
        tmp_ip_address = prevs.get_top_ip_address()
        if tmp_ip_address is not None:
            country_code = find_country(tmp_ip_address)
        
        if country_code is not None:
            # Print the journalctl line before processing
            logging.info(f"CC: {country_code} : {line.strip()}")
        else:
            # Print the journalctl line before processing
            logging.info(f"CC: n/a : {line.strip()}")
        
        # Was there a match ???
        if result[0]:
            logging.debug(f"Match found: {result[1]}")
            res = combine(result[1][3], line)
            if res is not None:
                # print the new line
                logging.info(f"*** Combined line: {res.strip()}")
            else:
                logging.error("could not combine lines")
        
except KeyboardInterrupt:
    logging.error("Script interrupted. Exiting...")
finally:
    # Cleanup: close the temporary file and delete it
    if os.path.exists(temp_file.name):
        temp_file.close()
        os.remove(temp_file.name)
        logging.debug(f"Temporary file {temp_file.name} removed.")
