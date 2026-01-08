""" RAG Pipeline for Aibot app."""


# aibottapp/rag/rag_pipeline.py

from .loader import load_document
from .vectorstore import GLOBAL_VECTOR_STORE, chunk_text


# ======================================================
# 📄 INGEST DOCUMENT (PDF / DOCX / TXT)
# ======================================================
def ingest_document(user, uploaded_file, document_id):
    """
    Store document chunks with document_id embedded into text
    (SimpleVectorStore-compatible).
    """

    text = load_document(uploaded_file)

    if not text or not text.strip():
        print("❌ No text extracted")
        return

    chunks = chunk_text(text)

    # 🔑 Embed document_id into the text itself
    wrapped_chunks = [
        f"[DOCUMENT_ID={document_id}]\n{chunk}"
        for chunk in chunks
    ]

    GLOBAL_VECTOR_STORE.add_texts(
        texts=wrapped_chunks,
        metadata={
            "user_id": user.id,
            "filename": uploaded_file.name,
        }
    )

    print(f"✅ Ingested {len(chunks)} chunks for document {document_id}")


# ======================================================
# 🔍 RETRIEVE CONTEXT (SAFE + COMPATIBLE)
# ======================================================
def retrieve_context(question, document_id=None, top_k=3):
    """
    Retrieve chunks.
    - If document_id is provided → only chunks from that document
    - Else → global search (text-only chat)
    """

    results = GLOBAL_VECTOR_STORE.similarity_search(
        query=question,
        top_k=top_k * 4  # fetch more, filter later
    )

    if not results:
        return []

    filtered = []

    for chunk in results:
        # chunk is STRING (not object)
        if document_id:
            if f"[DOCUMENT_ID={document_id}]" in chunk:
                filtered.append(chunk)
        else:
            filtered.append(chunk)

        if len(filtered) >= top_k:
            break

    # Remove document markers before sending to LLM
    return [
        c.replace(f"[DOCUMENT_ID={document_id}]\n", "")
        for c in filtered
    ]
