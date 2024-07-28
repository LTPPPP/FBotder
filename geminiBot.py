import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup

# Set up Gemini API
genai.configure(api_key='AIzaSyABvqN-8d3jpqlOeE1HzSK07LcW-R1B0Ss')
model = genai.GenerativeModel('gemini-pro')

# Initialize the main template
main_template = "You are a helpful assistant. Please provide accurate and authentic responses to user requests."

def search_file(query):
    try:
        with open('find.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Implement a simple search (you might want to use more advanced techniques for better results)
        if query.lower() in content.lower():
            return content[
                   content.lower().index(query.lower()):content.lower().index(query.lower()) + 200]  # Return a snippet
        return None
    except UnicodeDecodeError:
        print("Error: Unable to read the file. It may contain characters that are not UTF-8 encoded.")
        return None

def write_to_file(response):
    with open('find.txt', 'a', encoding='utf-8') as file:
        file.write(f"{response}\n\n")

def web_search(query):
    # This is a simple web search function. You might want to use a more robust solution.
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


def chatbot():
    print("Chatbot: Xin chào! Tôi là chatbot. Bạn cần giúp gì không?")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Bái bai! Hẹn gặp lại bạn sau nhé! moah moah <3 ")
            break

        if user_input.lower().startswith('adjust template:'):
            global main_template
            main_template = user_input[16:].strip()
            print("Chatbot: Template adjusted successfully.")
            continue

        # Search in find.txt
        file_result = search_file(user_input)

        if file_result:
            prompt = f"{main_template}\n\nUser: {user_input}\n\nRelevant information: {file_result}\n\nChatbot:"
        else:
            # Web search
            web_result = web_search(user_input)
            if web_result:
                prompt = f"{main_template}\n\nUser: {user_input}\n\nRelevant information from web: {web_result}\n\nChatbot:"
            else:
                prompt = f"{main_template}\n\nUser: {user_input}\n\nChatbot:"

        response = generate_response(prompt)
        print(f"Chatbot: {response}")
        write_to_file(response)

if __name__ == "__main__":
    chatbot()