![](logo_readme.png)
# PyOMlx
### Serve MlX models locally!

## Motivation
Inspired by [Ollama](https://github.com/ollama/ollama) project, I wanted to have a similar experience for serving [MLX models](https://github.com/ml-explore/mlx-examples). [Mlx from ml-explore](https://github.com/ml-explore/mlx) is a new framework for running ML models in Apple Silicon. This app is intended to be used along with [PyOllaMx](https://github.com/kspviswa/pyOllaMx)

I'm using these in my day to day workflow and I intend to keep develop these for my use and benifit.

If you find this valuable, feel free to use it and contribute to this project as well. Please ⭐️ this repo to show your support and make my day!

I'm planning on work on next items on this roadmap.md[roadmap.md]. Feel free to comment your thoughts (if any) and influence my work (if interested)

## How to use

1) Download this repo and install the deps

```
pip install -r requirements.txt
```
2) Run the app

```
python3 PyOMlx.py
```

3) You will now see the application running in the system tray. Use [PyOllaMx](https://github.com/kspviswa/pyOllaMx) to chat with MLX models seamlessly

## Features

- Automatically discover & serve MLX models that are downloaded from [MLX Huggingface community](https://huggingface.co/mlx-community).
