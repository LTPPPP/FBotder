import re

def latex_to_text(latex):
    replacements = {
        # Derivatives and Logs
        '\\frac{d}{dx}': 'd/dx',
        '\\ln': 'ln',
        '\\log': 'log',
        
        # Trigonometric functions
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
        
        # Other mathematical functions
        '\\sqrt': 'sqrt',
        '\\pm': '±',
        
        # Brackets
        '\\left(': '(',
        '\\right)': ')',
        '\\left[': '[',
        '\\right]': ']',
        '\\left\\{': '{',
        '\\right\\}': '}',

        # Greek letters (lowercase)
        '\\alpha': 'alpha',
        '\\beta': 'beta',
        '\\gamma': 'gamma',
        '\\delta': 'delta',
        '\\epsilon': 'epsilon',
        '\\zeta': 'zeta',
        '\\eta': 'eta',
        '\\theta': 'theta',
        '\\iota': 'iota',
        '\\kappa': 'kappa',
        '\\lambda': 'lambda',
        '\\mu': 'mu',
        '\\nu': 'nu',
        '\\xi': 'xi',
        '\\omicron': 'omicron',
        '\\pi': 'pi',
        '\\rho': 'rho',
        '\\sigma': 'sigma',
        '\\tau': 'tau',
        '\\upsilon': 'upsilon',
        '\\phi': 'phi',
        '\\chi': 'chi',
        '\\psi': 'psi',
        '\\omega': 'omega',

        # Greek letters (uppercase)
        '\\Delta': 'Delta',
        '\\Gamma': 'Gamma',
        '\\Lambda': 'Lambda',
        '\\Omega': 'Omega',
        '\\Phi': 'Phi',
        '\\Pi': 'Pi',
        '\\Psi': 'Psi',
        '\\Sigma': 'Sigma',
        '\\Theta': 'Theta',
        '\\Upsilon': 'Upsilon',
        '\\Xi': 'Xi',

        # Logical operators
        '\\text{and}': 'and',
        '\\text{or}': 'or',
        '\\text{not}': 'not',

        # Comparison operators
        '\\neq': '!=',
        '\\leq': '<=',
        '\\geq': '>=',
        '\\equiv': '===',
        '\\approx': '≈',
        '\\sim': '~',

        # Miscellaneous symbols
        '\\propto': 'propto',
        '\\infty': 'infinity',
        '\\cdot': '*',
        '\\times': '*',
        '\\div': '/',
        '\\sum': 'sum',
        '\\int': 'integral',
        '\\prod': 'product',
        '\\subset': 'subset',
        '\\supset': 'superset',
        '\\subseteq': 'subseteq',
        '\\supseteq': 'superset',
        '\\cup': 'union',
        '\\cap': 'intersection',
        '\\forall': 'for all',
        '\\exists': 'exists',
        '\\neg': 'not',
        '\\in': 'in',
        '\\notin': 'not in',
        '\\to': 'to',
        '\\rightarrow': '->',
        '\\leftarrow': '<-',
        '\\Leftrightarrow': '<->',
        '\\Rightarrow': '=>',
        '\\Leftarrow': '<=',
        '\\lt': '<',
        '\\gt': '>',

        # Text formatting
        '\\mathbf': 'bold',
        '\\mathit': 'italic',
        '\\mathbb': 'bb',
        '\\mathcal': 'cal',
        '\\mathfrak': 'frak',
        '\\mathsf': 'sf',
        '\\mathtt': 'tt',
        '\\underline': 'underline',
        '\\overline': 'overline',
        '\\hat': 'hat',
        '\\tilde': 'tilde',
        '\\bar': 'bar',
        '\\vec': 'vec',
        '\\dot': 'dot',
        '\\ddot': 'ddot',
        '\\ddots': 'ddots',
        '\\cdots': 'cdots',
        '\\ldots': 'ldots',
        '\\vdots': 'vdots',
        '\\hline': 'hline',
        '\\cline': 'cline',
        '\\includegraphics': 'includegraphics',

        # Advanced mathematical notation
        '\\frac{\\partial}{\\partial x}': '∂/∂x',
        '\\nabla': '∇',

        # Probability and statistics
        '\\mathbb{E}': 'E',
        '\\mathbb{P}': 'P',
        '\\Pr': 'Pr',
        '\\var': 'Var',
        '\\cov': 'Cov',
        '\\corr': 'Corr',
        '\\mathcal{N}': 'N',
        '\\rightarrow': '→',
        '\\Rightarrow': '⇒',
        '\\mid': '|',

        # Common mathematical functions
        '\\exp': 'exp',
        '\\max': 'max',
        '\\min': 'min',
        '\\sup': 'sup',
        '\\inf': 'inf',
        '\\lim': 'lim',

        # Summation and product
        '\\sum': '∑',
        '\\prod': '∏',

        # Integrals
        '\\int': '∫',
        '\\oint': '∮',
        '\\iint': '∬',
        '\\iiint': '∭',

        # Set theory
        '\\emptyset': '∅',
        '\\notin': '∉',
        '\\subset': '⊂',
        '\\supset': '⊃',
        '\\subseteq': '⊆',
        '\\supseteq': '⊇',

        # Logic
        '\\forall': '∀',
        '\\exists': '∃',
        '\\nexists': '∄',

        # Equality and inequality
        '\\approx': '≈',
        '\\equiv': '≡',
        '\\leq': '≤',
        '\\geq': '≥',
        '\\ll': '≪',
        '\\gg': '≫',

        # Miscellaneous
        '\\infty': '∞',
        '\\partial': '∂',
        '\\deg': '°',
        '\\prime': '′',
        '\\backprime': '‵',

        # Basic operators
        '\\pm': '±',
        '\\mp': '∓',
        '\\times': '×',
        '\\div': '÷',
        '\\cdot': '·',
        '\\ast': '*',

        # Set theory
        '\\setminus': '∖',

        # Logical operators
        '\\land': '∧',
        '\\lor': '∨',
        '\\lnot': '¬',
        '\\top': '⊤',
        '\\bot': '⊥',

        # Arrows
        '\\leftrightarrow': '↔',

        # More Greek letters
        '\\varepsilon': 'ε',

        # Miscellaneous symbols
        '\\circ': '∘',
        '\\bullet': '•',
        '\\oplus': '⊕',
        '\\otimes': '⊗',
        '\\perp': '⊥',
        '\\parallel': '∥',
        '\\angle': '∠',
        '\\triangle': '△',
        '\\square': '□',
        '\\diamond': '◇',
        '\\aleph': 'ℵ',
        '\\hbar': 'ℏ',
        '\\ell': 'ℓ',
        '\\wp': '℘',
        '\\Re': 'ℜ',
        '\\Im': 'ℑ',
        '\\neg': '¬',
        '\\wedge': '∧',
        '\\vee': '∨',
        '\\bigcup': '⋃',
        '\\bigcap': '⋂',
        '\\partial': '∂',
        '\\nabla': '∇',
        '\\propto': '∝',
        '\\eth': 'ð',
        '\\surd': '√',
        '\\vdash': '⊢',
        '\\models': '⊨',
        '\\lfloor': '⌊',
        '\\rfloor': '⌋',
        '\\lceil': '⌈',
        '\\rceil': '⌉',
        '\\preceq': '≼',
        '\\succeq': '≽',
        '\\prec': '≺',
        '\\succ': '≻',
        '\\dashv': '⊣',
        '\\measuredangle': '∡',
        '\\sphericalangle': '∢',
        '\\blacksquare': '■',
        '\\blacktriangle': '▲',
        '\\blacktriangledown': '▼',
        '\\blacklozenge': '◆',
        '\\circledast': '⊛',
        '\\circleddash': '⊝',
        '\\circledcirc': '⊚',
        '\\oslash': '⊘',
        '\\boxplus': '⊞',
        '\\boxminus': '⊟',
        '\\boxtimes': '⊠',
        '\\boxdot': '⊡',
        '\\bigtriangleup': '△',
        '\\bigtriangledown': '▽',
        '\\bigcirc': '○',
        '\\bigstar': '★',
        '\\asymp': '≍',
        '\\bowtie': '⋈',
        '\\sqsubset': '⊏',
        '\\sqsupset': '⊐',
        '\\sqsubseteq': '⊑',
        '\\sqsupseteq': '⊒',
        '\\int': '∫',
        '\\iint': '∬',
        '\\iiint': '∭',
        '\\oint': '∮',
        '\\sum': '∑',
        '\\Sigma': '∑',
        '\\Delta': 'Δ',
        '\\delta': 'δ',
        '\\nabla': '∇',
        '\\partial': '∂',

        # Matrix 
        '\\matrix': 'matrix',
        '\\bmatrix': '[matrix]',
        '\\pmatrix': '(matrix)',
        '\\vmatrix': '|matrix|',
        '\\Vmatrix': '‖matrix‖',

        # Matrix operations
        '\\det': 'det',
        '\\tr': 'tr',
        '\\rank': 'rank',
        '\\ker': 'ker',
        '\\dim': 'dim',
        '\\transpose': 'ᵀ',
        '\\top': 'ᵀ',
        '\\dagger': '†',
        '\\hermitianconjugate': '†',

        # Matrix elements
        '\\mathbf{A}': 'A',
        '\\mathbf{B}': 'B',
        '\\mathbf{C}': 'C',
        '\\mathbf{X}': 'X',
        '\\mathbf{Y}': 'Y',
        '\\mathbf{Z}': 'Z',

        # Identity matrix
        '\\mathbf{I}': 'I',
        '\\mathrm{I}': 'I',

        # Zero matrix
        '\\mathbf{0}': '0',
        '\\mathrm{0}': '0',

        # Vector symbols
        '\\vec': 'vec',
        '\\overrightarrow': '→',
        '\\overleftarrow': '←',
        '\\mathbf{v}': 'v',
        '\\mathbf{u}': 'u',
        '\\mathbf{w}': 'w',

        # Norms and inner products
        '\\lVert': '‖',
        '\\rVert': '‖',
        '\\langle': '⟨',
        '\\rangle': '⟩',

        # Matrix decompositions
        '\\operatorname{diag}': 'diag',
        '\\operatorname{eig}': 'eig',
        '\\operatorname{svd}': 'SVD',
        '\\operatorname{LU}': 'LU',
        '\\operatorname{QR}': 'QR',

        # Special matrices
        '\\operatorname{Toeplitz}': 'Toeplitz',
        '\\operatorname{Hankel}': 'Hankel',
        '\\operatorname{Vandermonde}': 'Vandermonde',

        # Linear transformations
        '\\operatorname{im}': 'im',
        '\\operatorname{coker}': 'coker',

        # Tensor product
        '\\otimes': '⊗',

        # Kronecker product
        '\\bigotimes': '⊗',

        # Hadamard product
        '\\circ': '∘',

        # Frobenius norm
        '\\|\\mathbf{A}\\|_F': '‖A‖_F',

        # Eigenvalues and eigenvectors
        '\\lambda': 'λ',
        '\\operatorname{eig}': 'eig',

        # Positive definite
        '\\succ': '≻',
        '\\prec': '≺',
        '\\succeq': '⪰',
        '\\preceq': '⪯'

        # Graph Theory
        '\\mathcal{G}': 'G',  # Graph
        '\\mathcal{V}': 'V',  # Vertex set
        '\\mathcal{E}': 'E',  # Edge set
        '\\deg': 'deg',  # Degree of a vertex
        '\\path': 'path',  # Path
        '\\cycle': 'cycle',  # Cycle
        '\\chi': 'χ',  # Chromatic number

        # Combinatorics
        '\\binom': 'C',  # Binomial coefficient
        '\\stirling': 'S',  # Stirling number
        '\\mathcal{P}': 'P',  # Permutation

        # Number Theory
        '\\gcd': 'gcd',  # Greatest common divisor
        '\\lcm': 'lcm',  # Least common multiple
        '\\pmod': 'mod',  # Modulo operation
        '\\phi': 'φ',  # Euler's totient function

        # Set Theory
        '\\varnothing': '∅',  # Empty set
        '\\powerset': '℘',  # Power set

        # Algorithms and Complexity
        '\\mathcal{O}': 'O',  # Big O notation
        '\\Omega': 'Ω',  # Big Omega notation
        '\\Theta': 'Θ',  # Big Theta notation

        # Combination
        'C_n^k': 'C(n,k)',  # Combination of k from n
        '\\binom{n}{k}': 'C(n,k)',  # Binomial coefficient (already present, but included for clarity)

        # Permutation
        'P_n^k': 'P(n,k)',  # Permutation of k from n
        'A_n^k': 'P(n,k)',  # Alternative notation for permutation

        # Probability
        'P(A)': 'P(A)',  # Probability of event A
        'P(A|B)': 'P(A|B)',  # Conditional probability of A given B
        'P(A \\cup B)': 'P(A ∪ B)',  # Probability of A or B
        'P(A \\cap B)': 'P(A ∩ B)',  # Probability of A and B

        # Additional probability notations
        '\\overline{A}': 'A\'',  # Complement of event A
        'P(\\overline{A})': 'P(A\')',  # Probability of complement of A

        # Expected value and variance (if not already present)
        'E(X)': 'E(X)',  # Expected value of X
        'Var(X)': 'Var(X)',  # Variance of X
        '\\sigma^2': 'σ²',  # Variance symbol
    }

    # Replace fraction notation separately
    latex = re.sub(r'\\frac{(.+?)}{(.+?)}', r'(\1)/(\2)', latex)  # Convert \frac{a}{b} to (a)/(b)

    # Replace all LaTeX commands with text symbols
    for key, value in replacements.items():
        latex = latex.replace(key, value)

    # Handle power notation
    latex = re.sub(r'\^{(.+?)}', r'^\1', latex)  # Convert ^{a} to ^a
    
    # Remove unnecessary escape characters
    latex = latex.replace('$$', '').replace('$', '')  # Remove inline math mode characters
    
    return latex
