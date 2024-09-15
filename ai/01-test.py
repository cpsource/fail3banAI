import openai

openai.api_key = 'your-api-key-here'

response = openai.chat_completion(
    model='01-mini',
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)

