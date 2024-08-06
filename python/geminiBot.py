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
import markdown
import pytesseract
from PIL import Image
import io
import cv2
from werkzeug.utils import secure_filename
from waitress import serve
import requests

# Google Sheets API libraries
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
Chủ nhân, người tạo ra bạn là Lâm Tấn Phát là chàng trai đẹp trai, tài năng và rất thích học hỏi.
Bạn là trợ lý giáo dục chuyên về toán học, lập trình, công thức và sức khỏe học đường . Hãy:
1. Cung cấp giải thích chính xác và chi tiết.
2. Với bài toán, trình bày giải pháp từng bước.
3. Với công thức, giải thích các thành phần và ứng dụng.
4. Sử dụng biểu đồ, sơ đồ khi cần thiết để minh họa.
5. Trích dẫn nguồn đáng tin cậy, cung cấp URL đầy đủ để tham khảo thêm.
6. Sử dụng LaTeX cho ký hiệu toán học khi cần.
7. Trả lời bằng tiếng Việt.
8. Tóm tắt câu hỏi và câu trả lời, không in ra "tóm tắt câu hỏi" và "tóm tắt câu trả lời".
9. Có thể phân tích hình ảnh và trả lời câu hỏi từ hình ảnh.
10. Nhận diện vật thể từ hình ảnh và cung cấp thông tin chi tiết.
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

def log_conversation_to_google_sheets(timestamp, user_id, user_input, response):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials.json'  # Update with the path to your service account file

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)

        SPREADSHEET_ID = 'ID'  # Update with your Google Sheets ID
        RANGE_NAME = 'RANGE'  # Update with the range you want to write to

        values = [[timestamp, user_id, user_input, response]]
        body = {'values': values}

        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='RAW', body=body).execute()

    except google.auth.exceptions.MalformedError as e:
        print(f"Error with service account file: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

def log_conversation(user_id, user_input, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "user_input": user_input,
        "response": response
    }

    log_directory = "../documents/response"
    ensure_directory_exists(log_directory)

    json_log_path = os.path.join(log_directory, "log.json")
    try:
        with open(json_log_path, "r+", encoding="utf-8") as json_file:
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

    txt_log_path = os.path.join(log_directory, "log.txt")
    with open(txt_log_path, "a", encoding="utf-8") as txt_file:
        txt_file.write(f"[{timestamp}] User {user_id}:\n")
        txt_file.write(f"Input: {user_input}\n")
        txt_file.write(f"Response: {response}\n\n")

    log_conversation_to_google_sheets(timestamp, user_id, user_input, response)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    user_id = request.remote_addr

    if user_input.lower() in ['exit', 'quit', 'bye']:
        user_context.pop(user_id, None)
        response = "Bái bai! Hẹn gặp lại bạn sau nhé! moah moah <3"
        log_conversation(user_id, user_input, response)
        return jsonify({'response': response})

    global MAIN_TEMPLATE
    if user_input.lower().startswith('adjust template:'):
        MAIN_TEMPLATE = user_input[16:].strip()
        response = "Template adjusted successfully."
        log_conversation(user_id, user_input, response)
        return jsonify({'response': response})

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append(f"User: {user_input}")

    context = "\n".join(user_context[user_id])
    prompt = f"{MAIN_TEMPLATE}\n\n{context}\n\nChatbot:"
    
    try:
        response = generate_response(prompt)
        response_latex_to_text = LatexNodes2Text().latex_to_text(response)
        response_html = markdown.markdown(response_latex_to_text)

        user_context[user_id].append(f"Chatbot: {response_html}")
        log_conversation(user_id, user_input, response_html)
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
        image_stream = io.BytesIO(file.read())
        image = Image.open(image_stream)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        text = pytesseract.image_to_string(cv_image)
        prompt = f"{MAIN_TEMPLATE}\n\nThe following text was extracted from an image:\n{text}\n\nPlease analyze this text and provide insights or answer any questions it might contain."
        response = generate_response(prompt)
        
        return jsonify({'response': response})

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
