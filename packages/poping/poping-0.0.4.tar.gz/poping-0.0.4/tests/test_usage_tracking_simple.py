"""
Simplified unit tests for session-level usage tracking

Tests the conv.usage property without backend dependencies.
"""

import sys
import pytest
from unittest.mock import Mock
from poping._agent import Session, Agent, AgentConfig
from poping.client import PopingClient


class TestUsageTrackingSimple:
    """Simplified test suite for session usage tracking"""

    def setup_method(self):
        """Setup test fixtures"""
        # Mock client
        self.mock_client = Mock(spec=PopingClient)
        self.mock_client._http = Mock()

        # Mock agent config
        self.mock_config = AgentConfig(
            llm="claude-sonnet-4-5-20250929",
            local_tools=[],
            cloud_tools=[],
        )

        # Mock agent
        self.mock_agent = Mock(spec=Agent)
        self.mock_agent.agent_id = "agt_test123"
        self.mock_agent.config = self.mock_config
        self.mock_agent.tool_registry = Mock()
        self.mock_agent.tool_registry.cloud_tools = []

        # Create session
        self.session = Session(
            agent=self.mock_agent,
            client_id="test_user",
            session_id="test_session",
            client=self.mock_client,
            project_id="prj_test",
        )

    def test_initial_usage_is_zero(self):
        """Test that initial usage is zero"""
        usage = self.session.usage

        assert usage["input_tokens"] == 0
        assert usage["output_tokens"] == 0
        assert usage["total_tokens"] == 0
        assert usage["cost"] == 0.0

    def test_usage_returns_copy(self):
        """Test that usage property returns a copy (not reference)"""
        usage1 = self.session.usage
        usage2 = self.session.usage

        # Modify first reference
        usage1["input_tokens"] = 999

        # Second reference should be unaffected
        assert usage2["input_tokens"] == 0

        # Actual accumulator should be unaffected
        assert self.session._usage_accumulator["input_tokens"] == 0

    def test_accumulate_usage_tokens_only(self):
        """Test basic token accumulation (without cost calculation)"""
        usage_data = {"input_tokens": 100, "output_tokens": 50}

        self.session._accumulate_usage(usage_data)

        usage = self.session.usage
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50
        assert usage["total_tokens"] == 150
        # Cost may be 0 if pricing module unavailable (which is fine)
        assert isinstance(usage["cost"], (int, float))

    def test_accumulate_usage_multiple_calls(self):
        """Test accumulation across multiple calls"""
        # First call
        self.session._accumulate_usage({"input_tokens": 100, "output_tokens": 50})

        # Second call
        self.session._accumulate_usage({"input_tokens": 200, "output_tokens": 150})

        # Third call
        self.session._accumulate_usage({"input_tokens": 50, "output_tokens": 25})

        usage = self.session.usage
        assert usage["input_tokens"] == 350  # 100 + 200 + 50
        assert usage["output_tokens"] == 225  # 50 + 150 + 25
        assert usage["total_tokens"] == 575

    def test_accumulate_usage_missing_tokens(self):
        """Test handling of missing token fields"""
        # Empty usage dict
        self.session._accumulate_usage({})

        usage = self.session.usage
        assert usage["input_tokens"] == 0
        assert usage["output_tokens"] == 0
        assert usage["total_tokens"] == 0

    def test_chat_accumulates_usage(self):
        """Test that chat() calls accumulate usage"""
        # Mock API response with usage
        self.mock_client._http._request.return_value = {
            "message": "Hello!",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        response = self.session._chat_legacy([{"type": "text", "text": "Hi"}])

        assert response == "Hello!"

        usage = self.session.usage
        assert usage["input_tokens"] == 10
        assert usage["output_tokens"] == 5
        assert usage["total_tokens"] == 15

    def test_chat_multiple_turns_accumulate(self):
        """Test that multiple chat turns accumulate usage"""
        # Mock responses with different usage
        responses = [
            {"message": "Response 1", "usage": {"input_tokens": 10, "output_tokens": 5}},
            {"message": "Response 2", "usage": {"input_tokens": 20, "output_tokens": 15}},
            {"message": "Response 3", "usage": {"input_tokens": 30, "output_tokens": 25}},
        ]

        for i, response_data in enumerate(responses):
            self.mock_client._http._request.return_value = response_data
            self.session._chat_legacy([{"type": "text", "text": f"Message {i + 1}"}])

        usage = self.session.usage
        assert usage["input_tokens"] == 60  # 10 + 20 + 30
        assert usage["output_tokens"] == 45  # 5 + 15 + 25
        assert usage["total_tokens"] == 105

    def test_chat_without_usage_field(self):
        """Test that chat works even if backend doesn't return usage"""
        # Mock API response without usage field
        self.mock_client._http._request.return_value = {
            "message": "Hello!",
            # No 'usage' field
        }

        response = self.session._chat_legacy([{"type": "text", "text": "Hi"}])

        assert response == "Hello!"

        # Usage should still be zero
        usage = self.session.usage
        assert usage["input_tokens"] == 0
        assert usage["output_tokens"] == 0
        assert usage["total_tokens"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
