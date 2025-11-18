"""
Configuration management for AIMemo
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """
    Configuration for AIMemo.
    
    Attributes:
        db_path: Path to SQLite database
        db_connection: PostgreSQL connection string (if using Postgres)
        max_context_memories: Maximum memories to inject as context
        enable_openai: Enable OpenAI interceptor
        enable_anthropic: Enable Anthropic interceptor
    """
    
    db_path: str = field(default_factory=lambda: os.getenv("AIMEMO_DB_PATH", "aimemo.db"))
    db_connection: Optional[str] = field(default_factory=lambda: os.getenv("AIMEMO_DB_CONNECTION"))
    max_context_memories: int = field(default_factory=lambda: int(os.getenv("AIMEMO_MAX_CONTEXT", "5")))
    enable_openai: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_OPENAI", "true").lower() == "true")
    enable_anthropic: bool = field(default_factory=lambda: os.getenv("AIMEMO_ENABLE_ANTHROPIC", "true").lower() == "true")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

