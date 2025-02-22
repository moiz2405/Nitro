import requests

API_URL = "http://127.0.0.1:5000/chat"

print("Welcome to the AI Assistant! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = requests.post(API_URL, json={"message": user_input}).json()
    print(f"Assistant: {response.get('response', 'Error')}")
