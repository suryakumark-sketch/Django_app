""" Vector store for Aibot app."""

# aibot/rag/vectorstore.py

import numpy as np
from sentence_transformers import SentenceTransformer

# Local embedding model (FREE)
_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


class SimpleVectorStore:
    """Simple vector store for storing and searching text embeddings."""

    def __init__(self):
        """ Initialize the vector store."""
        self.texts = []
        self.embeddings = []

    def add_texts(self, texts, metadata=None):
        """ Add texts to the vector store."""
        _ = metadata  # explicitly mark as used
        for text in texts:
            emb = _MODEL.encode(text)
            self.texts.append(text)
            self.embeddings.append(emb)

    def similarity_search(self, query, top_k=3):
        """ Search for similar texts in the vector store."""
        if not self.texts:
            return []

        query_emb = _MODEL.encode(query)

        scores = []
        for idx, emb in enumerate(self.embeddings):
            score = np.dot(query_emb, emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(emb)
            )
            scores.append((score, self.texts[idx]))

        scores.sort(reverse=True, key=lambda x: x[0])
        return [text for _, text in scores[:top_k]]


# 🔥 SINGLE GLOBAL STORE
GLOBAL_VECTOR_STORE = SimpleVectorStore()


def chunk_text(text, chunk_size=400, overlap=50):
    """ Chunk text into smaller segments."""
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap

    return chunks

def get_last_chunks(self, top_k=3):
    """ Get the last chunks from the vector store."""
    return [item["text"] for item in self.store[-top_k:]]
