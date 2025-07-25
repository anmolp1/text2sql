

#!/usr/bin/env python3
"""
src/ingestion/schema_client.py

BigQuery wrapper: list tables and fetch schemas for a dataset.
"""

from typing import List, Dict, Optional
from google.cloud import bigquery
from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

def get_client() -> bigquery.Client:
    """
    Initialize and return a BigQuery client using the configured project.
    """
    return bigquery.Client(project=settings.GCP_PROJECT)

def list_tables(dataset_id: Optional[str] = None) -> List[str]:
    """
    List all table IDs in the specified BigQuery dataset.
    """
    ds = dataset_id or settings.BIGQUERY_DATASET
    client = get_client()
    try:
        tables = client.list_tables(ds)
        return [table.table_id for table in tables]
    except Exception as e:
        logger.error(f"Error listing tables in dataset '{ds}': {e}")
        raise

def get_table_schema(table_id: str, dataset_id: Optional[str] = None) -> List[bigquery.SchemaField]:
    """
    Fetch the schema (list of SchemaField) for a given table.
    """
    ds = dataset_id or settings.BIGQUERY_DATASET
    client = get_client()
    table_ref = f"{ds}.{table_id}"
    try:
        table = client.get_table(table_ref)
        return table.schema
    except Exception as e:
        logger.error(f"Error fetching schema for table '{table_ref}': {e}")
        raise

def get_all_table_schemas(dataset_id: Optional[str] = None) -> Dict[str, List[bigquery.SchemaField]]:
    """
    Fetch schemas for all tables in the dataset.
    Returns a dict mapping table IDs to lists of SchemaField.
    """
    schemas: Dict[str, List[bigquery.SchemaField]] = {}
    for table_id in list_tables(dataset_id):
        try:
            schemas[table_id] = get_table_schema(table_id, dataset_id)
        except Exception:
            # already logged in get_table_schema
            continue
    return schemas