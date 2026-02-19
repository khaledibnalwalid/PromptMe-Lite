// LLM07 System Prompt Leakage Challenge - Modern Chat Interface

const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const queryCounter = document.getElementById('query-counter');

// Add message to chat
function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = sender === 'user' ? 'You' : 'Assistant';

    const text = document.createElement('div');
    text.className = 'message-text';

    // Check if message contains the API key and highlight it
    if (content.includes('d368130b3370c44860743687208a846e')) {
        text.innerHTML = content.replace(
            /d368130b3370c44860743687208a846e/g,
            '<span class="flag">d368130b3370c44860743687208a846e</span>'
        );
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

// Update query counter
function updateQueryCounter(count) {
    if (queryCounter) {
        queryCounter.textContent = `${count}/20 queries used`;

        // Change color based on usage
        if (count >= 18) {
            queryCounter.style.background = 'rgba(244, 67, 54, 0.3)'; // Red
        } else if (count >= 15) {
            queryCounter.style.background = 'rgba(255, 152, 0, 0.3)'; // Orange
        } else if (count >= 10) {
            queryCounter.style.background = 'rgba(255, 193, 7, 0.3)'; // Amber
        } else {
            queryCounter.style.background = 'rgba(255, 255, 255, 0.2)'; // Default
        }
    }
}

// Show success banner
function showSuccessBanner() {
    const existingBanner = document.querySelector('.success-banner');
    if (!existingBanner) {
        const banner = document.createElement('div');
        banner.className = 'success-banner';
        banner.innerHTML = '🎉 <strong>Congratulations!</strong> You successfully jailbroke the assistant and leaked the API key!';

        const header = document.querySelector('header');
        header.insertAdjacentElement('afterend', banner);
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
        const params = new URLSearchParams();
        params.append('message', message);

        const response = await fetch('/ask', {
            method: 'POST',
            body: params
        });

        const html = await response.text();

        // Remove loading
        removeLoading();

        // Parse the HTML response
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Check for error banner
        const errorBanner = doc.querySelector('.error-banner');
        if (errorBanner) {
            addMessage(errorBanner.textContent.trim(), 'assistant');
            messageInput.value = '';
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            return;
        }

        // Get assistant messages
        const messages = doc.querySelectorAll('.message.assistant');

        if (messages.length > 0) {
            // Get the last assistant message
            const lastMessage = messages[messages.length - 1];
            const messageText = lastMessage.querySelector('.message-text');

            if (messageText) {
                const content = messageText.innerHTML || messageText.textContent;

                // Create a temporary div to extract pure text
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = content;
                const textContent = tempDiv.textContent || tempDiv.innerText;

                addMessage(textContent, 'assistant');

                // Check if API key was leaked (success)
                if (content.includes('d368130b3370c44860743687208a846e')) {
                    showSuccessBanner();
                }
            }
        }

        // Update query counter
        const newCounter = doc.querySelector('#query-counter');
        if (newCounter) {
            const match = newCounter.textContent.match(/(\d+)\/20/);
            if (match) {
                updateQueryCounter(parseInt(match[1]));
            }
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

// Reset session function
async function resetSession() {
    if (!confirm('Are you sure you want to reset the session? This will clear all messages and reset the query counter.')) {
        return;
    }

    try {
        const response = await fetch('/reset', {
            method: 'POST'
        });

        if (response.ok) {
            // Reload the page to show clean state
            window.location.reload();
        } else {
            alert('Failed to reset session. Please try again.');
        }
    } catch (error) {
        alert('Error resetting session: ' + error.message);
    }
}
