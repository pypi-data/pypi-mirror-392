"""
Core AIMemo class - Main entry point for the memory system
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib

from .storage import MemoryStore, SQLiteStore
from .config import Config
from .providers import OpenAIProvider, AnthropicProvider


class AIMemo:
    """
    Main memory system that intercepts LLM calls and injects context.
    
    Usage:
        aimemo = AIMemo()
        aimemo.enable()
        
        # Your LLM calls now have memory
        client = OpenAI()
        response = client.chat.completions.create(...)
    """
    
    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        config: Optional[Config] = None,
        namespace: str = "default",
        auto_enable: bool = False,
    ):
        """
        Initialize AIMemo memory system.
        
        Args:
            store: Memory storage backend (default: SQLite)
            config: Configuration object
            namespace: Namespace for isolating memories
            auto_enable: Automatically enable interceptors
        """
        self.config = config or Config()
        self.store = store or SQLiteStore(self.config.db_path)
        self.namespace = namespace
        self._enabled = False
        self._providers = {}
        
        # Initialize providers
        self._init_providers()
        
        if auto_enable:
            self.enable()
    
    def _init_providers(self):
        """Initialize LLM provider interceptors."""
        self._providers["openai"] = OpenAIProvider(self)
        self._providers["anthropic"] = AnthropicProvider(self)
    
    def enable(self):
        """Enable memory interception for LLM calls."""
        if self._enabled:
            return
        
        for provider in self._providers.values():
            provider.enable()
        
        self._enabled = True
    
    def disable(self):
        """Disable memory interception."""
        if not self._enabled:
            return
        
        for provider in self._providers.values():
            provider.disable()
        
        self._enabled = False
    
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Manually add a memory.
        
        Args:
            content: Memory content
            metadata: Additional metadata
            tags: Tags for categorization
            
        Returns:
            Memory ID
        """
        memory_id = self._generate_id(content)
        
        memory = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "tags": tags or [],
            "namespace": self.namespace,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.store.save(memory)
        return memory_id
    
    def search(
        self,
        query: str,
        limit: int = 5,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search memories by query.
        
        Args:
            query: Search query
            limit: Maximum results
            tags: Filter by tags
            
        Returns:
            List of matching memories
        """
        return self.store.search(
            query=query,
            namespace=self.namespace,
            limit=limit,
            tags=tags,
        )
    
    def get_context(self, query: str, limit: int = 5) -> str:
        """
        Get relevant context for a query.
        
        Args:
            query: Query to find context for
            limit: Number of memories to retrieve
            
        Returns:
            Formatted context string
        """
        memories = self.search(query, limit=limit)
        
        if not memories:
            return ""
        
        context_parts = ["Previous context:"]
        for mem in memories:
            context_parts.append(f"- {mem['content']}")
        
        return "\n".join(context_parts)
    
    def clear(self, namespace: Optional[str] = None):
        """Clear memories for a namespace."""
        ns = namespace or self.namespace
        self.store.clear(ns)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content."""
        return hashlib.sha256(
            f"{content}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
    
    def __enter__(self):
        """Context manager support."""
        self.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.disable()

