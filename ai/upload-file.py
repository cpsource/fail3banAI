import openai
import os
import argparse
import sys

class ChatWithOpenAI:
    def __init__(self, model="gpt-4"):
        """
        Initialize the chat class, retrieving the API key from the environment and setting the model.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
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
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages
            )
            assistant_message = response['choices'][0]['message']['content']
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

    def upload_file_for_finetuning(self, file_path, purpose='fine-tune'):
        """
        Upload a file to OpenAI for fine-tuning or other purposes.
        """
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."

        try:
            with open(file_path, 'rb') as file:
                response = openai.File.create(
                    file=file,
                    purpose=purpose
                )
            return response
        except Exception as e:
            return f"Error uploading file: {str(e)}"

    def upload_file_for_embeddings(self, file_path, purpose='embeddings'):
        """
        Upload a file to OpenAI for generating embeddings.
        """
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."

        try:
            with open(file_path, 'rb') as file:
                response = openai.File.create(
                    file=file,
                    purpose=purpose
                )
            return response
        except Exception as e:
            return f"Error uploading file: {str(e)}"

    def reset_conversation(self):
        """
        Clear the chat history.
        """
        self.messages = []

# Main function that handles command-line arguments
def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Chat with OpenAI, send a file, or upload a file for fine-tuning/embeddings.')
    parser.add_argument('--send-file', help='The path of the file to send to OpenAI as a chat message.')
    parser.add_argument('--upload-file', help='The path of the file to upload to OpenAI for fine-tuning or embeddings.')
    parser.add_argument('--purpose', default='fine-tune', choices=['fine-tune', 'embeddings', 'search'], help='Purpose of the file upload.')

    # Parse the arguments
    args = parser.parse_args()

    # Create a chat instance
    try:
        chat = ChatWithOpenAI()
    except ValueError as ve:
        print(str(ve))
        sys.exit(1)

    # Set the assistant's behavior
    chat.set_system("You are a helpful assistant.")

    # User sends an initial message
    chat.user_message("Hello! How are you?")
    print("Assistant:", chat.get_response())

    # Handle sending a file as a chat message
    if args.send_file:
        send_result = chat.send_file(args.send_file)
        print(send_result)
        print("Assistant:", chat.get_response())

    # Handle uploading a file for fine-tuning or embeddings
    if args.upload_file:
        if args.purpose == 'fine-tune':
            upload_response = chat.upload_file_for_finetuning(args.upload_file, purpose=args.purpose)
        elif args.purpose == 'embeddings':
            upload_response = chat.upload_file_for_embeddings(args.upload_file, purpose=args.purpose)
        else:
            upload_response = f"Purpose '{args.purpose}' is not supported."
        
        print("Upload Response:", upload_response)

if __name__ == "__main__":
    main()

