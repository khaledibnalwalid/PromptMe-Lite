// LLM01 Prompt Injection Challenge - Modern Chat Interface

const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

// Add message to chat
function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    if (sender === 'user') {
        label.textContent = 'You';
    } else if (sender === 'system') {
        label.textContent = 'System';
    } else {
        label.textContent = 'Assistant';
    }

    const text = document.createElement('div');
    text.className = 'message-text';

    // Check if message contains FLAG and format it
    if (content.includes('FLAG:')) {
        const parts = content.split('FLAG:');
        text.innerHTML = parts[0] + '<span class="flag">FLAG: ' + parts[1] + '</span>';
    } else {
        text.textContent = content;
    }

    messageDiv.appendChild(label);
    messageDiv.appendChild(text);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading';
    loadingDiv.id = 'loading';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = 'Assistant';

    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = 'Thinking...';

    loadingDiv.appendChild(label);
    loadingDiv.appendChild(text);
    chatContainer.appendChild(loadingDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove loading indicator
function removeLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.remove();
    }
}

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Disable send button
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';

    // Add user message to chat
    addMessage(message, 'user');

    // Show loading
    showLoading();

    try {
        // Send to server using FormData (like original form)
        const formData = new FormData();
        formData.append('message', message);

        const response = await fetch('/chat', {
            method: 'POST',
            body: formData
        });

        const html = await response.text();

        // Remove loading
        removeLoading();

        // Parse the HTML response to extract the bot's message
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const messages = doc.querySelectorAll('.message.assistant');

        if (messages.length > 0) {
            // Get the last assistant message (the new one)
            const lastMessage = messages[messages.length - 1];
            const messageText = lastMessage.querySelector('.message-text');

            if (messageText) {
                // Check if there's a FLAG span
                const flagSpan = messageText.querySelector('.flag');
                if (flagSpan) {
                    // Extract text before FLAG and the FLAG itself
                    const textContent = messageText.childNodes[0]?.textContent?.trim() || '';
                    const flagContent = flagSpan.textContent;
                    addMessage(textContent + '\n' + flagContent, 'assistant');
                } else {
                    addMessage(messageText.textContent, 'assistant');
                }
            }
        } else {
            addMessage('Error: No response received', 'assistant');
        }
    } catch (error) {
        removeLoading();
        addMessage(`Error: ${error.message}`, 'assistant');
    }

    // Reset form
    messageInput.value = '';
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
    messageInput.focus();
});

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
});

// Auto-scroll chat container to bottom on load
window.addEventListener('load', () => {
    chatContainer.scrollTop = chatContainer.scrollHeight;
});
