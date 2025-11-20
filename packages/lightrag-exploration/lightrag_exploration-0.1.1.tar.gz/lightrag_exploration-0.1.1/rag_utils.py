# --- RAG utility functions for rag_router.py ---
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# local imports
from settings import LocalSettings


async def initialize_rag(
    chat_model: str = "gemma3:1b", embed_model: str = "nomic-embed-text:latest"
) -> LightRAG:
    # detect embedding dimension from the embedding model to avoid mismatches
    try:
        sample = await ollama_embed(
            [""], embed_model=embed_model, host="http://localhost:11434"
        )
        # sample is a numpy array like (1, dim)
        try:
            detected_dim = int(sample.shape[1])
        except Exception:
            detected_dim = (
                len(sample[0])
                if len(sample) and hasattr(sample[0], "__len__")
                else 1024
            )
    except Exception:
        # fall back to 1024 if detection fails
        detected_dim = 1024

    print(
        f"Chosen models: chat_model={chat_model}, embed_model={embed_model} with dim={detected_dim}"
    )

    rag = LightRAG(
        working_dir=LocalSettings().research_output_dir,
        llm_model_func=ollama_model_complete,
        llm_model_name=chat_model,
        summary_max_tokens=20000,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 20000},
            "timeout": 300,
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=detected_dim,
            max_token_size=20000,
            func=lambda texts: ollama_embed(
                texts,
                embed_model=embed_model,
                host="http://localhost:11434",
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag