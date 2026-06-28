import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    cache_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME") or os.getenv("HF_HOME")
    kwargs = {"cache_folder": cache_dir} if cache_dir else {}
    return SentenceTransformer(MODEL_NAME, **kwargs)


def embed_text(text: str) -> list[float]:
    return get_embedding_model().encode(text).tolist()
