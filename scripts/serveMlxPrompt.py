import json
from flask import Flask, jsonify, request
from mlx_lm import load, generate
import os
from pathlib import Path
from datetime import datetime
from functools import wraps
from http import HTTPStatus
from huggingface_hub import snapshot_download
import re

app = Flask(__name__)

DEFAULT_HF_MLX_MODEL_REGISTRY = Path("~/.cache/huggingface/hub/").expanduser()

def listModels():
    """
    List available MLX models by inspecting the HuggingFace cache directory.
    Returns a dictionary of model names and their local paths.
    """
    models = {}
    try:
        model_root = DEFAULT_HF_MLX_MODEL_REGISTRY
        if not model_root.exists():
            return models

        # Walk through the models directory
        for model_dir in model_root.glob("models--*"):
            # Convert 'models--org--name' format to 'org/name'
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            model_path = model_dir / "snapshots"
            
            # Check if any snapshot exists
            if model_path.exists() and any(model_path.iterdir()):
                snapshot_dir = next(model_path.iterdir())  # Get the first snapshot
                # Only add if the model files exist
                if any(snapshot_dir.glob("*.safetensors")) or any(snapshot_dir.glob("*.bin")):
                    models[model_name] = str(snapshot_dir)

        return models
    except Exception as e:
        app.logger.error(f"Error listing models: {str(e)}")
        return {}

def validate_model(model_name):
    """Validate if the model is available in the HuggingFace cache."""
    available_models = listModels()
    if model_name not in available_models:
        raise ValueError(
            f"Model '{model_name}' not found in local cache. Available models: {', '.join(available_models.keys())}"
        )
    return available_models[model_name]

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            error_response = {
                "error": {
                    "message": str(e),
                    "type": "invalid_request_error",
                    "param": "model",
                    "code": "model_not_found"
                }
            }
            return jsonify(error_response), HTTPStatus.NOT_FOUND
        except Exception as e:
            error_response = {
                "error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "param": None,
                    "code": "internal_error"
                }
            }
            return jsonify(error_response), HTTPStatus.INTERNAL_SERVER_ERROR
    return wrapper

def firePrompt(model: str, prompt: str, temp=0.3):
    model_path = validate_model(model)
    model, tokenizer = load(model_path, {'trust_remote_code':True})
    response = generate(model, tokenizer, prompt=prompt, max_tokens=500, temp=temp)
    return response

def firePrompt_legacy(model: str, prompt: str, temp=0.3):
    model_dir = f'{DEFAULT_HF_MLX_MODEL_REGISTRY}/models--mlx-community--{model}'
    model_digest = ""
    with open(f'{model_dir}/refs/main', 'r') as f:
        model_digest = f.read()
    model_path = f'{model_dir}/snapshots/{model_digest}'
    model, tokenizer = load(model_path, {'trust_remote_code':True})
    response = generate(model, tokenizer, prompt=prompt, max_tokens=500, temp=temp)
    return response

def download_model(model_name: str) -> tuple[str, str]:
    """
    Download a model from HuggingFace hub.
    Returns a tuple of (local_dir, snapshot_hash).
    """
    try:
        local_dir = snapshot_download(
            repo_id=f"mlx-community/{model_name}",
            cache_dir=DEFAULT_HF_MLX_MODEL_REGISTRY,
            local_files_only=False
        )
        # Get the snapshot hash from the path
        snapshot_hash = os.path.basename(local_dir)
        return local_dir, snapshot_hash
    except Exception as e:
        raise ValueError(f"Failed to download model: {str(e)}")

@app.after_request
def add_header(response):
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/serve', methods=['POST'])
@handle_errors
def serve():
    if not request.is_json:
        return jsonify({
            "error": {
                "message": "Content-Type must be application/json",
                "type": "invalid_request_error",
                "param": "content-type",
                "code": "invalid_content_type"
            }
        }), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    required_fields = ['model', 'prompt', 'temp']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "error": {
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "type": "invalid_request_error",
                "param": missing_fields[0],
                "code": "missing_field"
            }
        }), HTTPStatus.BAD_REQUEST

    result = firePrompt_legacy(model=data['model'], prompt=data['prompt'], temp=data['temp'])
    return jsonify({"result": result})

@app.route('/v1/chat/completions', methods=['POST'])
@handle_errors
def chat_completions():
    if not request.is_json:
        return jsonify({
            "error": {
                "message": "Content-Type must be application/json",
                "type": "invalid_request_error",
                "param": "content-type",
                "code": "invalid_content_type"
            }
        }), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    messages = data.get('messages')
    
    if not messages:
        return jsonify({
            "error": {
                "message": "messages is required",
                "type": "invalid_request_error",
                "param": "messages",
                "code": "missing_field"
            }
        }), HTTPStatus.BAD_REQUEST
    
    if not isinstance(messages, list) or not messages:
        return jsonify({
            "error": {
                "message": "messages must be a non-empty array",
                "type": "invalid_request_error",
                "param": "messages",
                "code": "invalid_messages_format"
            }
        }), HTTPStatus.BAD_REQUEST

    # Validate each message has required fields
    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
            return jsonify({
                "error": {
                    "message": f"Message at index {idx} must have 'role' and 'content' fields",
                    "type": "invalid_request_error",
                    "param": f"messages[{idx}]",
                    "code": "invalid_message_format"
                }
            }), HTTPStatus.BAD_REQUEST

    model = data.get('model', 'mistralai/Mistral-7B-v0.1')
    temperature = data.get('temperature', 0.7)
    
    # Validate temperature
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        return jsonify({
            "error": {
                "message": "temperature must be a number between 0 and 2",
                "type": "invalid_request_error",
                "param": "temperature",
                "code": "invalid_temperature"
            }
        }), HTTPStatus.BAD_REQUEST
    
    # Construct the prompt from messages
    prompt = ""
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        prompt += f"{role}: {content}\nassistant: "
    
    # Get completion from MLX model
    try:
        result = firePrompt(model=model, prompt=prompt, temp=temperature)
    except Exception as e:
        return jsonify({
            "error": {
                "message": f"Error generating completion: {str(e)}",
                "type": "model_error",
                "param": None,
                "code": "model_error"
            }
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # Format response in OpenAI API format
    response = {
        "id": f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(result.split()),
            "total_tokens": len(prompt.split()) + len(result.split())
        }
    }
    return jsonify(response)

@app.route('/v1/models', methods=['GET'])
@handle_errors
def list_available_models():
    """
    List available models in OpenAI API format.
    """
    available_models = listModels()
    models_list = [
        {
            "id": model_id,
            "object": "model",
            "created": int(os.path.getctime(path)),
            "owned_by": model_id.split('/')[0],  # Organization name from model ID
            "permission": [],
            "root": path,
        }
        for model_id, path in available_models.items()
    ]
    print(models_list)
    return jsonify({
        "object": "list",
        "data": models_list
    })

@app.route('/download', methods=['POST'])
@handle_errors
def download_model_endpoint():
    if not request.is_json:
        return jsonify({
            "error": {
                "message": "Content-Type must be application/json",
                "type": "invalid_request_error",
                "param": "content-type",
                "code": "invalid_content_type"
            }
        }), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    if 'model' not in data:
        return jsonify({
            "error": {
                "message": "model field is required",
                "type": "invalid_request_error",
                "param": "model",
                "code": "missing_field"
            }
        }), HTTPStatus.BAD_REQUEST

    model_name = data['model']
    
    # Validate model name format (should be just the model name, not org/model)
    if '/' in model_name or not re.match(r'^[a-zA-Z0-9_-]+$', model_name):
        return jsonify({
            "error": {
                "message": "Invalid model name format. Should be a simple name (e.g., 'mistral-7b-v0.1') without organization prefix",
                "type": "invalid_request_error",
                "param": "model",
                "code": "invalid_model_format"
            }
        }), HTTPStatus.BAD_REQUEST

    try:
        _, snapshot_hash = download_model(model_name)
        return jsonify({
            "status": "success",
            "message": f"Model mlx-community/{model_name} downloaded successfully",
            "snapshot_hash": snapshot_hash
        })
    except ValueError as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "download_error",
                "param": "model",
                "code": "download_failed"
            }
        }), HTTPStatus.BAD_REQUEST

@app.route('/swagger.json', methods=['GET'])
@handle_errors
def swagger():
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "PyOMlx API",
            "description": "Python API for serving Apple MLX models over HTTP",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "http://localhost:11435",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/serve": {
                "post": {
                    "summary": "Legacy endpoint for model inference",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["model", "prompt", "temp"],
                                    "properties": {
                                        "model": {
                                            "type": "string",
                                            "description": "Name of the MLX model"
                                        },
                                        "prompt": {
                                            "type": "string",
                                            "description": "Input prompt for the model"
                                        },
                                        "temp": {
                                            "type": "number",
                                            "description": "Temperature for sampling",
                                            "default": 0.3
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "result": {
                                                "type": "string",
                                                "description": "Generated text response"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/v1/chat/completions": {
                "post": {
                    "summary": "OpenAI-compatible chat completions endpoint",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["messages"],
                                    "properties": {
                                        "model": {
                                            "type": "string",
                                            "description": "Model ID to use",
                                            "default": "mistralai/Mistral-7B-v0.1"
                                        },
                                        "messages": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "required": ["role", "content"],
                                                "properties": {
                                                    "role": {
                                                        "type": "string",
                                                        "enum": ["system", "user", "assistant"]
                                                    },
                                                    "content": {
                                                        "type": "string"
                                                    }
                                                }
                                            }
                                        },
                                        "temperature": {
                                            "type": "number",
                                            "description": "Sampling temperature",
                                            "default": 0.7,
                                            "minimum": 0,
                                            "maximum": 2
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "object": {"type": "string"},
                                            "created": {"type": "integer"},
                                            "model": {"type": "string"},
                                            "choices": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "index": {"type": "integer"},
                                                        "message": {
                                                            "type": "object",
                                                            "properties": {
                                                                "role": {"type": "string"},
                                                                "content": {"type": "string"}
                                                            }
                                                        },
                                                        "finish_reason": {"type": "string"}
                                                    }
                                                }
                                            },
                                            "usage": {
                                                "type": "object",
                                                "properties": {
                                                    "prompt_tokens": {"type": "integer"},
                                                    "completion_tokens": {"type": "integer"},
                                                    "total_tokens": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/v1/models": {
                "get": {
                    "summary": "List available models",
                    "responses": {
                        "200": {
                            "description": "List of available models",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "object": {"type": "string"},
                                            "data": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "object": {"type": "string"},
                                                        "created": {"type": "integer"},
                                                        "owned_by": {"type": "string"},
                                                        "permission": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {"type": "string"},
                                                                    "object": {"type": "string"},
                                                                    "allow_create_engine": {"type": "boolean"},
                                                                    "allow_sampling": {"type": "boolean"},
                                                                    "allow_logprobs": {"type": "boolean"},
                                                                    "allow_search_indices": {"type": "boolean"},
                                                                    "allow_view": {"type": "boolean"},
                                                                    "allow_fine_tuning": {"type": "boolean"},
                                                                    "organization": {"type": "string"},
                                                                    "group": {"type": "string", "nullable": True},
                                                                    "is_blocking": {"type": "boolean"}
                                                                }
                                                            }
                                                        },
                                                        "root": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/download": {
                "post": {
                    "summary": "Download a model from mlx-community",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["model"],
                                    "properties": {
                                        "model": {
                                            "type": "string",
                                            "description": "Name of the model to download (without mlx-community/ prefix)",
                                            "pattern": "^[a-zA-Z0-9_-]+$"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Model downloaded successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "message": {"type": "string"},
                                            "snapshot_hash": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request or download error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "object",
                                                "properties": {
                                                    "message": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "param": {"type": "string"},
                                                    "code": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    response = jsonify(swagger_spec)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
@handle_errors
def index():
    return jsonify({'name': 'PyOMlx',
                    'github': 'https://github.com/kspviswa/PyOMlx'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11435)