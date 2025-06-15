from flask import Flask, render_template, request, jsonify, send_file
import threading
import os
from nick_generator import generate_and_check_async, get_latest_output_file, get_log_buffer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    thread = threading.Thread(target=generate_and_check_async, args=(data,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/latest-nicks')
def latest_nicks():
    file_path = get_latest_output_file()
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False)
    return "No file found", 404

@app.route('/log-stream')
def log_stream():
    return get_log_buffer(), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True, port=6942)
