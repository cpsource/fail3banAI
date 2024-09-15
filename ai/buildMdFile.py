import openai
import os
import json
import argparse
import sys

#
# Note:
#
# This program uses ChatGPT to create a markdown document of python code
#
# Before you can run this, do the following from ~/
#
#  . openai/bin/activate
#  . OpenAI-My-Test-Key-Default-project.sh
#
# To run, do the following:
#
#  python3 buildMdFile.py <file-to-document> > <file-to-document>.md
#

class ChatWithOpenAI:
    def __init__(self, model="gpt-4o-2024-08-06"):
        """
        Initialize the chat class, retrieving the API key from the environment and setting the model.
        """
        self.api_key = os.getenv("OPENAI_API_DOC_PROJECT_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API_DOC_PROJECT_KEY key not found in environment variables.")
        openai.api_key = self.api_key
        self.model = model
        self.messages = []  # Store the conversation history

    def set_system(self, content):
        """
        Set the system message to define the assistant's behavior.
        """
        self.messages.append({"role": "system", "content": content})

    def user_message(self, content):
        """
        Add the user's message to the conversation.
        """
        self.messages.append({"role": "user", "content": content})

    def get_response(self):
        """
        Get the assistant's response from OpenAI, while maintaining context.
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            #print(f"response = {response}")
            assistant_message = response.choices[0].message.content
            #assistant_message = response['choices'][0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"

    def send_file(self, file_path):
        """
        Reads the contents of a file and sends it as a user message.
        Only works for text files; you can modify it for other types as needed.
        """
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."

        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()

            # Add the file contents as a user message
            self.user_message(f"Here is the content of the file '{file_path}':\n\n{file_contents}")
            return f"File '{file_path}' sent successfully."
        except Exception as e:
            return f"Error reading file: {str(e)}"
        
    def reset_conversation(self):
        """
        Clear the chat history.
        """
        self.messages = []

# Example usage
if __name__ == "__main__":
    # Set the OpenAI API key as an environment variable before running the script.
    # Example: export OPENAI_API_KEY="your-api-key-here"

    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Chat with OpenAI and send a file.')
    parser.add_argument('file_path', help='The path of the file to send to OpenAI.')

    # Parse the arguments
    args = parser.parse_args()

    # Check if the file_path is provided
    if not args.file_path:
        print("Error: No file provided.")
        sys.exit(1)

    # Create a chat instance
    chat = ChatWithOpenAI()

    # Set the assistant's behavior
    chat.set_system("Help document the attached python3 code.")

    # load a file into assistant
    chat.send_file(args.file_path)
    
    # User sends a message
    chat.user_message("Please document the attached python3 file in markdown format.")

    # Get the assistant's response
    response = chat.get_response()

    # write to a file
    infile = args.file_path
    # Strip off the extension from infile and use the base name + '.md' as the output filename
    base_name = os.path.splitext(infile)[0]  # This removes the extension
    output_filename = "README-" + base_name + ".md"  # Add the '.md' extension

    # Check if the output file already exists
    if os.path.exists(output_filename):
        print(f"Error: The file '{output_filename}' already exists.")
        sys.exit(1)  # Exit the program with an error code

    # Open the new file and write the output to it
    with open(output_filename, 'w') as outfile:
        # Create the content as a single string
        output_content = f"# {infile}\n{response}\n"
        # Write the content to the file
        outfile.write(output_content)

    print(f"Content successfully written to {output_filename}")

    #print(f"# {infile}\n{response}", infile, response)

