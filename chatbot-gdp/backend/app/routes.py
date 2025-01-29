from flask import current_app, request, jsonify
from . import app  # Import de l'instance app

@app.route('/api/chat', methods=['POST'])
def chat():
    chatbot = current_app.chatbot
    try:
        data = request.get_json()
        question = data.get('question')
        conversation_id = data.get('conversation_id')
        
        # Traitement du message avec le chatbot
        response = chatbot.process_message(question)
        
        return jsonify({
            'content': response,
            'conversation_id': conversation_id,
            'status': 'en_cours'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://doriangdp.github.io')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Ajoutez les autres routes nécessaires
@app.route('/api/check_timeout', methods=['POST'])
def check_timeout():
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        # Logique de vérification du timeout
        return jsonify({'timeout': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/end_conversation', methods=['POST'])
def end_conversation():
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        status = data.get('status')
        # Logique de fin de conversation
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_conversation', methods=['POST'])
def reset_conversation():
    try:
        data = request.get_json()
        old_conversation_id = data.get('old_conversation_id')
        # Logique de réinitialisation
        return jsonify({
            'success': True,
            'new_conversation_id': 'new_id'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500