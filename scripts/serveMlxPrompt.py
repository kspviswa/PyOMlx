import json
from flask import Flask, jsonify, request
from mlx_lm import load, generate
import os
from pathlib import Path

DEFAULT_HF_MLX_MODEL_REGISTRY = Path("~/.cache/huggingface/hub/").expanduser()

def firePrompt(model: str, prompt: str, temp=0.3):
    model_dir = f'{DEFAULT_HF_MLX_MODEL_REGISTRY}/models--mlx-community--{model}'
    model_digest = ""
    with open(f'{model_dir}/refs/main', 'r') as f:
        model_digest = f.read()
    model_path = f'{model_dir}/snapshots/{model_digest}'
    model, tokenizer = load(model_path, {'trust_remote_code':True})
    response = generate(model, tokenizer, prompt=prompt, max_tokens=500, temp=temp)
    return response

app = Flask(__name__)

@app.route('/serve', methods=['POST'])
def serve():
    data = request.get_json()
    result = firePrompt(model=data['model'], prompt=data['prompt'], temp=data['temp'])
    return result

@app.route('/')
def index():
    return jsonify({'name': 'alice',
                    'email': 'alice@outlook.com'})

app.run()