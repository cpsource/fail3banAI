import os
import subprocess

class Foo:
    def __init__(self):
        self.commands = {
            "show-activity_table": self.show_activity_table
        }

    def show_activity_table(self, filter_arg=None):
        """Run the ManageBanActivityDatabase.py show command with an optional filter argument."""
        try:
            # Prepare the command
            command = 'FAIL3BAN_PROJECT_ROOT/util/ManageBanActivityDatabase.py show'
            
            # If there's a filter argument (e.g., to pipe output to grep), add it
            if filter_arg:
                command += f' | grep {filter_arg}'

            env = os.environ.copy()  # Copy the current environment
            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)

            if result.returncode == 0:
                print(result.stdout)  # Normally, you'd send this to the client socket
            else:
                error_message = f"Error running command: {result.stderr}\n"
                print(error_message)

        except Exception as e:
            error_message = f"Exception occurred: {e}\n"
            print(error_message)

    def dispatch_command(self, command):
        """Dispatch command to the appropriate handler with optional arguments."""
        parts = command.split()

        # Extract the main command and any optional argument
        main_command = parts[0]
        optional_arg = parts[1] if len(parts) > 1 else None

        if main_command in self.commands:
            if main_command == 'show-activity_table':
                self.commands[main_command](optional_arg)  # Pass the optional argument
            else:
                self.commands[main_command]()  # No arguments for other commands
        else:
            print("Unknown command. Type 'help' for a list of commands.\n")

# Example usage of the class
foo = Foo()
foo.dispatch_command('show-activity_table ABC')  # Example of command with an argument
