"""
Basic tests for PACT Memory

Part of PACT by NeurobloomAI
https://github.com/neurobloomai/pact-hx
"""

import pytest
from unittest.mock import Mock, patch
from pact_langchain import PACTMemory, create_pact_memory
from pact_langchain.client import PACTClient


class TestPACTMemory:
    """Test suite for PACTMemory class."""
    
    @patch('pact_langchain.memory.PACTClient')
    def test_initialization(self, mock_client_class):
        """Test PACTMemory initialization."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session_123"
        mock_client_class.return_value = mock_client
        
        memory = PACTMemory(api_key="test_key")
        
        assert memory.api_key == "test_key"
        assert memory.session_id == "test_session_123"
        assert memory.emotional_tracking == True
        assert memory.context_consolidation == True
    
    @patch('pact_langchain.memory.PACTClient')
    def test_memory_variables(self, mock_client_class):
        """Test memory_variables property."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session"
        mock_client_class.return_value = mock_client
        
        # With emotional context
        memory = PACTMemory(api_key="test_key", return_emotional_context=True)
        assert set(memory.memory_variables) == {"history", "emotional_state", "context_summary"}
        
        # Without emotional context
        memory = PACTMemory(api_key="test_key", return_emotional_context=False)
        assert memory.memory_variables == ["history"]
    
    @patch('pact_langchain.memory.PACTClient')
    def test_save_context(self, mock_client_class):
        """Test save_context method."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session"
        mock_client_class.return_value = mock_client
        
        memory = PACTMemory(api_key="test_key")
        
        inputs = {"input": "Hello"}
        outputs = {"output": "Hi there!"}
        
        memory.save_context(inputs, outputs)
        
        mock_client.save_interaction.assert_called_once_with(
            session_id="test_session",
            user_message="Hello",
            ai_message="Hi there!",
            track_emotion=True,
            consolidate=True
        )
    
    @patch('pact_langchain.memory.PACTClient')
    def test_load_memory_variables(self, mock_client_class):
        """Test load_memory_variables method."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session"
        mock_client.get_context.return_value = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "emotional_state": "neutral",
            "consolidated_summary": "Brief greeting exchange"
        }
        mock_client_class.return_value = mock_client
        
        memory = PACTMemory(api_key="test_key", return_emotional_context=True)
        
        result = memory.load_memory_variables({})
        
        assert "history" in result
        assert "emotional_state" in result
        assert "context_summary" in result
        assert result["emotional_state"] == "neutral"
    
    @patch('pact_langchain.memory.PACTClient')
    def test_clear(self, mock_client_class):
        """Test clear method."""
        mock_client = Mock()
        mock_client.create_session.side_effect = ["session1", "session2"]
        mock_client_class.return_value = mock_client
        
        memory = PACTMemory(api_key="test_key")
        old_session = memory.session_id
        
        memory.clear()
        
        mock_client.delete_session.assert_called_once_with(old_session)
        assert memory.session_id == "session2"
    
    @patch('pact_langchain.memory.PACTClient')
    def test_get_emotional_state(self, mock_client_class):
        """Test get_emotional_state method."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session"
        mock_client.get_emotional_state.return_value = {
            "current_emotion": "happy",
            "valence": 0.8,
            "trend": "positive"
        }
        mock_client_class.return_value = mock_client
        
        memory = PACTMemory(api_key="test_key")
        state = memory.get_emotional_state()
        
        assert state["current_emotion"] == "happy"
        assert state["valence"] == 0.8


class TestPACTClient:
    """Test suite for PACTClient class."""
    
    def test_initialization(self):
        """Test client initialization."""
        client = PACTClient(api_key="test_key", api_url="https://api.test.com")
        
        assert client.api_key == "test_key"
        assert client.api_url == "https://api.test.com"
        assert "Bearer test_key" in client.headers["Authorization"]


class TestHelpers:
    """Test helper functions."""
    
    @patch('pact_langchain.memory.PACTClient')
    def test_create_pact_memory(self, mock_client_class):
        """Test create_pact_memory factory function."""
        mock_client = Mock()
        mock_client.create_session.return_value = "test_session"
        mock_client_class.return_value = mock_client
        
        memory = create_pact_memory(api_key="test_key", emotional_tracking=False)
        
        assert isinstance(memory, PACTMemory)
        assert memory.api_key == "test_key"
        assert memory.emotional_tracking == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
