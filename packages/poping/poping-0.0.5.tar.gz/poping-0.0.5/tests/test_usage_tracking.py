"""
Unit tests for session-level usage tracking

Tests the conv.usage property and accumulation logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from poping._agent import Session, Agent, AgentConfig
from poping.client import PopingClient


class TestUsageTracking:
    """Test suite for session usage tracking"""

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

    def test_accumulate_usage_basic(self):
        """Test basic usage accumulation"""
        usage_data = {"input_tokens": 100, "output_tokens": 50}

        # Mock pricing calculation
        with patch("llm.pricing.calculate_cost", return_value=0.123):
            self.session._accumulate_usage(usage_data)

        usage = self.session.usage
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50
        assert usage["total_tokens"] == 150
        assert usage["cost"] == 0.123

    def test_accumulate_usage_multiple_calls(self):
        """Test accumulation across multiple calls"""
        # First call
        with patch("llm.pricing.calculate_cost", return_value=0.100):
            self.session._accumulate_usage({"input_tokens": 100, "output_tokens": 50})

        # Second call
        with patch("llm.pricing.calculate_cost", return_value=0.200):
            self.session._accumulate_usage({"input_tokens": 200, "output_tokens": 150})

        # Third call
        with patch("llm.pricing.calculate_cost", return_value=0.050):
            self.session._accumulate_usage({"input_tokens": 50, "output_tokens": 25})

        usage = self.session.usage
        assert usage["input_tokens"] == 350  # 100 + 200 + 50
        assert usage["output_tokens"] == 225  # 50 + 150 + 25
        assert usage["total_tokens"] == 575
        assert usage["cost"] == 0.350  # 0.100 + 0.200 + 0.050

    def test_accumulate_usage_handles_missing_pricing(self):
        """Test that accumulation works even if pricing module unavailable"""
        # Simulate ImportError for pricing module
        with patch("llm.pricing.calculate_cost", side_effect=ImportError):
            self.session._accumulate_usage({"input_tokens": 100, "output_tokens": 50})

        usage = self.session.usage
        # Tokens should still be accumulated
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50
        assert usage["total_tokens"] == 150
        # Cost remains 0 (pricing unavailable)
        assert usage["cost"] == 0.0

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

        with patch("llm.pricing.calculate_cost", return_value=0.010):
            response = self.session._chat_legacy([{"type": "text", "text": "Hi"}])

        assert response == "Hello!"

        usage = self.session.usage
        assert usage["input_tokens"] == 10
        assert usage["output_tokens"] == 5
        assert usage["cost"] == 0.010

    def test_chat_multiple_turns_accumulate(self):
        """Test that multiple chat turns accumulate usage"""
        # Mock responses with different usage
        responses = [
            {"message": "Response 1", "usage": {"input_tokens": 10, "output_tokens": 5}},
            {"message": "Response 2", "usage": {"input_tokens": 20, "output_tokens": 15}},
            {"message": "Response 3", "usage": {"input_tokens": 30, "output_tokens": 25}},
        ]

        costs = [0.010, 0.025, 0.045]

        for i, (response_data, cost) in enumerate(zip(responses, costs)):
            self.mock_client._http._request.return_value = response_data

            with patch("llm.pricing.calculate_cost", return_value=cost):
                self.session._chat_legacy([{"type": "text", "text": f"Message {i + 1}"}])

        usage = self.session.usage
        assert usage["input_tokens"] == 60  # 10 + 20 + 30
        assert usage["output_tokens"] == 45  # 5 + 15 + 25
        assert usage["total_tokens"] == 105
        assert abs(usage["cost"] - 0.080) < 0.0001  # 0.010 + 0.025 + 0.045

    def test_usage_with_real_pricing(self):
        """Test usage calculation with actual pricing module"""
        # This test requires the pricing module to be available
        try:
            from llm.pricing import calculate_cost

            # Use real pricing for claude-sonnet-4-5-20250929
            usage_data = {"input_tokens": 640, "output_tokens": 57}

            self.session._accumulate_usage(usage_data)

            usage = self.session.usage
            assert usage["input_tokens"] == 640
            assert usage["output_tokens"] == 57
            assert usage["total_tokens"] == 697

            # Cost should be: (640/1000 * 0.4) + (57/1000 * 2.0) = 0.256 + 0.114 = 0.37
            expected_cost = 0.37
            assert abs(usage["cost"] - expected_cost) < 0.001

        except ImportError:
            pytest.skip("Pricing module not available in test environment")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
