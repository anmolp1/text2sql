

#!/usr/bin/env python3
"""
scripts/refresh_cache.py

Invalidates (deletes) cache entries in Redis based on a key pattern.

Inputs:
  - config.yaml (with optional key: redis_url)
  - Optional CLI argument: key pattern (default: "query::*")

Outputs:
  - Prints the number of deleted cache keys.
"""

import os
import sys
import yaml
import redis

def load_config(path: str = "config.yaml") -> dict:
    """Load configuration from YAML, return empty dict if file not found."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    return {}

def apply_config(cfg: dict):
    """Set environment variables for Redis connection if provided."""
    if "redis_url" in cfg:
        os.environ["REDIS_URL"] = cfg["redis_url"]
    if "cache_ttl" in cfg:
        os.environ["CACHE_TTL"] = str(cfg["cache_ttl"])

def main():
    # 1) Load config and apply
    cfg = load_config()
    apply_config(cfg)

    # 2) Determine Redis URL and pattern
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    pattern = sys.argv[1] if len(sys.argv) > 1 else "query::*"

    # 3) Connect to Redis
    try:
        client = redis.Redis.from_url(redis_url)
        client.ping()
    except Exception as e:
        sys.stderr.write(f"Error connecting to Redis at {redis_url}: {e}\n")
        sys.exit(1)

    # 4) Scan and delete matching keys
    deleted = 0
    for key in client.scan_iter(match=pattern):
        try:
            client.delete(key)
            deleted += 1
        except Exception as e:
            sys.stderr.write(f"Error deleting key {key}: {e}\n")

    print(f"✅ Deleted {deleted} keys matching pattern '{pattern}'")

if __name__ == "__main__":
    main()