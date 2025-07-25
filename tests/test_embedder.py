import pytest
from src.config import settings
from src.embeddings.embedder import embed_texts

# --- Dummy classes for mocking ---

class DummySentenceTransformer:
    def __init__(self, model_name):
        self.model_name = model_name

    def encode(self, texts):
        # Return a list of embeddings: [len(text), index]
        return [[float(len(t)), float(i)] for i, t in enumerate(texts)]

class DummyResponse:
    def __init__(self, predictions):
        self.predictions = predictions

class DummyAIPClient:
    def embed_text(self, request):
        texts = request["instances"]
        # Each embedding: [len(text), len(text)+1]
        preds = [{"embeddings": {"values": [float(len(t)), float(len(t)+1)]}} for t in texts]
        return DummyResponse(preds)

# --- Fixtures to reset model between tests ---

@pytest.fixture(autouse=True)
def reset_embedding_model():
    yield
    settings.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Tests ---

def test_embed_sentence_transformers(monkeypatch):
    settings.EMBEDDING_MODEL = "sentence-transformers/my-model"
    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", DummySentenceTransformer)

    texts = ["foo", "bar", "baz"]
    embeds = embed_texts(texts)

    expected = [
        [float(len("foo")), 0.0],
        [float(len("bar")), 1.0],
        [float(len("baz")), 2.0],
    ]
    assert embeds == expected

def test_embed_google_vertex(monkeypatch):
    settings.EMBEDDING_MODEL = "textembedding-gecko@001"
    import google.cloud.aiplatform as aiplatform
    monkeypatch.setattr(aiplatform, "EmbeddingServiceClient", lambda: DummyAIPClient())

    texts = ["hello"]
    embeds = embed_texts(texts)
    expected = [[float(len("hello")), float(len("hello")+1)]]
    assert embeds == expected

def test_embed_unsupported_model():
    settings.EMBEDDING_MODEL = "unsupported-model"
    with pytest.raises(ValueError) as exc:
        embed_texts(["test"])
    assert "Unsupported EMBEDDING_MODEL" in str(exc.value)