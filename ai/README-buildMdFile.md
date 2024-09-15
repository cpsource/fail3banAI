# ./buildMdFile.py

## Prerequisites

Before running the script, ensure you have:

1. Activated your Python virtual environment.
2. Set up the OpenAI API key in your environment. This can be done by running the following commands in your terminal from the home directory (`~/`):

    ```shell
    . openai/bin/activate
    . OpenAI-My-Test-Key-Default-project.sh
    ```

## Usage

Run the script as follows:

```shell
python3 buildMdFile.py <file-to-document>
```

The output will be a markdown file with the same name as the input file but with a `.md` extension.

## Script Structure

### `ChatWithOpenAI` Class

- **Initialization**: Retrieves the API key from environment variables and sets the model to communicate with (defaults to "gpt-4o-2024-08-06").

- **Methods**:
  - `set_system(content)`: Sets a system message to establish behavior rules for the assistant.
  - `user_message(content)`: Sends a user message to the assistant.
  - `get_response()`: Retrieves the assistant's response based on the conversation history.
  - `send_file(file_path)`: Reads a file's content and sends it to the assistant as a user message.
  - `reset_conversation()`: Clears the stored conversation history.

### Main Execution

- **Argument Parsing**: Command-line arguments are handled to specify the file path to the Python script that needs documentation.

- **Process**:
  1. Initializes a `ChatWithOpenAI` instance.
  2. Sets the assistant's behavior for documenting code.
  3. Loads the specified file into the assistant.
  4. Requests documentation in markdown format.
  5. Checks for filename conflicts with the output markdown file.
  6. Writes the generated documentation to a new markdown file, naming it after the input file with a `.md` extension.

- **Output**: The documentation is saved with a message indicating completion. Errors during file operations or if the API key is not set will halt execution with a message.

## Error Handling

The script includes error handling for:

- Missing OpenAI API key in environment variables.
- Non-existent input files.
- Pre-existing output markdown files.
