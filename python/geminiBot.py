import re
import requests
from flask import Flask, render_template, request, jsonify
from functools import lru_cache
from bs4 import BeautifulSoup
import google.generativeai as genai
import nltk
from rake_nltk import Rake
from sympy import latex, sympify, SympifyError
import matplotlib.pyplot as plt
import io
import base64

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Rake
r = Rake()

# Configure the Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Set up Gemini API
genai.configure(api_key='AIzaSyABvqN-8d3jpqlOeE1HzSK07LcW-R1B0Ss')
model = genai.GenerativeModel('gemini-pro')

# Initialize the main template
MAIN_TEMPLATE = "You are a helpful assistant. Please provide accurate and authentic responses to user requests."

@lru_cache(maxsize=100)
def search_file(query):
    try:
        with open('../documents/response/find.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        query_lower = query.lower()
        content_lower = content.lower()
        index = content_lower.find(query_lower)
        return content[index:index + 200] if index != -1 else None
    except UnicodeDecodeError:
        print("Error: Unable to read the file. It may contain characters that are not UTF-8 encoded.")
        return None

def write_to_file(response):
    with open('../documents/response/find.txt', 'a', encoding='utf-8') as file:
        file.write(f"{response}\n\n")

@lru_cache(maxsize=50)
def web_search(query):
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='g')
    return results[0].get_text() if results else None

def generate_response(prompt):
    return model.generate_content(prompt).text

def format_response(response):
    response = response.replace('"', '').replace('**', '')
    lines = response.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('*'):
            formatted_lines.append('\n' + line)
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def generate_math_image(formula):
    try:
        sympy_expr = sympify(formula)
        latex_str = latex(sympy_expr)
        
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"${latex_str}$", fontsize=20, ha='center', va='center')
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return f'<img src="data:image/png;base64,{img_base64}"/>'
    except (SympifyError, SyntaxError):
        return "Invalid mathematical expression. Please provide a correct formula."
    
def split_text_by_star(text):
    # Tách đoạn văn bản thành các câu bằng cách sử dụng dấu chấm và dấu sao.
    sentences = text.split('*')
    
    # Loại bỏ khoảng trắng đầu và cuối của từng câu.
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    # Nối các câu lại với dấu xuống dòng.
    formatted_text = '\n'.join(sentences)
    
    return formatted_text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    if user_input.lower() in ['exit', 'quit', 'bye']:
        return jsonify({'response': "Bái bai! Hẹn gặp lại bạn sau nhé! moah moah <3"})
    
    global MAIN_TEMPLATE
    if user_input.lower().startswith('adjust template:'):
        MAIN_TEMPLATE = user_input[16:].strip()
        return jsonify({'response': "Template adjusted successfully."})

    user_input_cleaned = user_input.replace('"', '').replace('**', '')
    r.extract_keywords_from_sentences([user_input_cleaned])
    sum_input = r.get_ranked_phrases()
    if not sum_input:
        return jsonify({'response': "Sorry, I couldn't understand your input. Please try again."})
    
    query = ' '.join(sum_input)
    file_result = search_file(query)
    if file_result:
        prompt = f"{MAIN_TEMPLATE}\n\nUser: {query}\n\nRelevant information: {file_result}\n\nChatbot:"
    else:
        web_result = web_search(query)
        prompt = f"{MAIN_TEMPLATE}\n\nUser: {query}\n\nRelevant information from web: {web_result}\n\nChatbot:" if web_result else f"{MAIN_TEMPLATE}\n\nUser: {query}\n\nChatbot:"
    
    response = generate_response(prompt)
    response_cleaned = format_response(response)
    response_line = split_text_by_star(response_cleaned)
    
    if 'formula' in query or 'công thức' in query:
        math_image = generate_math_image(query)
        response_cleaned = f"{response_line}\n\n{math_image}"
    
    write_to_file(response_line)
    return jsonify({'response': response_line})

if __name__ == '__main__':
    app.run(debug=True)
