

#!/usr/bin/env python3
"""
src/embeddings/embedder.py

Embeds text strings into vectors using the configured embedding model.
Supports:
  - Open-source Sentence-Transformers
  - Google Vertex AI free embedding
  - (No OpenAI fallback in this version)
"""

import os
from typing import List
from src.config import settings

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    Reads settings.EMBEDDING_MODEL to decide:
      - sentence-transformers/<model>
      - textembedding-gecko@001
    """
    model = settings.EMBEDDING_MODEL

    # Open-source Sentence-Transformers
    if model.startswith("sentence-transformers/"):
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer(model)
        embeddings = encoder.encode(texts)
        return [list(map(float, emb)) for emb in embeddings]

    # Google Vertex AI free embedding
    if model.startswith("textembedding-gecko"):
        from google.cloud import aiplatform
        client = aiplatform.EmbeddingServiceClient()
        model_name = f"projects/{settings.GCP_PROJECT}/locations/us-central1/publishers/google/models/{model}"
        response = client.embed_text(request={"model": model_name, "instances": texts})
        # predictions is a list of dicts with 'embeddings': { 'values': [...] }
        return [pred["embeddings"]["values"] for pred in response.predictions]

    raise ValueError(
        f"Unsupported EMBEDDING_MODEL '{model}'. "
        "Use 'sentence-transformers/<model>' or 'textembedding-gecko@001'."
    )