"""
Storage backends for memory persistence
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path


class MemoryStore(ABC):
    """Abstract base class for memory storage."""
    
    @abstractmethod
    def save(self, memory: Dict[str, Any]) -> None:
        """Save a memory."""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        namespace: str,
        limit: int = 5,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search memories."""
        pass
    
    @abstractmethod
    def clear(self, namespace: str) -> None:
        """Clear memories for namespace."""
        pass


class SQLiteStore(MemoryStore):
    """SQLite-based memory storage."""
    
    def __init__(self, db_path: str = "aimemo.db"):
        """
        Initialize SQLite store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    tags TEXT,
                    namespace TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster searches
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_namespace 
                ON memories(namespace)
            """)
            
            # Enable FTS5 for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts 
                USING fts5(content, namespace, tags)
            """)
            
            conn.commit()
    
    def save(self, memory: Dict[str, Any]) -> None:
        """Save memory to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, metadata, tags, namespace, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    memory["id"],
                    memory["content"],
                    json.dumps(memory.get("metadata", {})),
                    json.dumps(memory.get("tags", [])),
                    memory["namespace"],
                    memory["timestamp"],
                ),
            )
            
            # Add to FTS index
            conn.execute(
                """
                INSERT OR REPLACE INTO memories_fts 
                (rowid, content, namespace, tags)
                VALUES (
                    (SELECT rowid FROM memories WHERE id = ?),
                    ?, ?, ?
                )
                """,
                (
                    memory["id"],
                    memory["content"],
                    memory["namespace"],
                    json.dumps(memory.get("tags", [])),
                ),
            )
            
            conn.commit()
    
    def search(
        self,
        query: str,
        namespace: str,
        limit: int = 5,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search memories using FTS5."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Use FTS5 for full-text search
            cursor = conn.execute(
                """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.rowid = fts.rowid
                WHERE fts.content MATCH ? AND m.namespace = ?
                ORDER BY fts.rank
                LIMIT ?
                """,
                (query, namespace, limit),
            )
            
            results = []
            for row in cursor:
                results.append({
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]),
                    "tags": json.loads(row["tags"]),
                    "namespace": row["namespace"],
                    "timestamp": row["timestamp"],
                })
            
            return results
    
    def clear(self, namespace: str) -> None:
        """Clear all memories for namespace."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM memories WHERE namespace = ?",
                (namespace,)
            )
            conn.commit()


class PostgresStore(MemoryStore):
    """PostgreSQL-based memory storage."""
    
    def __init__(self, connection_string: str):
        """
        Initialize Postgres store.
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        try:
            import psycopg2
        except ImportError:
            raise ImportError(
                "psycopg2 required for PostgreSQL support. "
                "Install with: pip install psycopg2-binary"
            )
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        tags TEXT[],
                        namespace TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_namespace 
                    ON memories(namespace)
                """)
                
                # Create GIN index for full-text search
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_content_fts
                    ON memories USING gin(to_tsvector('english', content))
                """)
                
                conn.commit()
    
    def save(self, memory: Dict[str, Any]) -> None:
        """Save memory to PostgreSQL."""
        import psycopg2
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO memories 
                    (id, content, metadata, tags, namespace, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        tags = EXCLUDED.tags
                    """,
                    (
                        memory["id"],
                        memory["content"],
                        json.dumps(memory.get("metadata", {})),
                        memory.get("tags", []),
                        memory["namespace"],
                        memory["timestamp"],
                    ),
                )
                conn.commit()
    
    def search(
        self,
        query: str,
        namespace: str,
        limit: int = 5,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search memories using PostgreSQL full-text search."""
        import psycopg2
        import psycopg2.extras
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM memories
                    WHERE namespace = %s
                    AND to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC
                    LIMIT %s
                    """,
                    (namespace, query, query, limit),
                )
                
                results = []
                for row in cur:
                    results.append({
                        "id": row["id"],
                        "content": row["content"],
                        "metadata": row["metadata"],
                        "tags": row["tags"],
                        "namespace": row["namespace"],
                        "timestamp": row["timestamp"].isoformat(),
                    })
                
                return results
    
    def clear(self, namespace: str) -> None:
        """Clear all memories for namespace."""
        import psycopg2
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM memories WHERE namespace = %s",
                    (namespace,)
                )
                conn.commit()

