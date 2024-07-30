import io
import base64
from sympy import latex, sympify, SympifyError
import matplotlib.pyplot as plt

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