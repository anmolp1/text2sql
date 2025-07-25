

# src/rag/generator.py

from typing import List
from langchain.schema import Document
from src.sql_generator import generate_sql as _generate_sql

def generate_sql(docs: List[Document], question: str) -> str:
    """
    Given a list of retrieved schema Documents and a user question,
    build a schema context string and generate a BigQuery SQL query.
    """
    if not docs:
        raise ValueError("No schema documents provided for SQL generation")

    # Concatenate each document's text into a single schema context
    schema_context = "\n\n".join(doc.page_content for doc in docs)

    # Delegate to the core generator that uses the LLM
    return _generate_sql(schema_context, question)