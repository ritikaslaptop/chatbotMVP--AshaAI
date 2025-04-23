//quotes galore :D
const quotes = [
    { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
    { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
    { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
    { text: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
    { text: "The best preparation for tomorrow is doing your best today.", author: "H. Jackson Brown Jr." },
    { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
    { text: "The only limit to our realization of tomorrow will be our doubts of today.", author: "Franklin D. Roosevelt" },
    { text: "Your time is limited, don't waste it living someone else's life.", author: "Steve Jobs" },
    { text: "Life is 10% what happens to you and 90% how you react to it.", author: "Charles R. Swindoll" },
    { text: "The way to get started is to quit talking and begin doing.", author: "Walt Disney" }
];

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        themeToggle.innerHTML = `<i class="fas fa-${newTheme === 'dark' ? 'moon' : 'sun'} me-1"></i> Toggle Theme`;
    });


    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    document.getElementById('quoteText').textContent = `"${randomQuote.text}"`;
    document.getElementById('quoteAuthor').textContent = `- ${randomQuote.author}`;


    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    const clearChatBtn = document.getElementById('clearChat');


    let chatHistory = [];
    let currentMessageId = null;


    initChat();


    function initChat() {

        messageInput.focus();
        chatForm.addEventListener('submit', handleFormSubmit);
        messageInput.addEventListener('keydown', handleInputKeydown);
        clearChatBtn.addEventListener('click', clearChat);

        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                messageInput.value = btn.textContent;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });


        scrollToBottom();
    }


    function handleFormSubmit(e) {
        e.preventDefault();
        const message = messageInput.value.trim();

        if (message) {
            addUserMessage(message);
            messageInput.value = '';
            showTypingIndicator();
            sendMessage(message);
        }
    }


    function handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    }


    function addUserMessage(message) {
        const time = getCurrentTime();

        const messageHtml = `
            <div class="chat-message user-message">
                <div class="message-content">
                    <div class="message-bubble">${formatMessage(message)}</div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;

        appendMessage(messageHtml);
        chatHistory.push({ role: 'user', content: message, time });
    }


    function addBotMessage(message, id) {
        const time = getCurrentTime();
        currentMessageId = id;

        const messageHtml = `
            <div class="chat-message bot-message">
                <div class="message-avatar">
                    <svg class="logo-svg-small" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="25" cy="25" r="20" fill="#5E17EB" />
                        <path d="M15 25C15 20 20 15 25 15C30 15 35 20 35 25C35 30 30 35 25 35" stroke="white" stroke-width="2" fill="none" />
                        <circle cx="25" cy="25" r="3" fill="white" />
                        <path d="M25 35V40" stroke="white" stroke-width="2" />
                        <path d="M20 40H30" stroke="white" stroke-width="2" />
                    </svg>
                </div>
                <div class="message-content">
                    <div class="message-bubble">${formatMessage(message)}</div>
                    <div class="message-time">${time}</div>
                    <div class="message-feedback" data-message-id="${id}">
                        <button class="feedback-btn" data-feedback="helpful">
                            <i class="far fa-thumbs-up me-1"></i>Helpful
                        </button>
                        <button class="feedback-btn" data-feedback="not-helpful">
                            <i class="far fa-thumbs-down me-1"></i>Not helpful
                        </button>
                    </div>
                </div>
            </div>
        `;

        appendMessage(messageHtml);
        chatHistory.push({ role: 'assistant', content: message, time, id });


        const feedbackBtns = document.querySelectorAll(`.message-feedback[data-message-id="${id}"] .feedback-btn`);
        feedbackBtns.forEach(btn => {
            btn.addEventListener('click', () => handleFeedback(id, btn.dataset.feedback));
        });
    }


    function formatMessage(text) {

        text = text.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );


        text = text.replace(/\n/g, '<br>');

        if (text.includes('\n-') || text.includes('\n*')) {
            const lines = text.split('<br>');
            let inList = false;
            let formatted = [];

            lines.forEach(line => {
                if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                    if (!inList) {
                        formatted.push('<ul>');
                        inList = true;
                    }
                    const listItem = line.trim().substring(2);
                    formatted.push(`<li>${listItem}</li>`);
                } else {
                    if (inList) {
                        formatted.push('</ul>');
                        inList = false;
                    }
                    formatted.push(line);
                }
            });

            if (inList) {
                formatted.push('</ul>');
            }

            text = formatted.join('');
        }

        return text;
    }


    function appendMessage(messageHtml) {
        chatMessages.innerHTML += messageHtml;
        scrollToBottom();
    }


    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    //get current time:)
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    //show typing indicator
    function showTypingIndicator() {
        typingIndicator.classList.remove('d-none');
        scrollToBottom();
    }

    //hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.classList.add('d-none');
    }

    //send a message to the server
    function sendMessage(message) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            //hide typing indicator
            hideTypingIndicator();

            //add bot message
            addBotMessage(data.message, data.id);
        })
        .catch(error => {
            console.error('Error:', error);
            hideTypingIndicator();

            //add error message
            addBotMessage(
                "I'm sorry, I couldn't process your request. Please try again later.",
                "error-" + Date.now()
            );
        });
    }

    //handle message feedback
    function handleFeedback(messageId, feedback) {
        //find the feedback buttons for this message
        const feedbackBtns = document.querySelectorAll(`.message-feedback[data-message-id="${messageId}"] .feedback-btn`);

        //remove selected class from all buttons
        feedbackBtns.forEach(btn => btn.classList.remove('selected'));

        //add selected class to clicked button
        const clickedBtn = document.querySelector(`.message-feedback[data-message-id="${messageId}"] .feedback-btn[data-feedback="${feedback}"]`);
        if (clickedBtn) {
            clickedBtn.classList.add('selected');
        }

        //send feedback to server
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: messageId,
                feedback: feedback
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Feedback submitted:', data);
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
        });
    }

    //chat history (clear)
    function clearChat() {
        //keep welcome msg up always
        const welcomeMessage = chatMessages.querySelector('.chat-message');
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        }

       //reset chat history
        chatHistory = [];
        currentMessageId = null;

        //focus on input field
        messageInput.focus();
    }
});
