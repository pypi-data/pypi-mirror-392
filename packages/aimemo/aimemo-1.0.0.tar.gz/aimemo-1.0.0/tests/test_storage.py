"""
Unit tests for storage backends
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from aimemo.storage import SQLiteStore


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def store(temp_db):
    """Create SQLite store."""
    return SQLiteStore(temp_db)


def test_save_memory(store):
    """Test saving a memory."""
    memory = {
        "id": "test123",
        "content": "Test memory content",
        "metadata": {"key": "value"},
        "tags": ["test"],
        "namespace": "test",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    store.save(memory)
    
    # Should not raise any errors


def test_search_basic(store):
    """Test basic search functionality."""
    memory = {
        "id": "test123",
        "content": "Python is a great programming language",
        "metadata": {},
        "tags": [],
        "namespace": "test",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    store.save(memory)
    
    results = store.search("Python", "test", limit=5)
    assert len(results) == 1
    assert results[0]["content"] == memory["content"]


def test_search_empty(store):
    """Test search with no results."""
    results = store.search("nonexistent", "test", limit=5)
    assert len(results) == 0


def test_clear_namespace(store):
    """Test clearing a namespace."""
    memory1 = {
        "id": "test1",
        "content": "Memory 1",
        "metadata": {},
        "tags": [],
        "namespace": "test",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    memory2 = {
        "id": "test2",
        "content": "Memory 2",
        "metadata": {},
        "tags": [],
        "namespace": "other",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    store.save(memory1)
    store.save(memory2)
    
    store.clear("test")
    
    results_test = store.search("Memory", "test", limit=10)
    results_other = store.search("Memory", "other", limit=10)
    
    assert len(results_test) == 0
    assert len(results_other) == 1


def test_update_memory(store):
    """Test updating an existing memory."""
    memory = {
        "id": "test123",
        "content": "Original content",
        "metadata": {},
        "tags": [],
        "namespace": "test",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    store.save(memory)
    
    # Update
    memory["content"] = "Updated content"
    store.save(memory)
    
    results = store.search("Updated", "test", limit=5)
    assert len(results) == 1
    assert results[0]["content"] == "Updated content"

