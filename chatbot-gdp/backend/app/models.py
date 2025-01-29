from config import config
from app import app_instance
import sqlite3
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict
from datetime import datetime
from config import config

@dataclass
class Lead:
    """Structure des données à collecter pour chaque prospect."""
    conversation_id: str 
    id: Optional[int] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    age: Optional[int] = None
    situation_familiale: Optional[str] = None
    profession: Optional[str] = None
    revenu_annuel: Optional[str] = None
    patrimoine_actuel: Optional[str] = None
    objectifs_patrimoniaux: Optional[List[str]] = None
    created_at: Optional[str] = None
    commentaire: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    message_count: int = field(default=0)

    def is_complete(self) -> bool:
        """Vérifie si toutes les informations requises ont été collectées."""
        required_fields = [
            'nom', 'prenom', 'email', 'telephone', 'age', 
            'situation_familiale', 'profession', 'revenu_annuel', 
            'patrimoine_actuel', 'objectifs_patrimoniaux'
        ]
        return all(getattr(self, field) is not None for field in required_fields)

    def get_missing_fields(self) -> List[str]:
        """Retourne la liste des champs manquants dans l'ordre de priorité."""
        required_fields = [
            'nom', 'prenom', 'email', 'telephone', 'age', 
            'situation_familiale', 'profession', 'revenu_annuel', 
            'patrimoine_actuel', 'objectifs_patrimoniaux'
        ]
        return [field for field in required_fields if getattr(self, field) is None]

    def to_dict(self) -> dict:
        """Convertit l'instance en dictionnaire pour la sauvegarde."""
        data = asdict(self)
        # Convertit les listes et objets complexes en JSON
        if isinstance(self.objectifs_patrimoniaux, list):
            data['objectifs_patrimoniaux'] = json.dumps(self.objectifs_patrimoniaux)
        if self.conversation_history:
            data['conversation_history'] = json.dumps(self.conversation_history)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Lead':
        """Crée une instance à partir d'un dictionnaire."""
        # Convertit les chaînes JSON en objets Python
        if 'objectifs_patrimoniaux' in data and isinstance(data['objectifs_patrimoniaux'], str):
            try:
                data['objectifs_patrimoniaux'] = json.loads(data['objectifs_patrimoniaux'])
            except json.JSONDecodeError:
                data['objectifs_patrimoniaux'] = None
                
        if 'conversation_history' in data and isinstance(data['conversation_history'], str):
            try:
                data['conversation_history'] = json.loads(data['conversation_history'])
            except json.JSONDecodeError:
                data['conversation_history'] = []
                
        return cls(**data)


class DatabaseHandler:
    """Gère les interactions avec la base de données SQLite."""
    
    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.conn = sqlite3.connect(config.DATABASE_PATH)
        self.create_tables()
        
    def create_tables(self):
        """Crée la table des leads si elle n'existe pas."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE,
            nom TEXT,
            prenom TEXT,
            email TEXT,
            telephone TEXT,
            age INTEGER,
            situation_familiale TEXT,
            profession TEXT,
            revenu_annuel TEXT,
            patrimoine_actuel TEXT,
            objectifs_patrimoniaux TEXT,
            commentaire TEXT,
            conversation_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0
        )
        ''')
        self.conn.commit()

    def _lead_exists(self, conversation_id: str) -> bool:
        """Vérifie si un lead existe déjà avec cet ID de conversation."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM leads WHERE conversation_id = ? LIMIT 1", 
            (conversation_id,)
        )
        return cursor.fetchone() is not None
    
    def save_lead(self, lead: Lead) -> bool:
        """Sauvegarde ou met à jour un lead dans la base de données."""
        try:
            cursor = self.conn.cursor()
            data = lead.to_dict()
            
            if self._lead_exists(lead.conversation_id):
                # Mise à jour d'un enregistrement existant
                fields = [f"{k} = ?" for k in data.keys() if k != 'id']
                values = [v for k, v in data.items() if k != 'id']
                values.append(lead.conversation_id)
                
                cursor.execute(f'''
                UPDATE leads 
                SET {", ".join(fields)}
                WHERE conversation_id = ?
                ''', values)
            else:
                # Insertion d'un nouvel enregistrement
                fields = [k for k in data.keys() if k != 'id']
                placeholders = ["?" for _ in fields]
                values = [data[k] for k in fields]
                
                cursor.execute(f'''
                INSERT INTO leads 
                ({", ".join(fields)})
                VALUES ({", ".join(placeholders)})
                ''', values)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du lead: {str(e)}")
            self.conn.rollback()
            return False
            
    def get_lead(self, conversation_id: str) -> Optional[Lead]:
        """Récupère un lead par son ID de conversation."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM leads 
            WHERE conversation_id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        if row:
            # Convertit le résultat en dictionnaire
            columns = [description[0] for description in cursor.description]
            data = dict(zip(columns, row))
            return Lead.from_dict(data)
        return None

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Assure la fermeture de la connexion lors de la destruction de l'instance."""
        self.close()