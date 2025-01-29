import os
from openai import OpenAI
from config import config

def create_app():
    """Initialize and configure the application"""
    # Ensure instance folder exists
    os.makedirs(os.path.join(config.BASE_DIR, 'instance'), exist_ok=True)
    
    # Ensure embeddings_db folder exists
    os.makedirs(config.EMBEDDINGS_DIR, exist_ok=True)
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    # Import components after app creation to avoid circular imports
    from .models import DatabaseHandler
    from .chat_handler import WealthChatbot
    
    # Initialize database
    db = DatabaseHandler()
    db.create_tables()
    
    return {
        'openai_client': openai_client,
        'db': db,
        'chatbot': WealthChatbot(openai_client)
    }

# Import routes and models to make them available when importing the package
from . import routes
from . import models
from . import chat_handler
from . import utils

# Create and configure app instance
app_instance = create_app()