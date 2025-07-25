import os
from typing import List
from src.config import settings
from src.embedder import embed_texts
from langchain.vectorstores import FAISS
from langchain.schema import Document

def retrieve_schema_docs(question: str, top_k: int = None) -> List[Document]:
    """
    Retrieve the top-k relevant schema documents for a natural language question.
    Embeds the question, loads the FAISS vector store, and performs a similarity search.
    """
    # Determine vector store path (override via VECTORSTORE_PATH env var)
    vs_path = os.getenv("VECTORSTORE_PATH", "./vector_store")

    # Load the FAISS vector store saved by ingest_schema.py
    try:
        # embedding_function is used internally if you call similarity_search(text)
        store = FAISS.load_local(vs_path, embedding_function=embed_texts)
    except Exception as e:
        raise RuntimeError(f"Failed to load vector store at '{vs_path}': {e}")

    # Number of docs to retrieve
    k = top_k or settings.TOP_K

    # Perform retrieval. Try text-based first, then fallback to raw vector.
    try:
        docs = store.similarity_search(question, k=k)
    except Exception:
        query_emb = embed_texts([question])[0]
        docs = store.similarity_search_by_vector(query_emb, k)

    return docs