import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from functools import lru_cache
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

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
    if query.__contains__('fomula') or query.__contains__('công thức') :
        url = f"https://www.google.com/search?q={query}+formula"
    else :
        url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='g')
    return results[0].get_text() if results else None

def generate_response(prompt):
    return model.generate_content(prompt).text

def clean_response(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = [re.sub(r'^[^a-zA-Z0-9]*(```|\**\**)', '', sentence) for sentence in sentences]
    return ' '.join(cleaned_sentences)

def filter_main_keywords(query):
    # Tokenize the query
    word_tokens = word_tokenize(query)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in word_tokens if word.lower() not in stop_words]
    
    # Join the filtered words back into a string
    filtered_query = ' '.join(filtered_words)
    
    return filtered_query

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

    filtered_input = filter_main_keywords(user_input)
    file_result = search_file(filtered_input)
    if file_result:
        prompt = f"{MAIN_TEMPLATE}\n\nUser: {user_input}\n\nRelevant information: {file_result}\n\nChatbot:"
    else:
        web_result = web_search(filtered_input)
        prompt = f"{MAIN_TEMPLATE}\n\nUser: {user_input}\n\nRelevant information from web: {web_result}\n\nChatbot:" if web_result else f"{MAIN_TEMPLATE}\n\nUser: {user_input}\n\nChatbot:"

    response = generate_response(prompt)
    modified_response = clean_response(response)
    write_to_file(modified_response)
    print("keyword : " + filtered_input)
    print("respone : "+modified_response)
    return jsonify({'response': modified_response})

if __name__ == '__main__':
    app.run(debug=True)