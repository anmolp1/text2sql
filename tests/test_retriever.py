import os
import pytest
from langchain.schema import Document
import src.rag.retriever as retriever
from src.config import settings
from langchain.vectorstores import FAISS

class DummyStore:
    def __init__(self, docs, fallback_docs=None):
        self.docs = docs
        self.fallback_docs = fallback_docs or docs

    def similarity_search(self, query, k):
        # Return first k documents
        return self.docs[:k]

    def similarity_search_by_vector(self, vector, k):
        # Return last k documents
        return self.fallback_docs[-k:]

@pytest.fixture(autouse=True)
def reset_env_and_settings(monkeypatch):
    # Clear VECTORSTORE_PATH env var
    monkeypatch.delenv("VECTORSTORE_PATH", raising=False)
    # Reset TOP_K to a known default
    settings.TOP_K = 3
    # Patch embed_texts in retriever to avoid real embedding calls
    monkeypatch.setattr(retriever, "embed_texts", lambda texts: [[0.0]] * len(texts))
    yield

def test_retrieve_normal(monkeypatch):
    # Arrange
    docs = [Document(page_content=f"doc{i}", metadata={}) for i in range(5)]
    dummy_store = DummyStore(docs)
    # Monkey-patch FAISS.load_local to return our dummy store
    monkeypatch.setattr(FAISS, "load_local", staticmethod(lambda path, embedding_function: dummy_store))

    # Act & Assert: default TOP_K
    settings.TOP_K = 2
    result = retriever.retrieve_schema_docs("any question")
    assert result == docs[:2]

    # Act & Assert: overriding top_k
    result2 = retriever.retrieve_schema_docs("any question", top_k=4)
    assert result2 == docs[:4]

def test_retrieve_fallback(monkeypatch):
    # Arrange
    docs = [Document(page_content=f"doc{i}", metadata={}) for i in range(5)]
    dummy_store = DummyStore(docs)
    # Make similarity_search raise AttributeError to trigger fallback
    def bad_similarity(query, k):
        raise AttributeError("similarity_search not supported")
    dummy_store.similarity_search = bad_similarity
    dummy_store.similarity_search_by_vector = lambda vector, k: docs[-k:]
    monkeypatch.setattr(FAISS, "load_local", staticmethod(lambda path, embedding_function: dummy_store))

    # Act
    settings.TOP_K = 3
    result = retriever.retrieve_schema_docs("any question")

    # Assert: fallback returns last TOP_K docs
    assert result == docs[-3:]