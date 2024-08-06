document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');

    function addMessage(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        if (isUser) {
            messageElement.textContent = message;
        } else {
            messageElement.innerHTML = message; // Use innerHTML for bot messages
        }

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
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

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            const typingIndicator = addTypingIndicator();

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
                const imageUrl = URL.createObjectURL(blob);

                // Display the pasted image
                const imgElement = document.createElement('img');
                imgElement.src = imageUrl;
                imgElement.style.maxWidth = '100%';
                chatMessages.appendChild(imgElement);

                // Perform OCR on the image
                Tesseract.recognize(imageUrl)
                    .then(({ data: { text } }) => {
                        userInput.value = text;
                        sendBtn.click(); // Automatically send the OCR result
                    })
                    .catch(error => {
                        console.error('OCR Error:', error);
                        userInput.value = 'Error reading image. Please try again.';
                    });

                break;
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
        // Clear the chat messages
        chatMessages.innerHTML = '';

        // Clear the user context on the server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: 'exit' })
        })
            .then(response => response.json())
            .then(data => {
                // Optionally, display a message indicating a new chat has started
                const botMessage = document.createElement('div');
                botMessage.classList.add('message', 'bot-message');
                botMessage.innerHTML = 'New chat started. How can I assist you today?';
                chatMessages.appendChild(botMessage);
            });
    });
    const uploadBtn = document.getElementById('upload-btn');
    const fileUpload = document.getElementById('file-upload');

    uploadBtn.addEventListener('click', () => {
        fileUpload.click();
    });

    fileUpload.addEventListener('change', () => {
        const file = fileUpload.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => addMessage(data.response, false))
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('An error occurred during file upload. Please try again.', false);
                });
        }
    });
});
