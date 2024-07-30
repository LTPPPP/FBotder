import re
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

