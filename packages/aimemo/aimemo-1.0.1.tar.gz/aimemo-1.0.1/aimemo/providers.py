"""
LLM provider integrations for intercepting and augmenting calls
"""

import functools
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import AIMemo


class BaseProvider:
    """Base class for LLM provider interceptors."""
    
    def __init__(self, aimemo: "AIMemo"):
        self.aimemo = aimemo
        self._original_methods = {}
        self._enabled = False
    
    def enable(self):
        """Enable interception."""
        if self._enabled:
            return
        self._patch()
        self._enabled = True
    
    def disable(self):
        """Disable interception."""
        if not self._enabled:
            return
        self._unpatch()
        self._enabled = False
    
    def _patch(self):
        """Override this to patch provider methods."""
        pass
    
    def _unpatch(self):
        """Override this to restore original methods."""
        pass


class OpenAIProvider(BaseProvider):
    """OpenAI API interceptor."""
    
    def _patch(self):
        """Patch OpenAI chat completions."""
        try:
            import openai
        except ImportError:
            return
        
        # Store original method
        if hasattr(openai.OpenAI, "chat"):
            original_create = openai.resources.chat.completions.Completions.create
            self._original_methods["chat_create"] = original_create
            
            @functools.wraps(original_create)
            def wrapped_create(self_client, *args, **kwargs):
                # Inject context before the call
                messages = kwargs.get("messages", args[0] if args else [])
                messages = OpenAIProvider._inject_context(
                    messages, 
                    self.aimemo
                )
                kwargs["messages"] = messages
                
                # Call original method
                response = original_create(self_client, *args, **kwargs)
                
                # Store the conversation
                OpenAIProvider._store_conversation(
                    messages,
                    response,
                    self.aimemo
                )
                
                return response
            
            openai.resources.chat.completions.Completions.create = wrapped_create
    
    def _unpatch(self):
        """Restore original OpenAI methods."""
        try:
            import openai
        except ImportError:
            return
        
        if "chat_create" in self._original_methods:
            openai.resources.chat.completions.Completions.create = self._original_methods["chat_create"]
    
    @staticmethod
    def _inject_context(messages: List[Dict], aimemo: "AIMemo") -> List[Dict]:
        """Inject relevant context into messages."""
        if not messages:
            return messages
        
        # Get the last user message as query
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        if not last_user_msg:
            return messages
        
        # Search for relevant context
        context = aimemo.get_context(last_user_msg, limit=aimemo.config.max_context_memories)
        
        if context:
            # Insert context as system message at the beginning
            context_msg = {
                "role": "system",
                "content": f"{context}\n\nUse this context when relevant to the conversation."
            }
            return [context_msg] + messages
        
        return messages
    
    @staticmethod
    def _store_conversation(messages: List[Dict], response: Any, aimemo: "AIMemo"):
        """Store conversation in memory."""
        # Extract user message and assistant response
        user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_msg = msg.get("content", "")
                break
        
        if hasattr(response, "choices") and response.choices:
            assistant_msg = response.choices[0].message.content
            
            # Store as memory
            if user_msg and assistant_msg:
                aimemo.add_memory(
                    content=f"User: {user_msg}\nAssistant: {assistant_msg}",
                    metadata={
                        "type": "conversation",
                        "model": getattr(response, "model", "unknown"),
                    },
                    tags=["conversation", "openai"],
                )


class AnthropicProvider(BaseProvider):
    """Anthropic API interceptor."""
    
    def _patch(self):
        """Patch Anthropic message creation."""
        try:
            import anthropic
        except ImportError:
            return
        
        # Store original method
        if hasattr(anthropic.Anthropic, "messages"):
            original_create = anthropic.resources.messages.Messages.create
            self._original_methods["messages_create"] = original_create
            
            @functools.wraps(original_create)
            def wrapped_create(self_client, *args, **kwargs):
                # Inject context
                messages = kwargs.get("messages", args[0] if args else [])
                messages = AnthropicProvider._inject_context(
                    messages,
                    self.aimemo
                )
                kwargs["messages"] = messages
                
                # Call original
                response = original_create(self_client, *args, **kwargs)
                
                # Store conversation
                AnthropicProvider._store_conversation(
                    messages,
                    response,
                    self.aimemo
                )
                
                return response
            
            anthropic.resources.messages.Messages.create = wrapped_create
    
    def _unpatch(self):
        """Restore original Anthropic methods."""
        try:
            import anthropic
        except ImportError:
            return
        
        if "messages_create" in self._original_methods:
            anthropic.resources.messages.Messages.create = self._original_methods["messages_create"]
    
    @staticmethod
    def _inject_context(messages: List[Dict], aimemo: "AIMemo") -> List[Dict]:
        """Inject context for Anthropic."""
        if not messages:
            return messages
        
        # Get last user message
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        item.get("text", "") 
                        for item in content 
                        if item.get("type") == "text"
                    )
                last_user_msg = content
                break
        
        if not last_user_msg:
            return messages
        
        # Get context
        context = aimemo.get_context(last_user_msg, limit=aimemo.config.max_context_memories)
        
        if context:
            # Prepend context to first user message
            for i, msg in enumerate(messages):
                if msg.get("role") == "user":
                    current_content = msg.get("content", "")
                    messages[i]["content"] = f"{context}\n\n{current_content}"
                    break
        
        return messages
    
    @staticmethod
    def _store_conversation(messages: List[Dict], response: Any, aimemo: "AIMemo"):
        """Store Anthropic conversation."""
        user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        item.get("text", "")
                        for item in content
                        if item.get("type") == "text"
                    )
                user_msg = content
                break
        
        if hasattr(response, "content") and response.content:
            assistant_msg = ""
            for block in response.content:
                if hasattr(block, "text"):
                    assistant_msg += block.text
            
            if user_msg and assistant_msg:
                aimemo.add_memory(
                    content=f"User: {user_msg}\nAssistant: {assistant_msg}",
                    metadata={
                        "type": "conversation",
                        "model": getattr(response, "model", "unknown"),
                    },
                    tags=["conversation", "anthropic"],
                )

