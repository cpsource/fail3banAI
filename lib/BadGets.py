import os
import logging

logger = logging.getLogger("fail3ban")

class BadGets:
    def __init__(self, filepath=None):
        # if this goes to zero, check the filepath for change
        self.reload_counter = 10

        self.filepath = filepath
        # If no filepath is provided, use the default
        if self.filepath is None:
            self.filepath = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/BadGets.ctl"
            
        logger.debug(f"filepath: {self.filepath}")

        self.bad_gets = ()  # Initialize as an empty tuple for membership checks

        # Save initial file attributes
        self.last_modified_time = None
        self.file_size = None
        self.save_file_attributes()

        # Load the contents of the file
        self.read_bad_gets_file()

    def save_file_attributes(self):
        """Save the file's size and modification time."""
        #logger.debug(f"filepath = {self.filepath}")
        
        try:
            self.last_modified_time = os.path.getmtime(self.filepath)
            self.file_size = os.path.getsize(self.filepath)
        except FileNotFoundError:
            logger.error(f"File {self.filepath} not found.")

    def read_bad_gets_file(self):
        """Read the BadGets.ctl file and store non-commented lines in self.bad_gets."""
        try:
            with open(self.filepath, 'r') as file:
                # Read lines, filter out comments (lines starting with #), and add to the tuple
                valid_lines = tuple(line.strip() for line in file if not line.strip().startswith('#'))
                self.bad_gets = valid_lines

            # After successful read, save file attributes again
            self.save_file_attributes()

        except FileNotFoundError:
            logger.error(f"File {self.filepath} not found.")
        except Exception as e:
            logger.error(f"An error occurred while reading the file: {e}")

    def _bad_gets_changed(self):
        """Check if the BadGets.ctl file has changed (size or modification time)."""
        try:
            current_modified_time = os.path.getmtime(self.filepath)
            current_file_size = os.path.getsize(self.filepath)

            if (current_modified_time != self.last_modified_time or
                current_file_size != self.file_size):
                logger.debug("File has changed, reloading...")
                self.read_bad_gets_file()
                return True
            return False
        except FileNotFoundError:
            logger.debug(f"File {self.filepath} not found.")
            return False
        
    def is_bad_get(self, input_string):
        """Return True if input_string contains ../../ or / or matches a bad_get in self.bad_gets."""

        #print(f"{self.bad_gets}")
        
        input_string = input_string.strip()
        
        # Reload the file if necessary
        self.reload_counter -= 1
        if self.reload_counter <= 0:
            self.reload_counter = 10
            if self._bad_gets_changed():
                self.read_bad_gets_file()

        # Get rid of // in input_string
        if input_string[:2] == '//':
            input_string = input_string[1:]
            
        # special case for "/"
        if input_string == '/':
            return False
        
        # Special case for "../../"
        if "../../" in input_string:
            return True

        # Check each entry in the bad_gets tuple by comparing the part of input_string
        # with the same length as the bad_get entry.
        idx = 0
        for bad_get in self.bad_gets:
            idx += 1
            if len(bad_get) == 0:
                continue
            if input_string[:len(bad_get)] == bad_get:
                #print(f"match: idx = {idx}, {bad_get}, {type(bad_get)}")
                #print(f"{self.bad_gets}")
                return True
        return False
    
if __name__ == "__main__":
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

    # Initialize the class with the control file
    bad_gets_instance = BadGets()

    # Test input strings
    test_strings = [
        "/ecp/Current/exporttool/microsoft.exchange.ediscovery.exporttool.application",
        "/geoserver/web/",
        "/guacamole",
        "/index.php?lang=../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?echo(md5(\"hi\"));?>+/tmp/index1.//i",
        "/foobar",
        "/favicon.ico",
        "/xmlrpc.php",
    ]

    # Loop over the test strings and check if they are "bad GETs"
    for input_string in test_strings:
        result = bad_gets_instance.is_bad_get(input_string)
        print(f"Input: {input_string}\nIs Bad Get: {result}\n")

