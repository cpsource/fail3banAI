import os

class BadGets:
    def __init__(self, filepath=None):

        # if this goes to zero, check the filepath for change
        self.reload_counter = 10

        self.filepath = filepath
        # If no filepath is provided, use the default
        if self.filepath is None:
            self.filepath = os.getenv("FAIL3BAN_PROJECT_ROOT") + "/control/BadGets.ctl"
            
        print(f"filepath: {self.filepath}")

        self.bad_gets = set()  # Initialize as an empty set for fast membership checks

        # Save initial file attributes
        self.last_modified_time = None
        self.file_size = None
        self.save_file_attributes()

        # Load the contents of the file
        self.read_bad_gets_file()

    def save_file_attributes(self):
        """Save the file's size and modification time."""

        print(f"filepath = {self.filepath}")
        
        try:
            self.last_modified_time = os.path.getmtime(self.filepath)
            self.file_size = os.path.getsize(self.filepath)
        except FileNotFoundError:
            print(f"File {self.filepath} not found.")

    def read_bad_gets_file(self):
        """Read the BadGets.ctl file and store non-commented lines in self.bad_gets."""
        try:
            with open(self.filepath, 'r') as file:
                # Read lines, filter out comments (lines starting with #), and add to the set
                valid_lines = {line.strip() for line in file if not line.strip().startswith('#')}
                self.bad_gets = valid_lines

            # After successful read, save file attributes again
            self.save_file_attributes()

        except FileNotFoundError:
            print(f"File {self.filepath} not found.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")

    def _bad_gets_changed(self):
        """Check if the BadGets.ctl file has changed (size or modification time)."""
        try:
            current_modified_time = os.path.getmtime(self.filepath)
            current_file_size = os.path.getsize(self.filepath)

            if (current_modified_time != self.last_modified_time or
                current_file_size != self.file_size):
                print("File has changed, reloading...")
                self.read_bad_gets_file()
                return True
            return False
        except FileNotFoundError:
            print(f"File {self.filepath} not found.")
            return False
        
    def is_bad_get(self, input_string):
        """Return True if input_string contains ../../ or is in the bad_gets set."""

        # do we reload the file? If so, do so
        self.reload_counter -= 1
        if self.reload_counter <= 0:
            self.reload_counter = 10
            if self._bad_gets_changed():
                self.read_bad_gets_file()

        # special case testing
        if "../../" in input_string:
            return True

        # else look in the set
        return input_string in self.bad_gets
    
if __name__ == "__main__":
    # Initialize the class with the control file
    bad_gets_instance = BadGets()

    # Test input strings
    test_strings = [
        "/ecp/Current/exporttool/microsoft.exchange.ediscovery.exporttool.application",
        "/geoserver/web/",
        "/guacamole",
        "/index.php?lang=../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?echo(md5(\"hi\"));?>+/tmp/index1.//i",
        "/foobar",
    ]

    # Loop over the test strings and check if they are "bad GETs"
    for input_string in test_strings:
        result = bad_gets_instance.is_bad_get(input_string)
        print(f"Input: {input_string}\nIs Bad Get: {result}\n")
