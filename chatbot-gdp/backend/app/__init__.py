
from flask import Flask
from flask_cors import CORS
from openai import OpenAI
from config import config

def create_app():
    """Initialize and configure the application"""
    # Create Flask app
    app = Flask(__name__)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5000",
                "http://127.0.0.1:5000",
                "https://doriangdp.github.io"
            ],
            "supports_credentials": True,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize OpenAI client - Modified initialization
    openai_client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        # Remove the proxies parameter if it exists
    )
    
    # Initialize database
    from .models import DatabaseHandler
    db = DatabaseHandler()
    db.create_tables()
    
    # Initialize chatbot with the client
    from .chat_handler import WealthChatbot
    chatbot = WealthChatbot(openai_client)
    
    # Store instances in app context
    app.openai_client = openai_client
    app.db = db
    app.chatbot = chatbot

    # Register routes
    with app.app_context():
        from . import routes
    
    return app
