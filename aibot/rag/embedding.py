""" Embeddings for Aibot app."""

# chatbotapp/rag/embeddings.py

from typing import List

from sentence_transformers import SentenceTransformer

# ✅ Free, local, industry-standard embedding model
# 384-dimensional vectors
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of texts into embedding vectors (LOCAL, FREE).

    Args:
        texts (List[str]): List of text chunks or questions

    Returns:
        List[List[float]]: Embedding vectors
    """
    return _model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True
    ).tolist()
