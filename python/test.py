import re

text = """
Đạo hàm của một hằng số
\\frac{d}{dx}c = 0

Đạo hàm của một hàm lũy thừa
\\frac{d}{dx}x^n = nx^{n-1}

Đạo hàm của một hàm mũ
\\frac{d}{dx}e^x = e^x
\\frac{d}{dx}a^x = a^x \\ln a

Đạo hàm của một hàm logarit
\\frac{d}{dx}\\ln x = \\frac{1}{x}
\\frac{d}{dx}\\log_a x = \\frac{1}{x\\ln a}

Đạo hàm của một hàm lượng giác
\\frac{d}{dx}\\sin x = \\cos x
\\frac{d}{dx}\\cos x = -\\sin x
\\frac{d}{dx}\\tan x = \\sec^2 x
\\frac{d}{dx}\\cot x = -\\csc^2 x
\\frac{d}{dx}\\sec x = \\sec x\\tan x
\\frac{d}{dx}\\csc x = -\\csc x\\cot x

Đạo hàm của hàm số nghịch đảo
\\frac{d}{dx}\\arcsin x = \\frac{1}{\\sqrt{1-x^2}}
\\frac{d}{dx}\\arccos x = -\\frac{1}{\\sqrt{1-x^2}}
\\frac{d}{dx}\\arctan x = \\frac{1}{1+x^2}
\\frac{d}{dx}\\operatorname{arccot} x = -\\frac{1}{1+x^2}
\\frac{d}{dx}\\operatorname{arcsec} x = \\frac{1}{|x|\\sqrt{x^2-1}}
\\frac{d}{dx}\\operatorname{arccsc} x = -\\frac{1}{|x|\\sqrt{x^2-1}}

Đạo hàm của hàm hợp
Nếu f(x) khả vi tại x và g(x) khả vi tại f(x), thì g(f(x)) khả vi tại x và
$$\\frac{d}{dx}g(f(x)) = g'(f(x))f'(x)$$

Đạo hàm của một tổng hay hiệu
\\frac{d}{dx}(f(x) \\pm g(x)) = f'(x) \\pm g'(x)

Đạo hàm của một tích
\\frac{d}{dx}(f(x)g(x)) = f'(x)g(x) + f(x)g'(x)

Đạo hàm của một thương
\\frac{d}{dx}\\left(\\frac{f(x)}{g(x)}\\right) = \\frac{g(x)f'(x) - f(x)g'(x)}{g(x)^2}

Quy tắc đạo hàm liên hợp
Nếu u(x) và v(x) khả vi tại x, thì
$$\\frac{d}{dx}(u(x)v(x)) = u'(x)v(x) + u(x)v'(x)$$
"""

def latex_to_text(latex):
    # Replace LaTeX syntax with corresponding text symbols
    replacements = {
        '\\frac{d}{dx}': 'd/dx ',
        '\\ln': 'ln',
        '\\log': 'log',
        '\\sin': 'sin',
        '\\cos': 'cos',
        '\\tan': 'tan',
        '\\cot': 'cot',
        '\\sec': 'sec',
        '\\csc': 'csc',
        '\\arcsin': 'arcsin',
        '\\arccos': 'arccos',
        '\\arctan': 'arctan',
        '\\operatorname{arccot}': 'arccot',
        '\\operatorname{arcsec}': 'arcsec',
        '\\operatorname{arccsc}': 'arccsc',
        '\\sqrt': 'sqrt',
        '\\pm': '+/-',
        '\\left(': '(',
        '\\right)': ')',
        '\\': ''
    }

    # Replace all LaTeX commands with text symbols
    for key, value in replacements.items():
        latex = latex.replace(key, value)
    
    # Handle power notation
    latex = re.sub(r'\^{(.+?)}', r'^\1', latex)
    latex = re.sub(r'\((.*?)\)', r'(\1)', latex)
    
    # Remove unnecessary escape characters
    latex = latex.replace('$$', '').replace('$', '')
    
    return latex

translated_text = latex_to_text(text)
print(translated_text)
