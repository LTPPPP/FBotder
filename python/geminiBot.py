from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os,re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../templates', static_folder='../assets')

# Set up Gemini API
genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-pro')

# Initialize the main template
main_template = "You are a helpful assistant. Please provide accurate and authentic responses to user requests."

def search_file(query):
    try:
        with open('../documents/response/find.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        if query.lower() in content.lower():
            return content[content.lower().index(query.lower()):content.lower().index(query.lower()) + 200]
        return None
    except UnicodeDecodeError:
        print("Error: Unable to read the file. It may contain characters that are not UTF-8 encoded.")
        return None

def write_to_file(response):
    with open('../documents/response/find.txt', 'a', encoding='utf-8') as file:
        file.write(f"{response}\n\n")

def web_search(query):
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='g')
    if results:
        return results[0].get_text()
    return None

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    if user_input.lower() in ['exit', 'quit', 'bye']:
        return jsonify({'response': "Bái bai! Hẹn gặp lại bạn sau nhé! moah moah <3"})

    if user_input.lower().startswith('adjust template:'):
        global main_template
        main_template = user_input[16:].strip()
        return jsonify({'response': "Template adjusted successfully."})

    file_result = search_file(user_input)
    if file_result:
        prompt = f"{main_template}\n\nUser: {user_input}\n\nRelevant information: {file_result}\n\nChatbot:"
    else:
        web_result = web_search(user_input)
        if web_result:
            prompt = f"{main_template}\n\nUser: {user_input}\n\nRelevant information from web: {web_result}\n\nChatbot:"
        else:
            prompt = f"{main_template}\n\nUser: {user_input}\n\nChatbot:"

    response = generate_response(prompt)
    write_to_file(response)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
