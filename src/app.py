# src/app.py

import streamlit as st
from .schema_loader import load_schema
from .embedder import embed_texts
from .retriever import Retriever
from .sql_generator import generate_sql
from .executor import execute_sql

# Load and vectorize schema once
schema_info = load_schema()
texts = []
metadatas = []
for tbl in schema_info:
    for col in tbl["columns"]:
        texts.append(f"{tbl['table_name']}.{col['name']} ({col['type']}): {col.get('description','')}")
        metadatas.append({"table": tbl['table_name'], "column": col['name']})

embeddings = embed_texts(texts)
retriever = Retriever(dimension=len(embeddings[0]))
retriever.add_embeddings(embeddings, metadatas)

st.title("RAG-to-SQL MVP")
user_query = st.text_input("Enter your question:")
if user_query:
    # Retrieve context
    q_embed = embed_texts([user_query])[0]
    hits = retriever.retrieve(q_embed)
    schema_ctx = "\n".join([f"{h['table']}.{h['column']}" for h in hits])

    # Generate SQL
    sql = generate_sql(user_query, schema_ctx)
    st.subheader("Generated SQL")
    st.code(sql)

    # Execute and show
    df = execute_sql(sql)
    st.subheader("Results")
    st.dataframe(df)