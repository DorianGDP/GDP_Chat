import os
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
                "http://localhost:5000",  # Development
                "http://127.0.0.1:5000",  # Development
                "https://doriangdp.github.io"  # Production
            ],
            "supports_credentials": True,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Ensure instance folder exists
    os.makedirs(os.path.join(config.BASE_DIR, 'instance'), exist_ok=True)
    
    # Ensure embeddings_db folder exists
    os.makedirs(config.EMBEDDINGS_DIR, exist_ok=True)
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # Initialize database
    from .models import DatabaseHandler
    db = DatabaseHandler()
    db.create_tables()
    
    # Initialize chatbot
    from .chat_handler import WealthChatbot
    chatbot = WealthChatbot(openai_client)
    
    # Store instances in app context
    app.openai_client = openai_client
    app.db = db
    app.chatbot = chatbot

    # Register routes
    with app.app_context():
        from . import routes

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Create app instance
app = create_app()
