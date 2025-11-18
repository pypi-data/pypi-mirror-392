"""
PACT Memory for LangChain
=========================
Drop-in replacement for LangChain memory with emotional intelligence.

Part of PACT by NeurobloomAI
https://github.com/neurobloomai/pact-hx
"""

from typing import Any, Dict, List, Optional
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseMessage
from pydantic import Field, PrivateAttr

from .client import PACTClient


class PACTMemory(BaseChatMemory):
    """
    LangChain memory with emotional intelligence and context consolidation.
    
    Drop-in replacement for ConversationBufferMemory that tracks:
    - Emotional states across conversation
    - Topic importance and priority
    - Context consolidation (summarizes old messages)
    - Relationship patterns
    
    Usage:
        memory = PACTMemory(api_key="your_key")
        conversation = ConversationChain(llm=llm, memory=memory)
    """
    
    api_key: str = Field(..., description="PACT API key")
    api_url: str = Field(
        default="https://api.neurobloom.ai/pact/v1",
        description="PACT API endpoint"
    )
    
    # Core PACT features
    emotional_tracking: bool = Field(
        default=True,
        description="Track emotional states in conversation"
    )
    context_consolidation: bool = Field(
        default=True,
        description="Automatically consolidate old context"
    )
    consolidation_threshold: int = Field(
        default=10,
        description="Number of messages before consolidation kicks in"
    )
    
    # Memory behavior
    max_token_limit: Optional[int] = Field(
        default=2000,
        description="Max tokens to return in memory context"
    )
    return_emotional_context: bool = Field(
        default=True,
        description="Include emotional metadata in loaded variables"
    )
    
    # Internal state
    session_id: Optional[str] = Field(default=None, description="PACT session ID")
    
    # Private attribute for Pydantic 2.0 compatibility
    _pact_client: Any = PrivateAttr(default=None)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pact_client = PACTClient(
            api_key=self.api_key,
            api_url=self.api_url
        )
        # Create session on init
        self.session_id = self._pact_client.create_session()
    
    # REQUIRED: LangChain BaseChatMemory interface
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables (required by LangChain)."""
        if self.return_emotional_context:
            return ["history", "emotional_state", "context_summary"]
        return ["history"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load conversation memory with PACT enhancements.
        
        Returns:
            dict: Contains 'history' plus optional emotional context
        """
        # Fetch from PACT API
        response = self._pact_client.get_context(
            session_id=self.session_id,
            max_tokens=self.max_token_limit,
            include_emotional=self.emotional_tracking
        )
        
        # Format for LangChain
        result = {
            "history": self._format_messages(response["messages"])
        }
        
        # Add PACT-specific context
        if self.return_emotional_context:
            result["emotional_state"] = response.get("emotional_state", "neutral")
            result["context_summary"] = response.get("consolidated_summary", "")
        
        return result
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save conversation turn to PACT memory.
        
        Args:
            inputs: User input (typically {"input": "user message"})
            outputs: AI output (typically {"output": "ai response"})
        """
        # Extract messages
        user_message = inputs.get(self.input_key, "")
        ai_message = outputs.get(self.output_key, "")
        
        # Send to PACT API
        self._pact_client.save_interaction(
            session_id=self.session_id,
            user_message=user_message,
            ai_message=ai_message,
            track_emotion=self.emotional_tracking,
            consolidate=self.context_consolidation
        )
    
    def clear(self) -> None:
        """Clear memory and reset session."""
        if self.session_id:
            self._pact_client.delete_session(self.session_id)
        self.session_id = self._pact_client.create_session()
    
    # PACT-specific methods
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """
        Get current emotional state analysis.
        
        Returns:
            dict: Current emotional state, valence, key emotions
        """
        return self._pact_client.get_emotional_state(self.session_id)
    
    def get_context_graph(self) -> Dict[str, Any]:
        """
        Get full PACT memory graph for visualization.
        
        Returns:
            dict: Node/edge graph structure of conversation context
        """
        return self._pact_client.get_memory_graph(self.session_id)
    
    def force_consolidation(self) -> Dict[str, Any]:
        """
        Manually trigger context consolidation.
        
        Returns:
            dict: Consolidation summary and stats
        """
        return self._pact_client.consolidate_context(self.session_id)
    
    def set_context_priority(self, topic: str, priority: str) -> None:
        """
        Manually set priority for a topic/context.
        
        Args:
            topic: Topic identifier
            priority: "high", "medium", or "low"
        """
        self._pact_client.set_priority(
            session_id=self.session_id,
            topic=topic,
            priority=priority
        )
    
    # Helper methods
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format PACT messages for LangChain."""
        formatted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            formatted.append(f"{role.capitalize()}: {content}")
        return "\n".join(formatted)
    
    # Context manager support (optional, but nice)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Could auto-save or cleanup here
        pass


# Async version (for async LangChain chains)

class AsyncPACTMemory(PACTMemory):
    """Async version of PACTMemory for async LangChain chains."""
    
    async def aload_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Async version of load_memory_variables."""
        response = await self._pact_client.aget_context(
            session_id=self.session_id,
            max_tokens=self.max_token_limit,
            include_emotional=self.emotional_tracking
        )
        
        result = {
            "history": self._format_messages(response["messages"])
        }
        
        if self.return_emotional_context:
            result["emotional_state"] = response.get("emotional_state", "neutral")
            result["context_summary"] = response.get("consolidated_summary", "")
        
        return result
    
    async def asave_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Async version of save_context."""
        user_message = inputs.get(self.input_key, "")
        ai_message = outputs.get(self.output_key, "")
        
        await self._pact_client.asave_interaction(
            session_id=self.session_id,
            user_message=user_message,
            ai_message=ai_message,
            track_emotion=self.emotional_tracking,
            consolidate=self.context_consolidation
        )


# Convenience factory functions

def create_pact_memory(
    api_key: str,
    emotional_tracking: bool = True,
    **kwargs
) -> PACTMemory:
    """
    Convenience function to create PACTMemory instance.
    
    Example:
        memory = create_pact_memory(api_key="sk_test_123")
    """
    return PACTMemory(
        api_key=api_key,
        emotional_tracking=emotional_tracking,
        **kwargs
    )
