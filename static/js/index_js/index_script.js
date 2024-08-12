document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');

    function addMessage(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.innerHTML = message;
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


    async function processImage() {
        const file = document.getElementById('user-input').files[0];
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/process_image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        addMessage(data.response, false);
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
                const imageUrl = URL.createObjectURL(blob);

                const imgElement = document.createElement('img');
                imgElement.src = imageUrl;
                imgElement.style.maxWidth = '100%';
                chatMessages.appendChild(imgElement);
                chatMessages.scrollTop = chatMessages.scrollHeight
                sendBtn.click();
                userInput.value = "Processing image...";
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