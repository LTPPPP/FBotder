import io
import base64
from sympy import latex, sympify, SympifyError
import matplotlib.pyplot as plt

def format_response(response):
    response = response.replace('"', '').replace('**', '').replace('```', '')
    lines = response.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('*'):
            formatted_lines.append('\n' + line)
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def split_text_into_sentences(text):
    # Use NLTK to split text into sentences
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(text)
    return '\n'.join(sentences)

def format_text(text):
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip().startswith('*'):
            formatted_lines.append(f"<strong>{line.strip()[1:].strip()}</strong>")
        else:
            formatted_lines.append(f"{line}")
    return '\n'.join(formatted_lines)