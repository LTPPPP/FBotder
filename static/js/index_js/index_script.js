document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Initialize marked
    marked.setOptions({
        breaks: true,
        gfm: true,
    });

    function addMessage(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');

        if (!isUser) {
            // Format the message with Markdown
            message = formatMessageWithMarkdown(message);

            // Convert LaTeX to text for better display
            message = latexToText(message);
        }

        messageElement.innerHTML = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add copy functionality for code blocks
        const codeBlocks = messageElement.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            const copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.classList.add('copy-btn');
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent).then(() => {
                    const originalText = copyButton.textContent;
                    copyButton.textContent = 'Copied!';
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            });
            block.parentNode.insertBefore(copyButton, block);
        });
    }

    // Function to format the message with Markdown
    function formatMessageWithMarkdown(message) {
        return marked.parse(message);
    }

    // Function to convert LaTeX to plain text
    function latexToText(text) {
        // Replace LaTeX expressions with plain text equivalents
        text = text.replace(/\$\$(.*?)\$\$/g, '$1');  // display math mode
        text = text.replace(/\$(.*?)\$/g, '$1');       // inline math mode
        text = text.replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)');  // fractions
        text = text.replace(/\^(\{[^}]*\}|\S)/g, '^($1)');  // superscripts
        text = text.replace(/_(\{[^}]*\}|\S)/g, '_($1)');  // subscripts
        text = text.replace(/\\sqrt\{([^}]*)\}/g, 'sqrt($1)');  // square roots
        text = text.replace(/\\left|\\right/g, '');  // remove \left and \right
        text = text.replace(/\\[a-zA-Z]+/g, '');  // remove remaining LaTeX commands
        return text;
    }

    // Add a typing indicator when the bot is processing the user's message
    function addTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.classList.add('message', 'bot-message');
        indicatorElement.innerHTML = 'Chatbot is typing<span class="typing-indicator"></span>';
        chatMessages.appendChild(indicatorElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicatorElement;
    }

    // Remove the typing indicator once the bot's response is ready
    function removeTypingIndicator(indicator) {
        chatMessages.removeChild(indicator);
    }

    // Function to send the user's message to the server and receive a bot response
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);  // Add the user's message to the chat
            userInput.value = '';  // Clear the input field

            const typingIndicator = addTypingIndicator();  // Show typing indicator

            // Send the message to the server for processing
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            })
                .then(response => response.json())
                .then(data => {
                    removeTypingIndicator(typingIndicator);  // Remove typing indicator
                    addMessage(data.response, false);  // Add the bot's response to the chat
                })
                .catch(error => {
                    console.error('Error:', error);
                    removeTypingIndicator(typingIndicator);
                    addMessage('An error occurred. Please try again.', false);
                });
        }
    }

    // Handle user input events (sending message on Enter key or click of the send button)
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Start a new chat when the "New Chat" button is clicked
    newChatBtn.addEventListener('click', function () {
        chatMessages.innerHTML = '';  // Clear chat messages
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'exit' })
        })
            .then(response => response.json())
            .then(data => {
                addMessage('New chat started. How can I assist you today?', false);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    // Image upload functionality
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    userInput.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                uploadImage(blob);
                e.preventDefault();
                break;
            }
        }
    });

    function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/process_image', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, false);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('An error occurred while processing the image. Please try again.', false);
            });
    }
});