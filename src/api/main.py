from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import uvicorn

from src.config import settings
from src.api.routes import router

# Define API key header auth
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Simple API key verification dependency.
    Expects header 'X-API-Key' to match settings.API_TOKEN.
    """
    if api_key != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

# Instantiate FastAPI app
app = FastAPI(
    title="Text2SQL API",
    description="Natural-language to BigQuery SQL service",
    version="0.1.0"
)

# CORS middleware: allow origins provided in settings.CORS_ALLOW_ORIGINS (comma-separated)
origins = settings.CORS_ALLOW_ORIGINS.split(",") if getattr(settings, "CORS_ALLOW_ORIGINS", None) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate-limiting placeholder (implement as needed)
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # TODO: integrate a proper rate limiter (e.g., slowapi or fastapi-limiter)
    response = await call_next(request)
    return response

# Include the query router with API key dependency
app.include_router(
    router,
    prefix="/query",
    dependencies=[Depends(verify_api_key)],
    tags=["query"]
)

# Startup event: initialize resources (e.g., database, cache, model)
@app.on_event("startup")
async def on_startup():
    # e.g. initialize Redis client or load vector index
    pass

# Shutdown event: clean up resources
@app.on_event("shutdown")
async def on_shutdown():
    # e.g. close DB or cache connections
    pass

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=getattr(settings, "API_HOST", "0.0.0.0"),
        port=int(getattr(settings, "API_PORT", 8000)),
        reload=True
    )