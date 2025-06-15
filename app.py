from flask import Flask, render_template, request, jsonify
import json
import os
import threading
import time
from your_generator_module import generate_and_check_async, get_log_buffer  # ajuste isso se necessário

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    thread = threading.Thread(target=generate_and_check_async, args=(data,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/log-stream')
def log_stream():
    return get_log_buffer()

# Se quiser rota pra ver os nicks salvos
@app.route('/saved-nicks')
def saved_nicks():
    try:
        with open("nicks_log.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
