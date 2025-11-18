"""
AIMemo - Memory System for AI Conversations

A lightweight memory layer for AI agents that remembers context across conversations.
Author: Jason
License: MIT
"""

__version__ = "1.0.1"
__author__ = "Jason"

from .core import AIMemo
from .storage import MemoryStore, SQLiteStore, PostgresStore
from .config import Config

__all__ = [
    "AIMemo",
    "MemoryStore",
    "SQLiteStore", 
    "PostgresStore",
    "Config",
]

