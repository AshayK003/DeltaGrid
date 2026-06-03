"""TTL-based disk cache for OWID CSV and Climate Watch API responses."""

import json
import time
from pathlib import Path

from src.config import CACHE_DIR


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(key: str) -> Path:
    safe_name = key.replace("/", "_").replace("\\", "_").replace(":", "_")
    return CACHE_DIR / f"{safe_name}.json"


def read_cache(key: str, ttl: int) -> dict | list | None:
    """Return cached data if exists and not expired, else None."""
    path = _cache_path(key)
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def write_cache(key: str, data: dict | list) -> None:
    """Write data to disk cache."""
    _ensure_cache_dir()
    path = _cache_path(key)
    path.write_text(json.dumps(data, default=str), encoding="utf-8")


def clear_cache() -> int:
    """Remove all cached files. Returns count of files removed."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return count
