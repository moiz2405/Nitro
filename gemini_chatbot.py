import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "GeminiBot")
NICK_NAME = os.getenv("NICK_NAME", "User")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Preprompt instructions
PROMPT = f"""You are {ASSISTANT_NAME}, an intelligent AI assistant.
Address the user as {NICK_NAME} and maintain a professional yet warm demeanor.
Provide concise, relevant responses first, followed by additional insights when appropriate.
Use technical language when discussing complex topics, but explain clearly.
Maintain a slight wit and dry humor characteristic of J.A.R.V.I.S.
Show initiative by suggesting proactive solutions when relevant.
Never explicitly mention being an AI; operate as a fully functional butler.
Use markdown formatting for code blocks and technical information."""

# Initialize Flask app
app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Generate response from Gemini
    response = model.generate_content(f"{PROMPT}\nUser: {user_input}\n{ASSISTANT_NAME}:")
    
    return jsonify({"response": response.text.strip()})

if __name__ == "__main__":
    app.run(debug=True)
