#!/usr/bin/env python3
"""
scripts/ingest_schema.py

Pulls BigQuery schemas, creates text docs, embeds them, and stores in a FAISS vector store.

Inputs:
 - config.yaml (with keys: gcp_project, bigquery_dataset, bigquery_credentials_path, embedding_model, vectorstore_path)
 - BigQuery credentials JSON, referenced by bigquery_credentials_path

Output:
 - A FAISS vector store directory populated with schema embeddings.

Note:
    Dependencies are listed in requirements.txt.
    Install them with:
      pip install -r requirements.txt
"""

import os
import sys
import yaml
from src.config import settings
from src.embedder import embed_texts
from langchain.schema import Document
from langchain.vectorstores import FAISS


def load_config(path: str = "config.yaml") -> dict:
    """Load configuration from a YAML file."""
    if not os.path.exists(path):
        sys.stderr.write(f"Config file '{path}' not found.\n")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def apply_config(cfg: dict):
    """Override environment and settings based on config values."""
    cred = cfg.get("bigquery_credentials_path")
    if cred:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred
    if "gcp_project" in cfg:
        settings.GCP_PROJECT = cfg["gcp_project"]
    if "bigquery_dataset" in cfg:
        settings.BIGQUERY_DATASET = cfg["bigquery_dataset"]
    if "embedding_model" in cfg:
        settings.EMBEDDING_MODEL = cfg["embedding_model"]


def fetch_schemas(client, dataset_id: str) -> dict:
    """Retrieve schema for each table in the dataset."""
    schemas = {}
    try:
        tables = client.list_tables(dataset_id)
    except Exception as e:
        sys.stderr.write(f"Error listing tables for dataset '{dataset_id}': {e}\n")
        return schemas

    for table in tables:
        full_ref = f"{dataset_id}.{table.table_id}"
        try:
            tbl = client.get_table(full_ref)
            schemas[table.table_id] = tbl.schema
        except Exception as e:
            sys.stderr.write(f"Error fetching table '{full_ref}': {e}\n")
    return schemas


def schema_to_text(table_name: str, fields: list) -> str:
    """Convert schema fields into a human-readable text document."""
    lines = [f"Table: {table_name}", "Columns:"]
    for field in fields:
        lines.append(f"- {field.name} ({field.field_type})")
    return "\n".join(lines)


def main(config_path: str = "config.yaml"):
    # 1. Load and apply configuration
    cfg = load_config(config_path)
    apply_config(cfg)

    # 2. Import BigQuery client here to avoid top-level errors
    try:
        from google.cloud import bigquery
    except ModuleNotFoundError:
        sys.stderr.write(
            "Dependency missing: google-cloud-bigquery not installed.\n"
            "Install it with: pip install google-cloud-bigquery\n"
        )
        return

    # 3. Initialize BigQuery client and fetch schemas
    client = bigquery.Client(project=settings.GCP_PROJECT)
    schemas = fetch_schemas(client, settings.BIGQUERY_DATASET)
    if not schemas:
        sys.stderr.write(f"No schemas found for dataset '{settings.BIGQUERY_DATASET}'.\n")
        return

    # 4. Build Document objects and embed
    docs = [
        Document(page_content=schema_to_text(tbl, fields), metadata={"table": tbl})
        for tbl, fields in schemas.items()
    ]
    texts = [d.page_content for d in docs]
    embeddings = embed_texts(texts)

    # 5. Prepare vector store
    vs_path = cfg.get("vectorstore_path", "./vector_store")
    os.makedirs(vs_path, exist_ok=True)
    embedding_fn = lambda txt: embed_texts([txt])[0]
    store = FAISS.from_documents(docs, embedding=embedding_fn)
    store.save_local(vs_path)

    print(f"✅ Vector store built and saved to {vs_path}")


if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(cfg_file)