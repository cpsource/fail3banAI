import os
import sys
from openai import OpenAI
import json

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)

#
# The object you are receiving is a custom Python object returned by the OpenAI Python library.
# Specifically, it's an instance of a class provided by the openai library, which represents the
# response from the API.
#

print(response)
#sys.exit(0)

#
# typical return
#ChatCompletion(
#              id='chatcmpl-A9SZ7jePvoBjZ7wxlCKuEn7agM6cw',
#              choices=[Choice(finish_reason='stop',
#                              index=0,
#                              logprobs=None,
#                              message=ChatCompletionMessage(
#                                                            content='This is a test.',
#                                                            refusal=None,
#                                                            role='assistant',
#                                                            function_call=None,
#                                                            tool_calls=None
#                                                           )
#                             )
#                       ],
#              created=1726818121,
#              model='gpt-4o-2024-05-13',
#              object='chat.completion',
#              service_tier=None,
#              system_fingerprint='fp_52a7f40b0b',
#              usage=CompletionUsage(completion_tokens=5,
#                                    prompt_tokens=12,
#                                    total_tokens=17,
#                                    completion_tokens_details={'reasoning_tokens': 0}
#                                   )
#             )

# Print the response from the API
response_message = response.choices[0].message.content

#
# examine response
#

# Assuming `response` is the object returned from the API
print(f"type(response) = {type(response)}")  # Shows the type of the response object
print(f"dir(response) = {dir(response)}")   # Shows the attributes and methods of the response object

# For example, you can inspect the type of `response.choices[0]`
print(f"type(response.choices[0] = {type(response.choices[0])}")  # Will show the type, likely `Choice`

# You can also inspect individual attributes
print(f"type(response.choices[0].message = {type(response.choices[0].message)}")  # Should be `ChatCompletionMessage`

# print the extracted content
print("Message Content:", response_message)
