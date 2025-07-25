

#!/usr/bin/env python3
"""
src/ui/app.py

Streamlit UI for the Text2SQL RAG pipeline.
"""

import streamlit as st
import pandas as pd

from src.rag.retriever import retrieve_schema_docs
from src.rag.generator import generate_sql
from src.utils.validation import validate_sql
from src.execution.bigquery_client import run_query
from src.cache.redis_cache import get_cache, set_cache

def main():
    st.set_page_config(page_title="Text2SQL RAG Demo", layout="wide")
    st.title("🗣️  Text2SQL RAG Demo")
    st.write("Ask a natural language question about your BigQuery data and get back SQL results.")

    question = st.text_input("Enter your question here:", placeholder="e.g., How many orders in the last month?")
    if not question:
        st.info("Please enter a question to generate SQL and execute it.")
        return

    if st.button("Run Query"):
        cache_key = f"query::{question}"
        # 1) Attempt cache
        cached = get_cache(cache_key)
        if cached:
            st.success("✅ Loaded results from cache.")
            sql = cached["sql"]
            df = pd.DataFrame(cached["data"])
        else:
            # 2) Retrieve schema docs
            with st.spinner("🔍 Retrieving relevant schema documents..."):
                try:
                    docs = retrieve_schema_docs(question)
                except Exception as e:
                    st.error(f"Error retrieving schema docs: {e}")
                    return

            # 3) Generate SQL
            with st.spinner("🤖 Generating SQL with RAG..."):
                try:
                    sql = generate_sql(docs, question)
                except Exception as e:
                    st.error(f"Error generating SQL: {e}")
                    return

            st.subheader("Generated SQL")
            st.code(sql, language="sql")

            # 4) Validate SQL
            valid, err = validate_sql(sql)
            if not valid:
                st.error(f"SQL validation failed: {err}")
                return

            # 5) Execute SQL
            with st.spinner("⚡ Executing SQL against BigQuery..."):
                try:
                    df = run_query(sql)
                except Exception as e:
                    st.error(f"Error executing SQL: {e}")
                    return

            # 6) Cache results
            set_cache(cache_key, {"sql": sql, "data": df.to_dict(orient="records")})

        # Display results
        st.subheader("Query Results")
        st.dataframe(df)

if __name__ == "__main__":
    main()