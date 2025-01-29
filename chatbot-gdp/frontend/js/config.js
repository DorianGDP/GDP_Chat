// Configuration de l'API
const API_CONFIG = {
    // URL de base de l'API
    BASE_URL: 'https://chatbot-gdp.onrender.com/api',
    
    // Points d'entrée de l'API
    ENDPOINTS: {
        CHAT: '/chat',
        CHECK_TIMEOUT: '/check_timeout',
        END_CONVERSATION: '/chat/end_conversation',
        RESET_CONVERSATION: '/reset_conversation'
    },
    
    // Headers par défaut pour les requêtes
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://doriangdp.github.io'
    }
};

// Configuration du chat
const CHAT_CONFIG = {
    // Durée maximale d'une conversation (en millisecondes)
    CONVERSATION_TIMEOUT: 2 * 60 * 60 * 1000, // 2 heures
    
    // Temps avant l'avertissement de fin de conversation
    WARNING_TIME: 5 * 60 * 1000, // 5 minutes
    
    // Nombre maximum de messages dans une conversation
    MAX_MESSAGES: 15,
    
    // Délai entre chaque vérification de timeout (en millisecondes)
    CHECK_TIMEOUT_INTERVAL: 60 * 1000, // 1 minute
    
    // Délai d'animation pour l'indicateur de frappe (en millisecondes)
    TYPING_ANIMATION_DURATION: 2000
};

// États possibles de la conversation
const CONVERSATION_STATUS = {
    EN_COURS: 'en_cours',
    TERMINEE: 'terminée',
    NON_TERMINEE: 'non_terminée'
};

// Messages système
const SYSTEM_MESSAGES = {
    WELCOME: `Bonjour ! 👋 Je suis Patty, votre assistante en gestion de patrimoine. 
             Je suis là pour répondre à vos questions et vous accompagner dans vos projets patrimoniaux. 
             Comment puis-je vous aider aujourd'hui ?`,
             
    TIMEOUT: "La conversation est terminée. Pour toute question supplémentaire, veuillez nous contacter au 01 59 20 06 76.",
    
    ERROR: "Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants.",
    
    CONVERSATION_ENDED: "La conversation est terminée. Souhaitez-vous en commencer une nouvelle ?",
    
    CONVERSATION_INTERRUPTED: "La conversation a été interrompue. Voulez-vous la reprendre ou en commencer une nouvelle ?",
    
    WARNING: "La conversation se terminera automatiquement dans 5 minutes"
};

// Options pour les bulles de messages
const MESSAGE_OPTIONS = {
    // Classes CSS pour les différents types de messages
    CLASSES: {
        CONTAINER: 'message-container message-animation',
        BOT: 'message-bot text-gray-800',
        USER: 'message-user text-white',
        TYPING: 'message-bot typing-indicator'
    },
    
    // Paramètres pour l'indicateur de frappe
    TYPING_INDICATOR: {
        DOT_COUNT: 3,
        DOT_CLASS: 'typing-dot'
    }
};

// Configuration des boutons d'options
const BUTTON_OPTIONS = {
    CLASSES: {
        DEFAULT: 'w-full p-2 text-left hover:bg-cyan-100 rounded-lg border border-cyan-200 transition-colors',
        DISABLED: 'opacity-50 cursor-not-allowed'
    },
    
    ACTIONS: {
        NEW_CONVERSATION: "Nouvelle conversation",
        RESUME: "Reprendre",
        SEND: "Envoyer"
    }
};

// Export des configurations
export {
    API_CONFIG,
    CHAT_CONFIG,
    CONVERSATION_STATUS,
    SYSTEM_MESSAGES,
    MESSAGE_OPTIONS,
    BUTTON_OPTIONS
};