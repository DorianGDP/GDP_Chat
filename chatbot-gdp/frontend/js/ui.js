import { MESSAGE_OPTIONS, SYSTEM_MESSAGES } from './config.js';

class UIService {
    constructor() {
        // DOM Elements
        this.messagesContainer = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.resetButton = document.getElementById('resetButton');
        this.timerWarning = document.getElementById('timer-warning');
        this.statusIndicator = document.getElementById('status-indicator');

        // Initialize textarea auto-resize
        this.initializeTextareaAutoResize();
    }

    /**
     * Initialize textarea auto-resize functionality
     */
    initializeTextareaAutoResize() {
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
        });
    }

    /**
     * Creates and returns a typing indicator element
     * @returns {HTMLElement} Typing indicator element
     */
    createTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = MESSAGE_OPTIONS.CLASSES.CONTAINER;
        
        const innerDiv = document.createElement('div');
        innerDiv.className = 'flex justify-start';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = MESSAGE_OPTIONS.CLASSES.TYPING;
        
        for (let i = 0; i < MESSAGE_OPTIONS.TYPING_INDICATOR.DOT_COUNT; i++) {
            const dot = document.createElement('div');
            dot.className = MESSAGE_OPTIONS.TYPING_INDICATOR.DOT_CLASS;
            contentDiv.appendChild(dot);
        }
        
        innerDiv.appendChild(contentDiv);
        typingDiv.appendChild(innerDiv);
        return typingDiv;
    }

    /**
     * Adds a message to the chat interface
     * @param {string} sender - 'bot' or 'user'
     * @param {string} content - Message content
     * @param {Array} options - Optional clickable options
     */
    appendMessage(sender, content, options = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = MESSAGE_OPTIONS.CLASSES.CONTAINER;
        
        const innerDiv = document.createElement('div');
        innerDiv.className = sender === 'user' ? 'flex justify-end' : 'flex justify-start';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `p-4 max-w-[80%] whitespace-pre-wrap ${
            sender === 'user' ? MESSAGE_OPTIONS.CLASSES.USER : MESSAGE_OPTIONS.CLASSES.BOT
        }`;
        
        // Handle message content
        if (typeof content === 'string') {
            contentDiv.textContent = content;
        } else {
            contentDiv.innerHTML = content;
        }
        
        // Add options if provided
        if (options && options.length > 0) {
            const optionsDiv = this.createOptionsDiv(options);
            contentDiv.appendChild(optionsDiv);
        }
        
        innerDiv.appendChild(contentDiv);
        messageDiv.appendChild(innerDiv);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Creates a div containing clickable options
     * @param {Array} options - Array of option texts
     * @returns {HTMLElement} Options container element
     */
    createOptionsDiv(options) {
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'mt-3 space-y-2';
        
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-button w-full p-2 text-left hover:bg-cyan-100 rounded-lg border border-cyan-200 transition-colors';
            button.textContent = option;
            button.onclick = () => {
                this.handleOptionClick(option, optionsDiv);
            };
            optionsDiv.appendChild(button);
        });
        
        return optionsDiv;
    }

    /**
     * Handles option button clicks
     * @param {string} option - Selected option text
     * @param {HTMLElement} optionsDiv - Container of option buttons
     */
    handleOptionClick(option, optionsDiv) {
        // Disable all buttons in the options div
        optionsDiv.querySelectorAll('button').forEach(btn => {
            btn.disabled = true;
            btn.className += ' disabled';
        });
        
        // Trigger custom event for option selection
        const event = new CustomEvent('optionSelected', { detail: option });
        document.dispatchEvent(event);
    }

    /**
     * Scrolls the chat container to the bottom
     */
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    /**
     * Shows or hides the timer warning
     * @param {boolean} show - Whether to show or hide the warning
     */
    toggleTimerWarning(show) {
        this.timerWarning.classList.toggle('hidden', !show);
    }

    /**
     * Updates the status indicator text
     * @param {string} status - New status text
     */
    updateStatus(status) {
        this.statusIndicator.textContent = status;
    }

    /**
     * Enables or disables the input and send button
     * @param {boolean} enabled - Whether to enable or disable
     */
    setInputEnabled(enabled) {
        this.userInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        if (enabled) {
            this.userInput.focus();
        }
    }

    /**
     * Clears the chat messages container
     */
    clearMessages() {
        this.messagesContainer.innerHTML = '';
    }

    /**
     * Shows an error message in the chat
     * @param {string} message - Error message to display
     */
    showError(message = SYSTEM_MESSAGES.ERROR) {
        this.appendMessage('bot', message);
    }

    /**
     * Gets the current input value and clears it
     * @returns {string} Current input value
     */
    getAndClearInput() {
        const value = this.userInput.value.trim();
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        return value;
    }

    /**
     * Adds resource cards to a message
     * @param {Array} resources - Array of resource objects
     * @returns {string} HTML string for resources
     */
    formatResourceCards(resources) {
        return resources.map(resource => `
            <div class="resource-card">
                <div class="font-medium">${resource.title}</div>
                <div class="text-sm text-gray-600">${resource.description}</div>
                <a href="${resource.url}" target="_blank" class="text-cyan-600 hover:text-cyan-800 text-sm">
                    En savoir plus →
                </a>
            </div>
        `).join('');
    }
}

// Export une instance unique du service UI
export const uiService = new UIService();