

# Text2SQL RAG-Powered SQL Agent

A Retrieval-Augmented Generation (RAG) pipeline that allows non-technical users to ask natural-language questions about their BigQuery data, automatically convert those questions into SQL using Google's Gemini 2.5 Flash model, execute the queries, and display the results via a Streamlit UI or FastAPI API.

## Features

- **Schema Ingestion & Embedding**: Pulls BigQuery schemas, converts to text, and embeds into a local FAISS or Chroma vector store.
- **RAG-Based SQL Generation**: Uses retrieved schema documents and Gemini 2.5 Flash to generate valid `SELECT` statements.
- **SQL Validation**: Ensures only safe `SELECT` queries with a `LIMIT` clause are executed.
- **Query Execution**: Runs validated SQL against BigQuery and returns results as a pandas DataFrame.
- **Caching**: Caches query results in Redis to improve performance and reduce costs.
- **API & UI**: 
  - FastAPI endpoint (`/query`) with API key authentication.
  - Streamlit front-end (`/src/ui/app.py`) for ad-hoc querying.

## Prerequisites

- Python 3.10+
- [pipenv](https://pipenv.pypa.io/) or virtual environment (`venv`)
- Google Cloud project with BigQuery enabled
- Service account JSON key with BigQuery access
- Redis server (for caching)

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-org/text2sql.git
   cd text2sql
   ```

2. **Install dependencies** (using Pipenv)  
   ```bash
   pip install pipenv
   pipenv install --dev
   pipenv shell
   ```

   Or using `requirements.txt`:  
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

All settings are managed via `config/config.yaml`. Example:

```yaml
# BigQuery & GCP
gcp_project: your-gcp-project-id
bigquery_dataset: your_dataset_name
bigquery_credentials_path: /path/to/service-account.json

# Embeddings & LLM
embedding_model: textembedding-gecko@001
llm_model: gemini-2.5-flash

# Vector store
vectorstore_path: ./vector_store

# API
api_token: YOUR_SECURE_API_TOKEN
cors_allow_origins: "*"
api_host: 0.0.0.0
api_port: 8000

# Redis Cache
redis_url: redis://localhost:6379/0
cache_ttl: 3600

# Logging
logging_config_path: config/logging.yaml
```

You can also override any of these via environment variables.

## Quickstart

1. **Ingest schemas**  
   Populate or rebuild your vector store from BigQuery schemas:
   ```bash
   python scripts/ingest_schema.py config/config.yaml
   ```

2. **Run the FastAPI server**  
   Ensure `API_TOKEN` is set in your environment:
   ```bash
   export API_TOKEN="YOUR_SECURE_API_TOKEN"
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Run the Streamlit UI**  
   ```bash
   streamlit run src/ui/app.py
   ```

4. **Refresh cache** (optional)  
   ```bash
   python scripts/refresh_cache.py "query::*"
   ```

## Usage

- **API**:  
  Send a `POST` request to `http://<host>:<port>/query` with header `X-API-Key: YOUR_SECURE_API_TOKEN` and JSON body:
  ```json
  {
    "question": "How many orders were placed last month?"
  }
  ```

- **UI**:  
  Navigate to `http://localhost:8501` after running **Streamlit**, enter your question, and click **Run Query**.

## Running Tests

Execute all unit tests with:
```bash
pytest
```

## Project Structure

```
.
├── config/
│   ├── config.yaml
│   └── logging.yaml
├── scripts/
│   ├── ingest_schema.py
│   └── refresh_cache.py
├── src/
│   ├── api/
│   ├── cache/
│   ├── embeddings/
│   ├── execution/
│   ├── ingestion/
│   ├── rag/
│   ├── store/
│   ├── ui/
│   ├── utils/
│   └── config.py
├── tests/
│   ├── test_embedder.py
│   ├── test_retriever.py
│   └── test_execution.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions welcome! Please open issues or pull requests for enhancements, bug fixes, or additional tests.

## License

This project is licensed under the MIT License. See `LICENSE` for details.