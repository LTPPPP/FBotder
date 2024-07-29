document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    function addMessage(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageElement.innerHTML = isUser ? message : message; // Use innerHTML for bot messages
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

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
