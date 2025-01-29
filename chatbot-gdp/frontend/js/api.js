import { API_CONFIG, CONVERSATION_STATUS } from './config.js';

class ApiService {
    /**
     * Service de gestion des appels API
     */
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
        this.headers = API_CONFIG.DEFAULT_HEADERS;
    }

    /**
     * Envoie un message au chatbot
     * @param {string} message - Message de l'utilisateur
     * @param {string} conversationId - ID de la conversation
     * @returns {Promise<Object>} Réponse du chatbot
     */
    async sendMessage(message, conversationId) {
        try {
            const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.CHAT}`, {
                method: 'POST',
                headers: this.headers,
                credentials: 'include',
                body: JSON.stringify({
                    question: message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending message:', error);
            throw new Error('Failed to send message');
        }
    }

    /**
     * Vérifie le timeout de la conversation
     * @param {string} conversationId - ID de la conversation
     * @returns {Promise<Object>} Statut du timeout
     */
    async checkTimeout(conversationId) {
        try {
            const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.CHECK_TIMEOUT}`, {
                method: 'POST',
                headers: this.headers,
                credentials: 'include',
                body: JSON.stringify({ conversation_id: conversationId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error checking timeout:', error);
            return { timeout: false };
        }
    }

    /**
     * Termine une conversation
     * @param {string} conversationId - ID de la conversation
     * @param {string} status - Statut de fin de conversation
     * @returns {Promise<boolean>} Succès de l'opération
     */
    async endConversation(conversationId, status = CONVERSATION_STATUS.NON_TERMINEE) {
        try {
            const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.END_CONVERSATION}`, {
                method: 'POST',
                headers: this.headers,
                credentials: 'include',
                body: JSON.stringify({
                    conversation_id: conversationId,
                    status: status
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return true;
        } catch (error) {
            console.error('Error ending conversation:', error);
            return false;
        }
    }

    /**
     * Réinitialise une conversation
     * @param {string} oldConversationId - ID de l'ancienne conversation
     * @returns {Promise<Object>} Nouvelle configuration de conversation
     */
    async resetConversation(oldConversationId) {
        try {
            const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.RESET_CONVERSATION}`, {
                method: 'POST',
                headers: this.headers,
                credentials: 'include',
                body: JSON.stringify({
                    old_conversation_id: oldConversationId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error resetting conversation:', error);
            throw new Error('Failed to reset conversation');
        }
    }

    /**
     * Gère les erreurs de requête API
     * @param {Response} response - Réponse de l'API
     * @returns {Promise<Object>} Données de l'erreur
     */
    async handleRequestError(response) {
        let errorData = {
            status: response.status,
            message: 'Une erreur est survenue'
        };

        try {
            const data = await response.json();
            errorData.message = data.message || errorData.message;
        } catch (e) {
            console.error('Error parsing error response:', e);
        }

        return errorData;
    }

    /**
     * Vérifie la connexion au serveur
     * @returns {Promise<boolean>} État de la connexion
     */
    async checkConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: this.headers
            });

            return response.ok;
        } catch (error) {
            console.error('Server connection error:', error);
            return false;
        }
    }
}

// Export une instance unique du service API
export const apiService = new ApiService();