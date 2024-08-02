import re
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import google.generativeai as genai
import nltk
from rake_nltk import Rake
import base64
from latex_to_text import latex_to_text
from format_text import format_response, split_text_into_sentences, format_text
from searching import web_search
import json
import os
from datetime import datetime
# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Rake
r = Rake()

# Configure the Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Set up Gemini API
genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-pro')

# Initialize the main template
MAIN_TEMPLATE = """You are an educational assistant specializing in mathematics, coding, and formulas. 
Please provide accurate and detailed explanations for questions related to these topics. 
For math problems, show step-by-step solutions. 
For coding questions, provide explanations and example code snippets when appropriate, when providing code snippets, please wrap them in triple backticks (```) and specify the language.. 
For formulas, explain their components and applications. 
Use LaTeX for mathematical notation when necessary.
"""

# Dictionary to store user context
user_context = {}


def format_code_blocks(text):
    """
    Format code blocks by wrapping them in <pre><code> tags and applying syntax highlighting.
    """

    def replace_code_block(match):
        language = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{language}">{code}</code></pre>'

    # Replace code blocks
    text = re.sub(r'```(\w+)?\n(.*?)\n```', replace_code_block, text, flags=re.DOTALL)
    return text


def generate_response(prompt):
    response = model.generate_content(prompt).text
    return format_code_blocks(response)

# Add these functions for logging
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def log_conversation(user_id, user_input, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "user_input": user_input,
        "response": response
    }

    # Ensure the directory exists
    log_directory = "../documents/response"
    ensure_directory_exists(log_directory)

    # Log to JSON file
    json_log_path = os.path.join(log_directory, "log.json")
    try:
        with open(json_log_path, "r+" ,encoding="utf-8") as json_file:
            try:
                logs = json.load(json_file)
            except json.JSONDecodeError:
                logs = []
            logs.append(log_entry)
            json_file.seek(0)
            json.dump(logs, json_file, indent=2)
    except FileNotFoundError:
        with open(json_log_path, "w", encoding="utf-8") as json_file:
            json.dump([log_entry], json_file, indent=2)

    # Log to text file
    txt_log_path = os.path.join(log_directory, "log.txt")
    with open(txt_log_path, "a", encoding="utf-8") as txt_file:
        txt_file.write(f"[{timestamp}] User {user_id}:\n")
        txt_file.write(f"Input: {user_input}\n")
        txt_file.write(f"Response: {response}\n\n")

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    user_id = request.remote_addr  # Use user's IP address as a unique identifier

    if user_input.lower() in ['exit', 'quit', 'bye']:
        user_context.pop(user_id, None)  # Clear context for the user
        response = "Bái bai! Hẹn gặp lại bạn sau nhé! moah moah <3"
        log_conversation(user_id, user_input, response)
        return jsonify({'response': response})

    global MAIN_TEMPLATE
    if user_input.lower().startswith('adjust template:'):
        MAIN_TEMPLATE = user_input[16:].strip()
        response = "Template adjusted successfully."
        log_conversation(user_id, user_input, response)
        return jsonify({'response': response})

    # Initialize context for the user if not already present
    if user_id not in user_context:
        user_context[user_id] = []

    user_input_cleaned = user_input.replace('"', '').replace('**', '')
    r.extract_keywords_from_sentences([user_input_cleaned])
    sum_input = r.get_ranked_phrases()
    if not sum_input:
        return jsonify({'response': "Sorry, I couldn't understand your input. Please try again."})

    query = ' '.join(sum_input)
    web_result = web_search(query)

    # Append user input to the context
    user_context[user_id].append(f"User: {user_input}")

    # Create the prompt with context
    context = "\n".join(user_context[user_id])
    prompt = f"{MAIN_TEMPLATE}\n\n{context}\n\nRelevant information from web: {web_result}\n\nChatbot:" if web_result else f"{MAIN_TEMPLATE}\n\n{context}\n\nChatbot:"

    response = generate_response(prompt)
    response_cleaned = format_response(response)
    response_latex_to_text = latex_to_text(format_text(response_cleaned))

    # Append chatbot response to the context
    user_context[user_id].append(f"Chatbot: {response_latex_to_text}")
    # Log the conversation
    log_conversation(user_id, user_input, response_latex_to_text)
    print(f"User: {query}\n\nChatbot: {response_latex_to_text}\n")
    return jsonify({'response': response_latex_to_text})


if __name__ == '__main__':
    app.run(debug=True)