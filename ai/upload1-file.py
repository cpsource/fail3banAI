import openai
import os
import argparse
import sys

class ChatWithOpenAI:
    def __init__(self, model="gpt-4"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        openai.api_key = self.api_key
        self.model = model
        self.messages = []

    def set_system(self, content):
        self.messages.append({"role": "system", "content": content})

    def user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def get_response(self):
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
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."

        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()

            self.user_message(f"Here is the content of the file '{file_path}':\n\n{file_contents}")
            return f"File '{file_path}' sent successfully."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def upload_file_for_finetuning(self, file_path, purpose='fine-tune'):
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

    def create_fine_tuning_job(self, file_id, model="davinci"):
        try:
            response = openai.FineTune.create(
                training_file=file_id,
                model=model
            )
            return response
        except Exception as e:
            return f"Error creating fine-tuning job: {str(e)}"

    def get_fine_tuning_status(self, finetune_id):
        try:
            response = openai.FineTune.retrieve(id=finetune_id)
            return response
        except Exception as e:
            return f"Error retrieving fine-tuning status: {str(e)}"

    def get_finetuned_response(self, prompt, finetuned_model):
        try:
            response = openai.Completion.create(
                model=finetuned_model,
                prompt=prompt,
                max_tokens=150
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error getting fine-tuned response: {str(e)}"

    def generate_embeddings_from_file(self, file_path, model="text-embedding-ada-002"):
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."
        
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            embeddings = []
            for line in lines:
                line = line.strip()
                if line:
                    response = openai.Embedding.create(
                        input=line,
                        model=model
                    )
                    embeddings.append({
                        "input": line,
                        "embedding": response['data'][0]['embedding']
                    })
            
            return embeddings
        except Exception as e:
            return f"Error generating embeddings: {str(e)}"

    def reset_conversation(self):
        self.messages = []

# Main function that handles command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Chat with OpenAI, send a file, upload for fine-tuning/embeddings.')
    parser.add_argument('--send-file', help='The path of the file to send to OpenAI as a chat message.')
    parser.add_argument('--upload-file', help='The path of the file to upload to OpenAI for fine-tuning or embeddings.')
    parser.add_argument('--create-finetune', action='store_true', help='Create a fine-tuning job using the uploaded file.')
    parser.add_argument('--generate-embeddings', action='store_true', help='Generate embeddings from the uploaded file.')
    parser.add_argument('--model', default='davinci', help='Base model to fine-tune.')
    parser.add_argument('--embedding-model', default='text-embedding-ada-002', help='Model to use for generating embeddings.')
    
    args = parser.parse_args()

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
        # Upload the file
        upload_response = chat.upload_file_for_finetuning(args.upload_file, purpose='fine-tune' if args.create_finetune else 'embeddings')
        print("Upload Response:", upload_response)
        
        if isinstance(upload_response, dict) and 'id' in upload_response:
            file_id = upload_response['id']
        else:
            print("Failed to upload file.")
            sys.exit(1)
        
        # Create a fine-tuning job if requested
        if args.create_finetune:
            finetune_response = chat.create_fine_tuning_job(file_id, model=args.model)
            print("Fine-Tuning Job Response:", finetune_response)
        
        # Generate embeddings if requested
        if args.generate_embeddings:
            embeddings = chat.generate_embeddings_from_file(args.upload_file, model=args.embedding_model)
            print("Embeddings:", embeddings)

if __name__ == "__main__":
    main()

