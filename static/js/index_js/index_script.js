document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');

    function addMessage(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');

        if (!isUser) {
            // Format the message with copyable code blocks
            message = formatMessageWithCopyableCode(message);

            // Convert LaTeX to text
            message = latexToText(message);
        }

        messageElement.innerHTML = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const copyButtons = messageElement.querySelectorAll('.copy-btn');
        copyButtons.forEach(button => {
            button.addEventListener('click', function () {
                const codeBlock = this.closest('tr').querySelector('pre');
                const codeText = codeBlock.textContent.split('\n').slice(1).join('\n'); // Exclude the first line
                navigator.clipboard.writeText(codeText).then(() => {
                    // Change button text temporarily to indicate success
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            });
        });
    }

    function latexToText(text) {
        // Replace display math mode
        text = text.replace(/\$\$(.*?)\$\$/g, '$1');

        // Replace inline math mode
        text = text.replace(/\$(.*?)\$/g, '$1');

        // Replace \frac{numerator}{denominator}
        text = text.replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)');

        // Replace superscripts
        text = text.replace(/\^(\{[^}]*\}|\S)/g, '^($1)');

        // Replace subscripts
        text = text.replace(/_(\{[^}]*\}|\S)/g, '_($1)');

        // Replace \sqrt{x}
        text = text.replace(/\\sqrt\{([^}]*)\}/g, 'sqrt($1)');

        // Replace \left and \right
        text = text.replace(/\\left|\\\right/g, '');

        // Replace Greek letters
        const greekLetters = {
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
            'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ',
            'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο',
            'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
            'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω'
        };
        for (let [name, symbol] of Object.entries(greekLetters)) {
            text = text.replace(new RegExp('\\\\' + name, 'g'), symbol);
        }

        // Replace common LaTeX commands
        const latexCommands = {
            'sum': '∑', 'prod': '∏', 'int': '∫', 'infty': '∞',
            'times': '×', 'div': '÷', 'cdot': '·', 'approx': '≈',
            'neq': '≠', 'geq': '≥', 'leq': '≤', 'pm': '±',
            'in': '∈', 'notin': '∉', 'subset': '⊂', 'supset': '⊃',
            'cup': '∪', 'cap': '∩', 'emptyset': '∅'
        };
        for (let [command, symbol] of Object.entries(latexCommands)) {
            text = text.replace(new RegExp('\\\\' + command, 'g'), symbol);
        }

        // Remove remaining LaTeX commands
        text = text.replace(/\\[a-zA-Z]+/g, '');

        return text;
    }

    function formatMessageWithCopyableCode(message) {
        const codeRegex = /```([^`]*)```/g;
        let formattedMessage = message.replace(codeRegex, (_, codeContent) => {
            return `
                <table class="code-table">
                    <tr>
                        <td><pre>${codeContent}</pre></td>
                        <td><button class="copy-btn">Copy</button></td>
                    </tr>
                </table>
            `;
        });
        return formattedMessage;
    }

    function addTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.classList.add('message', 'bot-message');
        indicatorElement.innerHTML = 'Chatbot is typing<span class="typing-indicator"></span>';
        chatMessages.appendChild(indicatorElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicatorElement;
    }

    function removeTypingIndicator(indicator) {
        chatMessages.removeChild(indicator);
    }

    async function processImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/process_image', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            addMessage(data.response, false);
        } catch (error) {
            console.error('Error:', error);
            addMessage('An error occurred while processing the image. Please try again.', false);
        }
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            const typingIndicator = addTypingIndicator();

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            })
                .then(response => response.json())
                .then(data => {
                    removeTypingIndicator(typingIndicator);
                    addMessage(data.response, false);
                })
                .catch(error => {
                    console.error('Error:', error);
                    removeTypingIndicator(typingIndicator);
                    addMessage('An error occurred. Please try again.', false);
                });
        }
    }

    userInput.addEventListener('paste', async (e) => {
        e.preventDefault();
        const items = e.clipboardData.items;
        let pastedText = '';
        let hasImage = false;

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                hasImage = true;
                const blob = items[i].getAsFile();
                const file = new File([blob], "pasted_image.png", { type: blob.type });

                const imgElement = document.createElement('img');
                imgElement.src = URL.createObjectURL(blob);
                imgElement.style.maxWidth = '100%';
                chatMessages.appendChild(imgElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;

                addMessage('Processing image...', false);
                await processImage(file);
                return;  // Stop processing if image is found
            } else if (items[i].type === 'text/plain') {
                pastedText = await new Promise(resolve => items[i].getAsString(resolve));
            }
        }

        if (!hasImage && pastedText) {
            userInput.value = pastedText;
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    newChatBtn.addEventListener('click', function () {
        chatMessages.innerHTML = '';
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'exit' })
        })
            .then(response => response.json())
            .then(data => {
                addMessage('New chat started. How can I assist you today?', false);
            });
    });
});
