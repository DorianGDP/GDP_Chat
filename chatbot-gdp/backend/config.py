import os

class Config:
    """Base configuration class."""
    # OpenAI API Settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-4o"
    
    # Chat Settings
    MAX_MESSAGES = 15
    
    # File Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'leads.db')
    EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings_db')
    FAISS_INDEX_PATH = os.path.join(EMBEDDINGS_DIR, 'faiss_index.idx')
    METADATA_PATH = os.path.join(EMBEDDINGS_DIR, 'metadata.json')
    
    # Category Options
    PROFESSIONS = [
        "Salarié du secteur privé",
        "Fonctionnaire",
        "Chef d'entreprise",
        "Profession libérale",
        "Indépendant / Auto-entrepreneur",
        "Retraité",
        "Autre"
    ]
    
    REVENUS = [
        "Moins de 30 000€",
        "30 000€ - 40 000€",
        "40 000€ - 60 000€",
        "60 000€ - 80 000€",
        "80 000€ - 100 000€",
        "100 000€ - 250 000€",
        "Plus de 250 000€"
    ]
    
    PATRIMOINE = [
        "Moins de 20 000€",
        "20 000€ - 50 000€",
        "50 000€ - 100 000€",
        "100 000€ - 250 000€",
        "250 000€ - 500 000€",
        "500 000€ - 1 000 000€",
        "1 000 000€ - 2 500 000€",
        "Plus de 2 500 000€"
    ]
    
    SITUATION_FAMILIALE = [
        "Célibataire",
        "Marié(e)",
        "Pacsé(e)",
        "Divorcé(e)",
        "Veuf/Veuve"
    ]
    
    OBJECTIFS = [
        "Obtenir des revenus complémentaires",
        "Investir en immobilier",
        "Développer mon patrimoine",
        "Réduire mes impôts",
        "Préparer ma retraite",
        "Protéger ma famille",
        "Transmettre mon patrimoine",
        "Placer ma trésorerie excédentaire",
        "Autre"
    ]

config = Config()