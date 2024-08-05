# python/geminiBot.py

from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import google.generativeai as genai
import nltk
from rake_nltk import Rake
import base64
from pylatexenc.latex2text import LatexNodes2Text
import json
import os
import numpy as np
from datetime import datetime
import markdown  # Import markdown module for converting Markdown to HTML
import pytesseract
from PIL import Image
import io
import cv2
from werkzeug.utils import secure_filename

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Rake
r = Rake()

# Configure the Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Set up Gemini API
genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-1.5-pro')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the main template
MAIN_TEMPLATE = """
Bạn là trợ lý giáo dục chuyên về toán học, lập trình và công thức. Hãy:
1. Cung cấp giải thích chính xác và chi tiết.
2. Với bài toán, trình bày giải pháp từng bước.
3. Với công thức, giải thích các thành phần và ứng dụng.
4. Sử dụng biểu đồ, sơ đồ khi cần thiết để minh họa.
5. Trích dẫn nguồn đáng tin cậy, cung cấp URL đầy đủ để tham khảo thêm.
6. Sử dụng LaTeX cho ký hiệu toán học khi cần.
7. Trả lời bằng tiếng Việt.
8. Tóm tắt câu hỏi và câu trả lời, không in ra "tóm tắt câu hỏi" và "tóm tắt câu trả lời".
Hãy trả lời ngắn gọn nhưng đầy đủ. Nếu cần thêm thông tin, hãy hỏi người dùng.
"""

# Dictionary to store user context
user_context = {}

def generate_response(prompt):
    response = model.generate_content(prompt).text
    return response

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

    # Append user input to the context
    user_context[user_id].append(f"User: {user_input}")

    # Create the prompt with context
    context = "\n".join(user_context[user_id])
    prompt = f"{MAIN_TEMPLATE}\n\n{context}\n\nChatbot:"
    
    try:
        # Generate response from the model
        response = generate_response(prompt)
        response_latex_to_text = LatexNodes2Text().latex_to_text(response)
        # Escape special characters in the response
        # response_escaped = html.escape(response_latex_to_text)                
        # Convert Markdown to HTML
        response_html = markdown.markdown(response_latex_to_text)

        # Append chatbot response to the context
        user_context[user_id].append(f"Chatbot: {response_html}")
        # Log the conversation
        log_conversation(user_id, user_input, response_html)
        print("user", user_input)
        print("response", response_html)
        return jsonify({'response': response_html})
    except Exception as e:
        error_message = "An error occurred while processing your request. Please try again."
        log_conversation(user_id, user_input, error_message)
        return jsonify({'response': error_message})
    
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'response': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'response': 'No file selected for uploading'}), 400
    
    if file:
        # Read the image file
        image_stream = io.BytesIO(file.read())
        image = Image.open(image_stream)
        
        # Convert the image to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Perform OCR
        text = pytesseract.image_to_string(cv_image)
        
        # Generate a response using the OCR text
        prompt = f"{MAIN_TEMPLATE}\n\nThe following text was extracted from an image:\n{text}\n\nPlease analyze this text and provide insights or answer any questions it might contain."
        response = generate_response(prompt)
        
        return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
