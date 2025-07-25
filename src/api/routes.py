

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Any

from src.rag.retriever import retrieve_schema_docs
from src.rag.generator import generate_sql
from src.utils.validation import validate_sql
from src.execution.bigquery_client import run_query
from src.cache.redis_cache import get_cache, set_cache

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    sql: str
    data: List[Any]

@router.post("/", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    # Build cache key (you can customize hashing if needed)
    cache_key = f"query::{payload.question}"

    # 1) Check cache
    cached = get_cache(cache_key)
    if cached:
        return QueryResponse(sql=cached["sql"], data=cached["data"])

    # 2) Retrieve relevant schema docs
    docs = retrieve_schema_docs(payload.question)

    # 3) Generate SQL via RAG
    sql = generate_sql(docs, payload.question)

    # 4) Validate SQL safety (only SELECT, LIMIT, etc.)
    is_valid, err_msg = validate_sql(sql)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL validation failed: {err_msg}"
        )

    # 5) Execute SQL against BigQuery
    try:
        df = run_query(sql)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing SQL: {str(e)}"
        )

    # Convert DataFrame to list of records
    data = df.to_dict(orient="records")

    # 6) Cache the result
    set_cache(cache_key, {"sql": sql, "data": data})

    return QueryResponse(sql=sql, data=data)