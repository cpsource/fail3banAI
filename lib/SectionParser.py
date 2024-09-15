class SectionParser:
    def __init__(self, filename):
        self.filename = filename
        self.sections = {}

    def parse_file(self):
        current_section = None

        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    # Strip whitespace from the line
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Check if the line starts with a section in square brackets
                    if line.startswith('[') and line.endswith(']'):
                        # Set the current section
                        current_section = line[1:-1]  # Extract section name
                        self.sections[current_section] = []  # Initialize section with an empty list
                    elif current_section:
                        # Add data to the current section
                        self.sections[current_section].append(line)
        except FileNotFoundError:
            print(f"Error: {self.filename} file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_section(self, section_name):
        # Return the data for the requested section, or None if not found
        return self.sections.get(section_name, None)

    def get_all_sections(self):
        # Return the entire sections dictionary
        return self.sections

# Example usage
if __name__ == "__main__":
    parser = SectionParser('example_file.txt')
    parser.parse_file()

    # Print all sections and their data
    all_sections = parser.get_all_sections()
    for section, data in all_sections.items():
        print(f"Section: {section}")
        for line in data:
            print(f"  {line}")

    # Retrieve and print a specific section
    section_name = 'abc'
    section_data = parser.get_section(section_name)
    if section_data:
        print(f"\nData for section [{section_name}]:")
        for line in section_data:
            print(f"  {line}")
    else:
        print(f"Section [{section_name}] not found.")

