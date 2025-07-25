

#!/usr/bin/env python3
"""
src/cache/redis_cache.py

Simple Redis-backed cache for query results.
"""

import os
import json
import logging
from typing import Optional, Any

import redis

# Initialize logger
logger = logging.getLogger(__name__)

# Configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # default TTL: 1 hour

# Create Redis client
try:
    _redis_client = redis.Redis.from_url(REDIS_URL)
    _redis_client.ping()
except Exception as e:
    logger.error(f"Error connecting to Redis at {REDIS_URL}: {e}")
    _redis_client = None

def get_cache(key: str) -> Optional[Any]:
    """
    Fetch a cached value by key.
    Returns the deserialized JSON object, or None if missing or on error.
    """
    if _redis_client is None:
        return None
    try:
        raw = _redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Error getting cache for key '{key}': {e}")
        return None

def set_cache(key: str, value: Any) -> None:
    """
    Store a JSON-serializable value under the given key with TTL.
    """
    if _redis_client is None:
        return
    try:
        _redis_client.set(name=key, value=json.dumps(value), ex=CACHE_TTL)
    except Exception as e:
        logger.error(f"Error setting cache for key '{key}': {e}")