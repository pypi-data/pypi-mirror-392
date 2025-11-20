# LightRAG Exploration

LightRAG Exploration is a Python FastAPI application for exploring Retrieval-Augmented Generation (RAG) workflows. It provides a modern web interface for chat, graph visualization, and RAG experimentation using local LLMs via Ollama. The app is designed for easy local use and sharing as a pipx CLI tool.

## Features

- **RAG Chat:** Interact with a RAG pipeline using your own documents and local LLMs.
- **Classic Chat:** Simple chat interface with model selection and context summarization.
- **Graph Viewer:** Visualize the entity/relation graph extracted from your research data.
- **Modern Web UI:** Clean, responsive interface built with Tailwind CSS.
- **Easy Setup:** Installable as a pipx CLI for global use.
- **Ollama Integration:** Uses Ollama for local LLM inference and embeddings.
- **Configurable:** Uses `.env` for research output directory and Ollama host.

## Prerequisites

- Python 3.9+
- [pipx](https://pipxproject.github.io/pipx/)
- [Ollama](https://ollama.com/) installed and running with required models (e.g. `gemma3:1b`, `nomic-embed-text:latest`)

### Install system dependencies (macOS example)

```sh
brew install pipx
pipx ensurepath
source ~/.zshrc  # or restart your terminal
```

### Install with pipx

```sh
pipx install lightrag-exploration
```

## Usage

- The API will run on [http://localhost:8080](http://localhost:8080) by default.
- Open your browser and navigate to:
  - `/frontend` — Home page
  - `/frontend/chat` — Classic chat interface
  - `/frontend/rag-chat` — RAG chat interface
  - `/frontend/graph-viewer` — Graph visualization
  - `/docs` — FastAPI API docs

## How It Works

- **RAG Pipeline:** Uses LightRAG and Ollama for retrieval, embedding, and LLM completion.
- **Templates:** Web UI is served from the `templates/` directory.
- **Config:** Set `research_output_dir` and `ollama_host` in `.env` or `.env.example`.

## Development

- All source code is in the root and `routers/` directory.
- The entrypoint is `main.py`, which runs the FastAPI app.
- You can run locally with:
  ```sh
  python main.py
  ```
- Or install and run globally with pipx as above.

**Test your pipx build locally before uploading to PyPI!**

You can install your built wheel or sdist with pipx to verify everything works as expected:

```sh
python -m build
pipx install --force dist/lightrag_exploration-0.1.0-py3-none-any.whl
# or
pipx install --force dist/lightrag_exploration-0.1.0.tar.gz
lightrag-exploration
pipx uninstall lightrag-exploration
```

## Packaging & Distribution

To build and publish to PyPI:

1. Upgrade build and twine:
   ```sh
   python -m pip install --upgrade build twine
   ```
2. Build your package:
   ```sh
   python -m build
   ```
3. (Optional) Check your package:
   ```sh
   python -m twine check dist/*
   ```
4. Upload to PyPI:
   ```sh
   python -m twine upload dist/*
   ```

## Troubleshooting

- If you see errors about missing templates, ensure you installed with pipx after running `pipx ensurepath` and that your terminal session is up to date.
- Make sure Ollama is running and the required models are pulled.
- If you see errors about missing research output, check your `.env` and that the directory exists.

## License

MIT