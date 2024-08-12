from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PIL.Image

# Configure the API key
genai.configure(api_key='AIzaSyABvqN-8d3jpqlOeE1HzSK07LcW-R1B0Ss')

# Initialize the models
model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

app = Flask(__name__,template_folder='../templates', static_folder='../static')

def process_text(prompt):
    response = model.generate_content(prompt)
    return response.text

def process_image(image_path, prompt):
    img = PIL.Image.open(image_path)
    response = vision_model.generate_content([prompt, img])
    return response.text

@app.route('/')
def index():
    return render_template('code.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    
    if user_input.lower().startswith("image:"):
        image_path = user_input[6:].strip()
        prompt = data.get('image_prompt')
        response = process_image(image_path, prompt)
    else:
        response = process_text(user_input)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
