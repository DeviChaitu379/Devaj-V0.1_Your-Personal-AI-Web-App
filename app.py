from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import openai
from collections import deque
import tiktoken
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for sessions

#API
openai.api_base = "https://localhost:5000/v1"
openai.api_key = "not-needed"

# Store chat histories in memory (Databases might be used in future applications/upgrade in upcoming repos)
chat_sessions = {}

# Store user accounts (Proper account management will also be implemented in future repos)
users = {
    "admin": {
        "password": generate_password_hash("123"),
        "chats": {}
    }
}


# Maximum number of tokens to remember per chat
MAX_TOKENS_PER_CHAT = 4000  # Adjust this value as needed

tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(tokenizer.encode(text))

def trim_conversation_history(history, max_tokens):
    token_count = 0
    trimmed_history = deque()
    
    for message in reversed(history):
        message_tokens = count_tokens(message['content'])
        if token_count + message_tokens > max_tokens:
            break
        token_count += message_tokens
        trimmed_history.appendleft(message)
    
    return list(trimmed_history)

def create_chat_completion(user_input, system_message, chat_history):
    chat_history.append({"role": "user", "content": user_input})
    trimmed_history = trim_conversation_history(chat_history, MAX_TOKENS_PER_CHAT)
    
    response = openai.ChatCompletion.create(
        model="your_model_api_identifier",
        messages=[{"role": "system", "content": system_message}] + trimmed_history,
        temperature=0.8,
        stream=True,
    )
    
    def generate():
        response_text = ""
        for chunk in response:
            if 'choices' in chunk:
                chunk_message = chunk['choices'][0]['delta'].get('content', '')
                response_text += chunk_message
                yield chunk_message
        chat_history.append({"role": "assistant", "content": response_text})
    
    return generate()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    username = session['username']
    return render_template('index.html', chats=list(users[username]['chats'].keys()))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Invalid username or password"}), 401
    return render_template('login-page.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/new_chat', methods=['POST'])
@login_required
def new_chat():
    username = session['username']
    chat_id = str(len(users[username]['chats']) + 1)  
    users[username]['chats'][chat_id] = {
        'messages': [],
        'name': f'Chat {chat_id}'
    }
    return jsonify({
        "chat_id": chat_id,
        "chat_name": f'Chat {chat_id}',
        "chats": {k: v['name'] for k, v in users[username]['chats'].items()}
    })

@app.route('/get_chat/<chat_id>', methods=['GET'])
@login_required
def get_chat(chat_id):
    username = session['username']
    if chat_id in users[username]['chats']:
        return jsonify({
            "chat_name": users[username]['chats'][chat_id]['name'],
            "chat_history": users[username]['chats'][chat_id]['messages']
        })
    return jsonify({"error": "Chat not found"}), 404

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    username = session['username']
    data = request.json
    chat_id = str(data.get('chat_id'))
    user_input = data.get('user_input')
    
    if chat_id not in users[username]['chats']:
        return jsonify({"error": "Chat not found"}), 404

    system_message = (
        "The name of the user will be told by the user if you ask them or if they say it themselves. You are the assistant or chatbot and your name is Devaj. "
        "You were created by Rui also known by the name Chaitu. "
        "Always refer to the user as the name specified by them if they mention or if you ask. Keep all responses brief and concise. "
        "You, the assistant, are an expert in Chatting, roleplaying, coding, or even summarizing, etc., that normally a Language AI model can do. "
        "Your primary job and role as the ASSISTANT is to help the user in their daily life tasks which you can do so in the chat window, but maybe there might be a chance you could be a moving Robot one day if Rui/Chaitu Develops you further. "
        "Emphasize honesty, candor, and precision. Avoid speculation except when explicitly prompted to. "
        "Maintain a friendly, respectful, and professional tone. Politely correct me if I am wrong and give evidence-based facts. Never lecture me too much."
    )

    chat_history = users[username]['chats'][chat_id]['messages']
    return app.response_class(create_chat_completion(user_input, system_message, chat_history), mimetype='text/event-stream')

@app.route('/delete_chat/<chat_id>', methods=['POST'])
@login_required
def delete_chat(chat_id):
    username = session['username']
    if chat_id in users[username]['chats']:
        del users[username]['chats'][chat_id]
        return jsonify({"status": "Chat deleted", "chats": {k: v['name'] for k, v in users[username]['chats'].items()}})
    return jsonify({"error": "Chat not found"}), 404

@app.route('/rename_chat/<chat_id>', methods=['POST'])
@login_required
def rename_chat(chat_id):
    username = session['username']
    data = request.json
    new_name = data.get('name')
    
    if chat_id in users[username]['chats']:
        if new_name:
            users[username]['chats'][chat_id]['name'] = new_name
            return jsonify({"status": "Chat renamed", "chats": {k: v['name'] for k, v in users[username]['chats'].items()}})
        return jsonify({"error": "New name is required"}), 400
    
    return jsonify({"error": "Chat not found"}), 404

@app.route('/restart_chat/<int:chat_id>', methods=['POST'])
@login_required
def restart_chat(chat_id):
    username = session['username']
    if str(chat_id) in users[username]['chats']:
        users[username]['chats'][str(chat_id)]['messages'] = []
        return jsonify({"status": "Chat session restarted"})
    return jsonify({"error": "Chat not found"}), 404

@app.route('/restart_session', methods=['POST'])
@login_required
def restart_session():
    username = session['username']
    users[username]['chats'] = {}
    return jsonify({"status": "All chat sessions restarted"})

@app.route('/list_chats', methods=['GET'])
@login_required
def list_chats():
    username = session['username']
    return jsonify({"chats": {k: v['name'] for k, v in users[username]['chats'].items()}})

@app.route('/test_openai', methods=['GET'])
def test_openai():
    try:
        response = openai.Model.list()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
