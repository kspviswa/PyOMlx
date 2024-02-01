import json
from flask import Flask, jsonify, request
from prompt import firePrompt

app = Flask(__name__)

@app.route('/serve', methods=['POST'])
def serve():
    data = request.get_json()
    result = firePrompt(model=data['model'], prompt=data['prompt'])
    return result

@app.route('/')
def index():
    return jsonify({'name': 'alice',
                    'email': 'alice@outlook.com'})

app.run()