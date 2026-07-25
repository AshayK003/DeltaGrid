"""Tests for disk cache."""

import json
import time
from unittest.mock import patch

import pytest

from src.config import CACHE_DIR
from src.data.cache import clear_cache, read_cache, write_cache


@pytest.fixture(autouse=True)
def cleanup_cache():
    yield
    clear_cache()


def test_write_and_read_cache():
    write_cache("test_key", {"hello": "world"})
    result = read_cache("test_key", ttl=60)
    assert result == {"hello": "world"}


def test_read_cache_expired():
    write_cache("expired_key", {"data": 1})
    # Simulate expired by writing with old timestamp
    path = CACHE_DIR / "expired_key.json"
    old_time = time.time() - 120
    import os

    os.utime(path, (old_time, old_time))
    result = read_cache("expired_key", ttl=60)
    assert result is None


def test_read_cache_missing():
    result = read_cache("nonexistent_key", ttl=60)
    assert result is None


def test_clear_cache():
    write_cache("a", {"x": 1})
    write_cache("b", {"y": 2})
    count = clear_cache()
    assert count == 2
    assert read_cache("a", ttl=60) is None


def test_read_cache_ttl_zero():
    write_cache("ttl_zero", {"data": 1})
    result = read_cache("ttl_zero", ttl=0)
    assert result is None


def test_write_and_read_list():
    write_cache("list_key", [1, 2, 3])
    result = read_cache("list_key", ttl=60)
    assert result == [1, 2, 3]


def test_write_and_read_empty_dict():
    write_cache("empty_dict", {})
    result = read_cache("empty_dict", ttl=60)
    assert result == {}


def test_read_cache_corrupted_json():
    path = CACHE_DIR / "corrupted.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("not valid json {{{", encoding="utf-8")
    result = read_cache("corrupted", ttl=60)
    assert result is None


def test_cache_key_sanitization():
    write_cache("ndc/IND:us", {"test": True})
    result = read_cache("ndc/IND:us", ttl=60)
    assert result == {"test": True}


def test_clear_cache_empty_dir():
    clear_cache()
    count = clear_cache()
    assert count == 0


def test_write_cache_creates_new_file():
    write_cache("brand_new_key", {"a": 1, "b": [2, 3]})
    path = CACHE_DIR / "brand_new_key.json"
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1, "b": [2, 3]}


def test_write_cache_overwrites_existing():
    write_cache("dup_key", {"version": 1})
    write_cache("dup_key", {"version": 2})
    assert read_cache("dup_key", ttl=60) == {"version": 2}


def test_write_cache_creates_cache_dir(tmp_path, monkeypatch):
    target_dir = tmp_path / "nested" / "cache"
    monkeypatch.setattr("src.data.cache.CACHE_DIR", target_dir)
    assert not target_dir.exists()
    write_cache("dir_key", {"x": 1})
    assert target_dir.exists()
    assert (target_dir / "dir_key.json").exists()


def test_write_cache_swallows_write_error():
    with patch("pathlib.Path.write_text", side_effect=OSError("permission denied")):
        result = write_cache("perm_denied", {"x": 1})
    assert result is None
    assert read_cache("perm_denied", ttl=60) is None
