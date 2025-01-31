from config import config
from app import app_instance
import os
import json
import uuid
from datetime import datetime
import faiss
import numpy as np
from config import config
from .models import Lead, DatabaseHandler
from .untils import DataValidator

class WealthChatbot:
    def __init__(self, openai_client):
        self.client = client
        conversation_id = str(uuid.uuid4())
        self.lead = Lead(conversation_id=conversation_id)
        self.conversation_history = []
        self.validator = DataValidator()
        self.db = DatabaseHandler()
        self.conversation_ended = False
        self.MAX_MESSAGES = config.MAX_MESSAGES
        
        # Initialize RAG components
        self.index = faiss.read_index(config.FAISS_INDEX_PATH)
        with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

    def _get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for the query using OpenAI's API"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        return np.array(response.data[0].embedding, dtype='float32').reshape(1, -1)

    def _search_relevant_content(self, profile_summary: str, k: int = 3) -> list:
        """Search for relevant content based on the user's profile"""
        query_embedding = self._get_query_embedding(profile_summary)
        D, I = self.index.search(query_embedding, k)
        
        relevant_docs = []
        for idx in I[0]:
            relevant_docs.append(self.metadata[idx])
            
        return relevant_docs

    def _extract_information(self, user_message: str) -> dict:
        """Extrait les informations structurées du message utilisateur."""
        conversation_context = "\n".join([
            msg["content"] for msg in self.conversation_history[-3:]
        ])
        
        missing_fields = self.lead.get_missing_fields()
        current_field = missing_fields[0] if missing_fields else 'commentaire'
        
        if not missing_fields and self.lead.commentaire is None and "Avant de faire un bilan complet" in conversation_context:
            return {"commentaire": user_message}
            
        messages = [
            {"role": "system", "content": f"""Vous êtes un expert en extraction d'informations précises.
            Votre tâche est d'extraire spécifiquement les informations demandées du message de l'utilisateur.
            
            Contexte de la conversation:
            {conversation_context}
            
            Champ actuellement demandé: {current_field}"""},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                functions=[{
                    "name": "extract_lead_info",
                    "description": "Extrait et valide les informations du prospect",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nom": {"type": "string"},
                            "prenom": {"type": "string"},
                            "email": {"type": "string"},
                            "telephone": {"type": "string"},
                            "age": {"type": "integer"},
                            "situation_familiale": {"type": "string"},
                            "profession": {"type": "string"},
                            "revenu_annuel": {"type": "number"},
                            "patrimoine_actuel": {
                                "type": "object",
                                "properties": {
                                    "montant": {"type": "number"},
                                    "details": {"type": "string"}
                                }
                            },
                            "objectifs_patrimoniaux": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }],
                function_call={"name": "extract_lead_info"}
            )

            if current_field in ['nom', 'prenom'] and user_message.strip().isalpha():
                extracted_data = {current_field: user_message.strip()}
            else:
                function_response = response.choices[0].message.function_call.arguments
                extracted_data = json.loads(function_response)

            return self._validate_extracted_data(extracted_data)

        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            return {}

    def _validate_extracted_data(self, extracted_data: dict) -> dict:
        """Valide les données extraites et retourne les données validées."""
        validated_data = {}
        for key, value in extracted_data.items():
            if value is not None:
                if key in ['nom', 'prenom']:
                    is_valid, _ = self.validator.validate_name(value)
                    if is_valid:
                        validated_data[key] = value.capitalize()
                elif key == "email":
                    is_valid, _ = self.validator.validate_email(value)
                    if is_valid:
                        validated_data[key] = value.lower()
                elif key == "telephone":
                    is_valid, _ = self.validator.validate_phone(value)
                    if is_valid:
                        validated_data[key] = value
                elif key == "age":
                    is_valid, _ = self.validator.validate_age(value)
                    if is_valid:
                        validated_data[key] = value
                elif key == "situation_familiale":
                    is_valid, correct_value = self.validator.validate_situation_familiale(value)
                    if is_valid:
                        validated_data[key] = correct_value
                elif key == "patrimoine_actuel":
                    if isinstance(value, dict) and "montant" in value:
                        validated_data[key] = value["montant"]
                elif key == "objectifs_patrimoniaux":
                    if isinstance(value, list):
                        validated_data[key] = value
                else:
                    validated_data[key] = value

        return validated_data

    def _generate_next_question(self) -> str:
        """Génère la prochaine question basée sur les champs manquants."""
        missing_fields = self.lead.get_missing_fields()
        if not missing_fields:
            return self._generate_completion_message()

        next_field = missing_fields[0]
        field_prompts = {
            'profession': f"Quelle est votre situation professionnelle actuelle ?\n{self._format_options(config.PROFESSIONS)}",
            'revenu_annuel': f"Dans quelle tranche se situe votre revenu annuel ?\n{self._format_options(config.REVENUS)}",
            'patrimoine_actuel': f"Dans quelle tranche se situe votre patrimoine global ?\n{self._format_options(config.PATRIMOINE)}",
            'situation_familiale': f"Quelle est votre situation familiale ?\n{self._format_options(config.SITUATION_FAMILIALE)}",
            'objectifs_patrimoniaux': f"Quels sont vos principaux objectifs patrimoniaux ? (plusieurs choix possibles)\n{self._format_options(config.OBJECTIFS)}"
        }

        return field_prompts.get(next_field, self._generate_default_question(next_field))

    def _generate_default_question(self, field: str) -> str:
        """Génère une question par défaut pour un champ donné."""
        questions = {
            'nom': "Pour commencer notre échange, puis-je avoir votre nom de famille ?",
            'prenom': f"Merci. Et votre prénom ?",
            'email': "À quelle adresse email puis-je vous envoyer nos recommandations ?",
            'telephone': "Quel est votre numéro de téléphone pour vous recontacter ?",
            'age': "Quel âge avez-vous ?"
        }
        return questions.get(field, f"Pouvez-vous me communiquer votre {field} ?")

    def _format_options(self, options: list) -> str:
        """Formate une liste d'options pour l'affichage."""
        return "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])

    def _generate_completion_message(self) -> str:
        """Génère le message de conclusion avec recommandations."""
        result = self._analyze_profile()
        
        content_recommendations = "\nRessources recommandées :"
        for doc in result["relevant_content"]:
            content_type = "📈 Simulateur" if "simulateur" in doc["title"].lower() else "📗 Guide" if "guide" in doc["title"].lower() else "📄 Article"
            content_recommendations += f"\n{content_type} : {doc['title']} \n→ {doc['url']}"

        return f"""Synthèse de votre situation :

            {result['analysis']}

            {content_recommendations}

            Un conseiller vous contactera prochainement au {self.lead.telephone} pour approfondir ces recommandations.
            """

    def _analyze_profile(self) -> dict:
        """Analyse le profil utilisateur et génère des recommandations."""
        profile_summary = self._generate_profile_summary()
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en gestion de patrimoine."},
                    {"role": "user", "content": profile_summary}
                ]
            )
            
            analysis = response.choices[0].message.content
            relevant_docs = self._search_relevant_content(analysis)
            
            return {
                "analysis": analysis,
                "relevant_content": relevant_docs
            }
        except Exception as e:
            print(f"Error in profile analysis: {str(e)}")
            return {
                "analysis": "Une erreur est survenue lors de l'analyse.",
                "relevant_content": []
            }

    def _generate_profile_summary(self) -> str:
        """Génère un résumé du profil pour l'analyse."""
        return f"""Analysez ce profil :
        - Âge: {self.lead.age} ans
        - Situation: {self.lead.situation_familiale}
        - Profession: {self.lead.profession}
        - Revenu: {self.lead.revenu_annuel}
        - Patrimoine: {self.lead.patrimoine_actuel}
        - Objectifs: {', '.join(self.lead.objectifs_patrimoniaux) if isinstance(self.lead.objectifs_patrimoniaux, list) else self.lead.objectifs_patrimoniaux}
        - Commentaire: {self.lead.commentaire}
        
        Fournissez une analyse concise avec des recommandations personnalisées."""

    def process_message(self, user_message: str) -> str:
        """Traite un message utilisateur et retourne la réponse du chatbot."""
        # Vérification du nombre maximum de messages
        self.lead.message_count += 1
        if self.lead.message_count > self.MAX_MESSAGES or self.conversation_ended:
            return "La conversation est terminée. Pour toute question supplémentaire, veuillez nous contacter au 01 59 20 06 76."

        # Ajout du message à l'historique
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": user_message
        }
        self.lead.conversation_history.append(message_entry)
        self.conversation_history.append({"role": "user", "content": user_message})

        # Extraction et traitement des informations
        extracted_info = self._extract_information(user_message)
        info_updated = False

        # Mise à jour des informations du lead
        for key, value in extracted_info.items():
            if value is not None:
                setattr(self.lead, key, value)
                info_updated = True

        try:
            self.db.save_lead(self.lead)
        except Exception as e:
            print(f"Warning: Could not save to database: {str(e)}")

        # Génération de la réponse appropriée
        if not info_updated:
            response = self._generate_next_question()
        elif self.lead.is_complete():
            if not self.lead.commentaire:
                response = """
                Merci pour toutes ces informations. Avant de faire un bilan complet,
                pourriez-vous me décrire brièvement vos attentes ou questions particulières ?
                """
            else:
                response = self._generate_completion_message()
                self.conversation_ended = True
        else:
            response = self._generate_next_question()

        # Ajout de la réponse à l'historique
        bot_response = {
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response
        }
        self.lead.conversation_history.append(bot_response)
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def __del__(self):
        """Destructeur pour assurer la fermeture de la connexion à la base de données."""
        if hasattr(self, 'db'):
            self.db.close()
