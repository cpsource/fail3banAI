import re

jail = "ssh.d"  # Contains a dot (.)
escaped_jail = re.escape(jail)  # Escapes special characters
print(escaped_jail)  # Output: 'ssh\.d'

