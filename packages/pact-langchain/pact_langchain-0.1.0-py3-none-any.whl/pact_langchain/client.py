"""
PACT API Client
===============
Low-level client for PACT Memory API.

Part of PACT by NeurobloomAI
https://github.com/neurobloomai/pact-hx
"""

import requests
from typing import Dict, Any, List, Optional


class PACTClient:
    """Low-level client for PACT API."""
    
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize PACT API client.
        
        Args:
            api_key: PACT API key (get one at neurobloom.ai)
            api_url: PACT API endpoint URL
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "pact-langchain/0.1.0"
        }
    
    def create_session(self) -> str:
        """
        Create new conversation session.
        
        Returns:
            str: Session ID
        """
        response = requests.post(
            f"{self.api_url}/sessions",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["session_id"]
    
    def get_context(
        self,
        session_id: str,
        max_tokens: int = 2000,
        include_emotional: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve conversation context.
        
        Args:
            session_id: Session identifier
            max_tokens: Maximum tokens to return
            include_emotional: Include emotional metadata
            
        Returns:
            dict: Context data with messages and metadata
        """
        response = requests.get(
            f"{self.api_url}/sessions/{session_id}/context",
            headers=self.headers,
            params={
                "max_tokens": max_tokens,
                "include_emotional": include_emotional
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def save_interaction(
        self,
        session_id: str,
        user_message: str,
        ai_message: str,
        track_emotion: bool = True,
        consolidate: bool = True
    ) -> Dict[str, Any]:
        """
        Save conversation turn.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            ai_message: AI's response
            track_emotion: Enable emotional tracking
            consolidate: Enable context consolidation
            
        Returns:
            dict: Save confirmation with metadata
        """
        response = requests.post(
            f"{self.api_url}/sessions/{session_id}/interactions",
            headers=self.headers,
            json={
                "user_message": user_message,
                "ai_message": ai_message,
                "track_emotion": track_emotion,
                "consolidate": consolidate
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete session and all associated data.
        
        Args:
            session_id: Session identifier
        """
        response = requests.delete(
            f"{self.api_url}/sessions/{session_id}",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
    
    def get_emotional_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current emotional state analysis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Emotional state data
        """
        response = requests.get(
            f"{self.api_url}/sessions/{session_id}/emotional_state",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_memory_graph(self, session_id: str) -> Dict[str, Any]:
        """
        Get memory graph structure for visualization.
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Graph with nodes and edges
        """
        response = requests.get(
            f"{self.api_url}/sessions/{session_id}/graph",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def consolidate_context(self, session_id: str) -> Dict[str, Any]:
        """
        Manually trigger context consolidation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Consolidation summary
        """
        response = requests.post(
            f"{self.api_url}/sessions/{session_id}/consolidate",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def set_priority(
        self,
        session_id: str,
        topic: str,
        priority: str
    ) -> None:
        """
        Set context priority for a topic.
        
        Args:
            session_id: Session identifier
            topic: Topic identifier
            priority: Priority level ("high", "medium", "low")
        """
        response = requests.post(
            f"{self.api_url}/sessions/{session_id}/priority",
            headers=self.headers,
            json={"topic": topic, "priority": priority},
            timeout=30
        )
        response.raise_for_status()
    
    # Async versions (using aiohttp would be better, but requests for now)
    
    async def aget_context(
        self,
        session_id: str,
        max_tokens: int = 2000,
        include_emotional: bool = True
    ) -> Dict[str, Any]:
        """Async version of get_context."""
        # TODO: Implement with aiohttp
        return self.get_context(session_id, max_tokens, include_emotional)
    
    async def asave_interaction(
        self,
        session_id: str,
        user_message: str,
        ai_message: str,
        track_emotion: bool = True,
        consolidate: bool = True
    ) -> Dict[str, Any]:
        """Async version of save_interaction."""
        # TODO: Implement with aiohttp
        return self.save_interaction(
            session_id, user_message, ai_message, track_emotion, consolidate
        )
