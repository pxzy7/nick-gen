from flask import Flask, render_template, request, jsonify
import json
import os
import threading
from nick_generator import generate_and_check_async, get_log_buffer  # mantenha se precisar

app = Flask(__name__)

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

@app.route('/log-stream')
def log_stream():
    return get_log_buffer()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
