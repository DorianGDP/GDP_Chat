import { CHAT_CONFIG, SYSTEM_MESSAGES, CONVERSATION_STATUS } from './config.js';
import { apiService } from './api.js';
import { uiService } from './ui.js';

class ChatController {
    constructor() {
        this.conversationId = this.getConversationId();
        this.timeoutTimer = null;
        this.warningTimer = null;
        this.conversationStartTime = null;
        
        // Bind event handlers
        this.handleSendMessage = this.handleSendMessage.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.handleReset = this.handleReset.bind(this);
        this.handlePageUnload = this.handlePageUnload.bind(this);
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Start chat
        this.initialize();
    }
    
    /**
     * Initialize chat and event listeners
     */
    initializeEventListeners() {
        // UI event listeners
        uiService.sendButton.addEventListener('click', this.handleSendMessage);
        uiService.userInput.addEventListener('keypress', this.handleKeyPress);
        uiService.resetButton.addEventListener('click', this.handleReset);
        
        // Window event listeners
        window.addEventListener('beforeunload', this.handlePageUnload);
        window.addEventListener('storage', this.handleStorageChange.bind(this));
        
        // Check timeout periodically
        setInterval(this.checkTimeout.bind(this), CHAT_CONFIG.CHECK_TIMEOUT_INTERVAL);
    }
    
    /**
     * Initialize the chat interface
     */
    initialize() {
        this.resetTimers();
        this.showWelcomeMessage();
    }
    
    /**
     * Reset conversation timers
     */
    resetTimers() {
        clearTimeout(this.timeoutTimer);
        clearTimeout(this.warningTimer);
        
        this.conversationStartTime = Date.now();
        
        this.warningTimer = setTimeout(() => {
            uiService.toggleTimerWarning(true);
        }, CHAT_CONFIG.CONVERSATION_TIMEOUT - CHAT_CONFIG.WARNING_TIME);
        
        this.timeoutTimer = setTimeout(
            this.handleConversationTimeout.bind(this), 
            CHAT_CONFIG.CONVERSATION_TIMEOUT
        );
    }
    
    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        uiService.appendMessage('bot', SYSTEM_MESSAGES.WELCOME);
        uiService.setInputEnabled(true);
    }
    
    /**
     * Generate or get conversation ID
     */
    getConversationId() {
        let id = localStorage.getItem('chatConversationId');
        if (!id) {
            id = 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chatConversationId', id);
        }
        return id;
    }
    
    /**
     * Handle send button click
     */
    async handleSendMessage() {
        const message = uiService.getAndClearInput();
        if (!message) return;
        
        uiService.setInputEnabled(false);
        
        try {
            // Display user message
            uiService.appendMessage('user', message);
            
            // Show typing indicator
            const typingIndicator = uiService.createTypingIndicator();
            uiService.messagesContainer.appendChild(typingIndicator);
            
            // Send message to API
            const response = await apiService.sendMessage(message, this.conversationId);
            
            // Remove typing indicator
            typingIndicator.remove();
            
            // Handle response
            this.handleChatResponse(response);
            
        } catch (error) {
            console.error('Error sending message:', error);
            typingIndicator?.remove();
            uiService.showError();
            uiService.setInputEnabled(true);
        }
    }
    
    /**
     * Handle chat response from API
     */
    handleChatResponse(response) {
        // Update conversation ID if needed
        if (response.conversation_id && response.conversation_id !== this.conversationId) {
            this.conversationId = response.conversation_id;
            localStorage.setItem('chatConversationId', this.conversationId);
        }
        
        // Handle different conversation statuses
        switch (response.status) {
            case CONVERSATION_STATUS.TERMINEE:
                this.handleConversationEnded();
                break;
                
            case CONVERSATION_STATUS.NON_TERMINEE:
                this.handleConversationInterrupted();
                break;
                
            default:
                // Display bot response
                uiService.appendMessage('bot', response.content, response.options || []);
                
                // Enable input if no options are provided
                if (!response.options?.length) {
                    uiService.setInputEnabled(true);
                }
        }
    }
    
    /**
     * Handle conversation timeout
     */
    async handleConversationTimeout() {
        try {
            await apiService.endConversation(this.conversationId, CONVERSATION_STATUS.NON_TERMINEE);
            uiService.setInputEnabled(false);
            uiService.toggleTimerWarning(false);
            uiService.appendMessage('bot', SYSTEM_MESSAGES.TIMEOUT, ["Nouvelle conversation"]);
        } catch (error) {
            console.error('Timeout handling error:', error);
        }
    }
    
    /**
     * Handle conversation ended status
     */
    handleConversationEnded() {
        clearTimeout(this.timeoutTimer);
        clearTimeout(this.warningTimer);
        uiService.toggleTimerWarning(false);
        uiService.updateStatus('Conversation terminée');
        uiService.setInputEnabled(false);
    }
    
    /**
     * Handle conversation interrupted status
     */
    handleConversationInterrupted() {
        uiService.updateStatus('Conversation interrompue');
        uiService.appendMessage('bot', SYSTEM_MESSAGES.CONVERSATION_INTERRUPTED, ["Reprendre", "Nouvelle conversation"]);
    }
    
    /**
     * Handle key press events
     */
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSendMessage();
        }
    }
    
    /**
     * Reset conversation
     */
    async handleReset() {
        const oldConversationId = this.conversationId;
        this.conversationId = this.getConversationId();
        
        try {
            await apiService.endConversation(oldConversationId, CONVERSATION_STATUS.NON_TERMINEE);
        } catch (error) {
            console.warn('Error ending previous conversation:', error);
        }
        
        uiService.clearMessages();
        uiService.setInputEnabled(true);
        uiService.toggleTimerWarning(false);
        uiService.updateStatus('En ligne');
        
        this.resetTimers();
        this.showWelcomeMessage();
    }
    
    /**
     * Handle page unload
     */
    async handlePageUnload() {
        try {
            await apiService.endConversation(this.conversationId, CONVERSATION_STATUS.NON_TERMINEE);
            localStorage.removeItem('chatConversationId');
        } catch (error) {
            console.error('Error during page unload:', error);
        }
    }
    
    /**
     * Handle storage changes (for multi-tab support)
     */
    handleStorageChange(e) {
        if (e.key === 'chatConversationId') {
            this.conversationId = e.newValue || this.getConversationId();
        }
    }
    
    /**
     * Check conversation timeout
     */
    async checkTimeout() {
        try {
            const response = await apiService.checkTimeout(this.conversationId);
            if (response.timeout) {
                await this.handleConversationTimeout();
            }
        } catch (error) {
            console.error('Error checking timeout:', error);
        }
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatController();
});