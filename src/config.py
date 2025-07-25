# src/config.py
import os


class Settings:
    """
    Configuration for environment and model settings.
    Uses Google’s Gemini 2.5 Flash model by default.
    """
    def __init__(self):
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.GCP_PROJECT = os.getenv("GCP_PROJECT")
        self.BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "textembedding-gecko@001")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self.TOP_K = int(os.getenv("TOP_K", 5))


settings = Settings()
