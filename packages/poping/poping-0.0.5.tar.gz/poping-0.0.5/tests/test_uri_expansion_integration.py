"""Integration tests for URI expansion in Session and Storage"""

import pytest
from unittest.mock import Mock, patch

from poping._agent import Session, Agent
from poping.storage import Storage
from poping.client import PopingClient


class TestSessionURIExpansion:
    """Test URI expansion in Session class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock client and agent
        self.mock_client = Mock(spec=PopingClient)
        self.mock_client._http = Mock()

        self.mock_agent = Mock(spec=Agent)
        self.mock_agent.client = self.mock_client
        self.mock_agent.agent_id = "agt_test"
        self.mock_agent.config = Mock()
        self.mock_agent.config.enable_context = False
        self.mock_agent.config.local_tools = []
        self.mock_agent.tool_registry = Mock()
        self.mock_agent.tool_registry.cloud_tools = []

        # Create session
        self.session = Session(
            agent=self.mock_agent,
            client_id="alice",
            session_id="sess_001",
            client=self.mock_client,
            project_id="prj_123",
        )

    def test_expand_uri_storage_simplified(self):
        """Test expanding simplified @storage URI"""
        uri = "@storage://resume.pdf"
        expanded = self.session._expand_uri(uri)
        assert expanded == "@storage[alice]://resume.pdf"

    def test_expand_uri_session_simplified(self):
        """Test expanding simplified @session URI"""
        uri = "@session://images/gen.png"
        expanded = self.session._expand_uri(uri)
        assert expanded == "@session[alice/sess_001]://images/gen.png"

    def test_expand_uri_memory_simplified(self):
        """Test expanding simplified @memory URI"""
        uri = "@memory://profile.json"
        expanded = self.session._expand_uri(uri)
        assert expanded == "@memory[alice]://profile.json"

    def test_expand_uri_complete_unchanged(self):
        """Test complete URI returns unchanged"""
        uri = "@storage[bob]://file.pdf"
        expanded = self.session._expand_uri(uri)
        assert expanded == uri

    def test_expand_uri_shared_unchanged(self):
        """Test @storage[shared] returns unchanged"""
        uri = "@storage[shared]://logo.png"
        expanded = self.session._expand_uri(uri)
        assert expanded == uri

    def test_expand_uris_in_text_single(self):
        """Test expanding single URI in text"""
        text = "Check @storage://resume.pdf for details"
        expanded = self.session._expand_uris_in_text(text)
        assert expanded == "Check @storage[alice]://resume.pdf for details"

    def test_expand_uris_in_text_multiple(self):
        """Test expanding multiple URIs in text"""
        text = "See @storage://doc.pdf and @session://img.png"
        expanded = self.session._expand_uris_in_text(text)
        assert "@storage[alice]://doc.pdf" in expanded
        assert "@session[alice/sess_001]://img.png" in expanded

    def test_expand_uris_in_text_mixed(self):
        """Test expanding mixed simplified and complete URIs"""
        text = "My @storage://file.pdf and shared @storage[shared]://logo.png"
        expanded = self.session._expand_uris_in_text(text)
        assert "@storage[alice]://file.pdf" in expanded
        assert "@storage[shared]://logo.png" in expanded

    def test_expand_uris_in_content_text_block(self):
        """Test expanding URIs in text content block"""
        content = [{"type": "text", "text": "Check @storage://file.pdf"}]
        expanded = self.session._expand_uris_in_content(content)
        assert len(expanded) == 1
        assert expanded[0]["type"] == "text"
        assert expanded[0]["text"] == "Check @storage[alice]://file.pdf"

    def test_expand_uris_in_content_multiple_blocks(self):
        """Test expanding URIs in multiple content blocks"""
        content = [
            {"type": "text", "text": "First @storage://a.pdf"},
            {"type": "text", "text": "Second @session://b.png"},
        ]
        expanded = self.session._expand_uris_in_content(content)
        assert len(expanded) == 2
        assert expanded[0]["text"] == "First @storage[alice]://a.pdf"
        assert expanded[1]["text"] == "Second @session[alice/sess_001]://b.png"

    def test_expand_uris_in_content_image_url(self):
        """Test expanding URI in image source URL"""
        content = [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "@storage://image.png",
                },
            }
        ]
        expanded = self.session._expand_uris_in_content(content)
        assert expanded[0]["source"]["url"] == "@storage[alice]://image.png"

    def test_expand_uris_in_content_image_base64_unchanged(self):
        """Test base64 image source unchanged"""
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": "iVBORw0KGgoAAAANS...",
                },
            }
        ]
        expanded = self.session._expand_uris_in_content(content)
        assert expanded[0]["source"]["type"] == "base64"
        assert "data" in expanded[0]["source"]

    def test_chat_legacy_expands_uris(self):
        """Test legacy chat mode expands URIs before sending"""
        # Mock HTTP response
        self.mock_client._http._request.return_value = {
            "message": "Response text"
        }

        # Call chat with simplified URI
        response = self.session._chat_legacy([
            {"type": "text", "text": "Analyze @storage://file.pdf"}
        ])

        assert response == "Response text"

        # Verify HTTP request was made with expanded URI
        self.mock_client._http._request.assert_called_once()
        call_args = self.mock_client._http._request.call_args

        # Check that content was expanded
        content = call_args[1]["data"]["content"]
        assert content[0]["text"] == "Analyze @storage[alice]://file.pdf"


class TestStorageURIExpansion:
    """Test URI expansion in Storage class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock HTTP client
        self.mock_http = Mock()

        # Create storage with context
        self.storage = Storage(
            client=self.mock_http,
            client_id="alice",
            session_id="sess_001",
        )

    def test_expand_uri_with_context(self):
        """Test URI expansion with client_id context"""
        uri = "@storage://file.pdf"
        expanded = self.storage._expand_uri(uri)
        assert expanded == "@storage[alice]://file.pdf"

    def test_expand_uri_session_with_context(self):
        """Test @session URI expansion with session_id context"""
        uri = "@session://images/gen.png"
        expanded = self.storage._expand_uri(uri)
        assert expanded == "@session[alice/sess_001]://images/gen.png"

    def test_expand_uri_complete_unchanged(self):
        """Test complete URI unchanged"""
        uri = "@storage[bob]://file.pdf"
        expanded = self.storage._expand_uri(uri)
        assert expanded == uri

    def test_expand_uri_no_context(self):
        """Test URI expansion without context returns original"""
        storage_no_context = Storage(client=self.mock_http)
        uri = "@storage://file.pdf"
        expanded = storage_no_context._expand_uri(uri)
        assert expanded == uri  # Returns unchanged

    def test_expand_uri_non_uri_unchanged(self):
        """Test non-URI string returns unchanged"""
        non_uri = "regular_resource_id"
        expanded = self.storage._expand_uri(non_uri)
        assert expanded == non_uri

    def test_get_url_expands_uri(self):
        """Test get_url expands simplified URI"""
        # Mock HTTP response
        self.mock_http._request.return_value = {
            "url": "https://cdn.example.com/signed-url"
        }

        # Call with simplified URI
        url = self.storage.get_url("@storage://file.pdf")
        assert url == "https://cdn.example.com/signed-url"

        # Verify request was made with expanded URI
        self.mock_http._request.assert_called_once()
        call_args = self.mock_http._request.call_args
        endpoint = call_args[1]["endpoint"]

        assert "@storage[alice]://file.pdf" in endpoint

    def test_download_expands_uri(self):
        """Test download expands simplified URI"""
        # Mock HTTP response with iter_content
        mock_response = Mock()
        mock_response.iter_content.return_value = [b"file content"]
        self.mock_http._request.return_value = mock_response

        # Call with simplified URI
        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", create=True):
                self.storage.download("@storage://file.pdf", "/tmp/out.pdf")

        # Verify request was made with expanded URI
        self.mock_http._request.assert_called_once()
        call_args = self.mock_http._request.call_args
        endpoint = call_args[1]["endpoint"]

        assert "@storage[alice]://file.pdf" in endpoint


class TestBackwardCompatibility:
    """Test backward compatibility with complete URIs"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=PopingClient)
        self.mock_client._http = Mock()

        self.mock_agent = Mock(spec=Agent)
        self.mock_agent.client = self.mock_client
        self.mock_agent.agent_id = "agt_test"
        self.mock_agent.config = Mock()
        self.mock_agent.config.enable_context = False
        self.mock_agent.config.local_tools = []
        self.mock_agent.tool_registry = Mock()
        self.mock_agent.tool_registry.cloud_tools = []

        self.session = Session(
            agent=self.mock_agent,
            client_id="alice",
            session_id="sess_001",
            client=self.mock_client,
        )

    def test_complete_uri_passes_through(self):
        """Test complete URIs pass through unchanged"""
        uri = "@storage[bob]://shared_file.pdf"
        expanded = self.session._expand_uri(uri)
        assert expanded == uri

    def test_shared_storage_passes_through(self):
        """Test @storage[shared] passes through"""
        uri = "@storage[shared]://company_logo.png"
        expanded = self.session._expand_uri(uri)
        assert expanded == uri

    def test_mixed_uris_in_text(self):
        """Test text with both simplified and complete URIs"""
        text = "My @storage://private.pdf and team @storage[shared]://public.pdf"
        expanded = self.session._expand_uris_in_text(text)

        # Simplified expands, complete unchanged
        assert "@storage[alice]://private.pdf" in expanded
        assert "@storage[shared]://public.pdf" in expanded

