

#!/usr/bin/env python3
"""
src/store/vector_store.py

Abstracts a local vector store using FAISS or Chroma, with unified add/query interface.
"""

import os
from typing import List, Optional
from src.config import settings
from src.embedder import embed_texts
from langchain.schema import Document
from langchain.vectorstores import FAISS, Chroma

class LocalVectorStore:
    """
    A wrapper around a local vector store (FAISS or Chroma).
    Select via settings.VECTOR_STORE_TYPE ("faiss" or "chroma").
    """

    def __init__(self, path: Optional[str] = None):
        # Path to persist or load the vector store
        self.vs_path = path or os.getenv("VECTORSTORE_PATH", "./vector_store")
        self.store_type = getattr(settings, "VECTOR_STORE_TYPE", "faiss").lower()
        self.embedding_fn = embed_texts
        self.store = None

        # Attempt to load existing store
        if self.store_type == "chroma":
            # For Chroma, pass persist_directory
            try:
                self.store = Chroma(
                    persist_directory=self.vs_path,
                    embedding_function=self.embedding_fn
                )
            except Exception:
                # no existing store or load failed
                self.store = None
        else:
            # Default to FAISS
            try:
                self.store = FAISS.load_local(
                    self.vs_path,
                    embedding_function=self.embedding_fn
                )
            except Exception:
                self.store = None

    def add(self, docs: List[Document]) -> None:
        """
        Add a batch of Documents to the vector store and persist.
        """
        if self.store_type == "chroma":
            # Overwrite or create new Chroma collection
            self.store = Chroma.from_documents(
                docs,
                embedding_function=self.embedding_fn,
                persist_directory=self.vs_path
            )
            self.store.persist()
        else:
            # Use FAISS
            self.store = FAISS.from_documents(
                docs,
                embedding_function=self.embedding_fn
            )
            self.store.save_local(self.vs_path)

    def query(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Perform a similarity search given a text query.
        """
        if not self.store:
            raise RuntimeError(
                f"Vector store not initialized at {self.vs_path}, call add() first."
            )

        top_k = k or settings.TOP_K
        # Try text-based search
        try:
            return self.store.similarity_search(query, k=top_k)
        except Exception:
            # Fallback to vector-based
            q_emb = self.embedding_fn([query])[0]
            return self.store.similarity_search_by_vector(q_emb, top_k)