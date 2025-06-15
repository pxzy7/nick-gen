from flask import Flask, render_template, request, jsonify
import json
import os
import threading
from nick_generator import (
    generate_and_check_async,
    get_log_buffer,
    stop_generation,
    generation_status
)

app = Flask(__name__)

# ------------------- Funções auxiliares -------------------

def load_saved_nicks():
    try:
        with open('saved_nicks.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_nick(nick):
    nicks = load_saved_nicks()
    if nick not in nicks:
        nicks.append(nick)
        with open('saved_nicks.json', 'w') as file:
            json.dump(nicks, file)

# ------------------- Rotas principais ---------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/saved-nicks')
def saved_nicks():
    nicks = load_saved_nicks()
    return render_template('saved_nicks.html', nicks=nicks)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    thread = threading.Thread(target=generate_and_check_async, args=(data,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    stop_generation()
    return jsonify({"status": "stopping"})
    
@app.route('/status')
def status():
    from nick_generator import generation_status
    return jsonify({"is_generating": generation_status()})

@app.route('/log-stream')
def log_stream():
    return get_log_buffer()

# ------------------- Inicializador ---------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
