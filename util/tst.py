import os
from dotenv import dotenv_values

# load dotenv - contains ChatGPT Keys
#p = os.getenv('FAIL3BAN_PROJECT_ROOT')
#print(p)

dotenv_config = dotenv_values(f"{os.getenv('FAIL3BAN_PROJECT_ROOT')}/.env")
# display
try:
    # Attempt to print the value of the key
    key = dotenv_config["OPENAI_DEFAULT_PROJECT_ID"]
    print(key)
except KeyError:
    # Handle the case where the key doesn't exist
    print("Key 'OPENAI_DEFAULT_PROJECT_ID' not found in dotenv_config.")

