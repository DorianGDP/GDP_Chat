from config import config
from app import app_instance
import re
from typing import Tuple, Optional, List
from unidecode import unidecode
from config import config

class DataValidator:
    """Validation des données extraites des messages utilisateur."""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, Optional[str]]:
        """Valide un nom ou prénom.
        
        Args:
            name (str): Le nom à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        name = name.strip()
        
        if len(name) < 2:
            return False, "Le nom semble trop court. Pourriez-vous le vérifier ?"
            
        if len(name) > 50:
            return False, "Le nom semble trop long. Pourriez-vous le vérifier ?"
            
        if not re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\- ']*$", name):
            return False, "Le nom contient des caractères non autorisés. Pourriez-vous le vérifier ?"
            
        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Valide une adresse email.
        
        Args:
            email (str): L'email à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return True, None
        return False, "L'adresse email n'est pas valide. Pourriez-vous la vérifier ?"

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Valide un numéro de téléphone français.
        
        Args:
            phone (str): Le numéro à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        # Nettoyage du numéro
        cleaned_phone = re.sub(r'[\s.-]', '', phone)
        
        # Accepte les formats: +33612345678, 0612345678
        if re.match(r'^(\+33|0)[1-9][0-9]{8}$', cleaned_phone):
            return True, None
        return False, "Le numéro de téléphone n'est pas valide. Pourriez-vous le vérifier ?"

    @staticmethod
    def validate_age(age: int) -> Tuple[bool, Optional[str]]:
        """Valide l'âge d'une personne.
        
        Args:
            age (int): L'âge à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        if isinstance(age, int) and 18 <= age <= 120:
            return True, None
        return False, "L'âge doit être compris entre 18 et 120 ans."

    @staticmethod
    def validate_situation_familiale(situation: str) -> Tuple[bool, Optional[str]]:
        """Valide et normalise la situation familiale.
        
        Args:
            situation (str): La situation familiale à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, situation_normalisée)
        """
        # Mapping des situations valides
        situations_mapping = {
            'celibataire': 'célibataire',
            'célibataire': 'célibataire',
            'marie': 'marié(e)',
            'mariee': 'marié(e)',
            'marié': 'marié(e)',
            'mariée': 'marié(e)',
            'pacse': 'pacsé(e)',
            'pacsee': 'pacsé(e)',
            'pacsé': 'pacsé(e)',
            'pacsée': 'pacsé(e)',
            'divorce': 'divorcé(e)',
            'divorcee': 'divorcé(e)',
            'divorcé': 'divorcé(e)',
            'divorcée': 'divorcé(e)',
            'veuf': 'veuf/veuve',
            'veuve': 'veuf/veuve'
        }
        
        # Normalisation de l'entrée
        normalized_input = unidecode(situation.lower().strip())
        
        # Vérification de la correspondance
        for key, value in situations_mapping.items():
            if normalized_input in unidecode(key):
                return True, value
                
        return False, "Veuillez choisir parmi : célibataire, marié(e), pacsé(e), divorcé(e), veuf/veuve"

    @staticmethod
    def validate_profession(profession: str) -> Tuple[bool, Optional[str]]:
        """Valide la profession par rapport aux options disponibles.
        
        Args:
            profession (str): La profession à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        if profession in config.PROFESSIONS:
            return True, None
        return False, f"Veuillez choisir parmi les professions suivantes :\n{', '.join(config.PROFESSIONS)}"

    @staticmethod
    def validate_revenu(revenu: str) -> Tuple[bool, Optional[str]]:
        """Valide la tranche de revenu par rapport aux options disponibles.
        
        Args:
            revenu (str): La tranche de revenu à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        if revenu in config.REVENUS:
            return True, None
        return False, f"Veuillez choisir parmi les tranches suivantes :\n{', '.join(config.REVENUS)}"

    @staticmethod
    def validate_patrimoine(patrimoine: str) -> Tuple[bool, Optional[str]]:
        """Valide la tranche de patrimoine par rapport aux options disponibles.
        
        Args:
            patrimoine (str): La tranche de patrimoine à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        if patrimoine in config.PATRIMOINE:
            return True, None
        return False, f"Veuillez choisir parmi les tranches suivantes :\n{', '.join(config.PATRIMOINE)}"

    @staticmethod
    def validate_objectifs(objectifs: List[str]) -> Tuple[bool, Optional[str]]:
        """Valide les objectifs patrimoniaux par rapport aux options disponibles.
        
        Args:
            objectifs (List[str]): La liste des objectifs à valider
            
        Returns:
            Tuple[bool, Optional[str]]: (est_valide, message_erreur)
        """
        if not objectifs:
            return False, "Veuillez sélectionner au moins un objectif."
            
        invalid_objectives = [obj for obj in objectifs if obj not in config.OBJECTIFS]
        if invalid_objectives:
            return False, f"Les objectifs suivants ne sont pas valides : {', '.join(invalid_objectives)}\nVeuillez choisir parmi : {', '.join(config.OBJECTIFS)}"
            
        return True, None

def format_phone_number(phone: str) -> str:
    """Formate un numéro de téléphone en format standard français.
    
    Args:
        phone (str): Le numéro à formater
        
    Returns:
        str: Le numéro formaté
    """
    # Nettoyage du numéro
    cleaned = re.sub(r'[\s.-]', '', phone)
    
    # Conversion du format international vers le format national
    if cleaned.startswith('+33'):
        cleaned = '0' + cleaned[3:]
    
    # Format XX XX XX XX XX
    return ' '.join([cleaned[i:i+2] for i in range(0, len(cleaned), 2)])

def normalize_string(text: str) -> str:
    """Normalise une chaîne de caractères (retire les accents, met en minuscules).
    
    Args:
        text (str): Le texte à normaliser
        
    Returns:
        str: Le texte normalisé
    """
    return unidecode(text.lower().strip())