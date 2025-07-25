#!/usr/bin/env python3
"""
src/execution/bigquery_client.py

Executes a validated SQL query against BigQuery and returns the results as a pandas DataFrame.

Inputs:
 - SQL string
 - BigQuery credentials (via GOOGLE_APPLICATION_CREDENTIALS env var set in config)

Outputs:
 - pandas.DataFrame containing the query results.
"""

import pandas as pd
from google.cloud import bigquery
from src.config import settings

def run_query(sql: str) -> pd.DataFrame:
    """
    Execute the given SQL query against BigQuery and return the results as a DataFrame.

    Raises:
        RuntimeError: If the query execution fails.
    """
    client = bigquery.Client(project=settings.GCP_PROJECT)
    try:
        query_job = client.query(sql)
        result = query_job.result()
        df = result.to_dataframe()
        return df
    except Exception as e:
        raise RuntimeError(f"Error executing query: {e}")