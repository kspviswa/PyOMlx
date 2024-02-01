from mlx_lm import load, generate
import os
from pathlib import Path

DEFAULT_HF_MLX_MODEL_REGISTRY = Path("~/.cache/huggingface/hub/").expanduser()

#model, tokenizer = load("mlx-community/stablelm-2-zephyr-1_6b-4bit")
#model, tokenizer = load("/Users/kspviswa/.cache/huggingface/hub/models--mlx-community--stablelm-2-zephyr-1_6b-4bit/snapshots/34f6e2321d9e0317d243bb03f9c1f6d4a7c30d3a", {'trust_remote_code':True})

def firePrompt(model: str, prompt: str):
    model_dir = f'{DEFAULT_HF_MLX_MODEL_REGISTRY}/models--mlx-community--{model}'
    model_digest = ""
    with open(f'{model_dir}/refs/main', 'r') as f:
        model_digest = f.read()
    model_path = f'{model_dir}/snapshots/{model_digest}'
    model, tokenizer = load(model_path, {'trust_remote_code':True})
    response = generate(model, tokenizer, prompt=prompt, max_tokens=500)
    return response

if __name__ == "__main__":
    res = firePrompt('stablelm-2-zephyr-1_6b-4bit', 'write a c++ program to sort')
    print(res)