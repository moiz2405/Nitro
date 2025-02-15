import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and other variables
api_key = os.getenv("GEMINI_API_KEY")
nickname = os.getenv("NickName")
assistant_name = os.getenv("AssistantName")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing. Please set it in the .env file.")

print(f"Loaded API key for {assistant_name}, assisting {nickname}.")
