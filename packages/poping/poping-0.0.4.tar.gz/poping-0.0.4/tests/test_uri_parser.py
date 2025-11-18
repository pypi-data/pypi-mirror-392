"""
Unit tests for URI parser module (v2.0)

Tests updated for ARCHITECTURE.md v2.0:
- Field names: scheme → type, resource_id → subtype
- URI types: @session → @context
- New URI types: @resource, @dataset, @knowledge
"""

import pytest
from poping.uri_parser import URIParser, ParsedURI


class TestURIParser:
    """Test URI parsing and expansion (v2.0)"""

    # ========================================================================
    # Parsing Tests
    # ========================================================================

    def test_parse_simplified_storage_uri(self):
        """Test parsing simplified @storage URI"""
        parsed = URIParser.parse("@storage://resume.pdf")
        assert parsed.type == "storage"
        assert parsed.subtype is None
        assert parsed.path == "resume.pdf"
        assert parsed.is_simplified is True

    def test_parse_complete_storage_uri(self):
        """Test parsing complete @storage URI with client_id"""
        parsed = URIParser.parse("@storage[alice]://resume.pdf")
        assert parsed.type == "storage"
        assert parsed.subtype == "alice"
        assert parsed.path == "resume.pdf"
        assert parsed.is_simplified is False

    def test_parse_simplified_context_uri(self):
        """Test parsing simplified @context URI (replaces @session)"""
        parsed = URIParser.parse("@context://images/gen.png")
        assert parsed.type == "context"
        assert parsed.subtype is None
        assert parsed.path == "images/gen.png"
        assert parsed.is_simplified is True

    def test_parse_complete_context_uri(self):
        """Test parsing complete @context URI with client_id/session_id"""
        parsed = URIParser.parse("@context[alice/sess_001]://images/gen.png")
        assert parsed.type == "context"
        assert parsed.subtype == "alice/sess_001"
        assert parsed.path == "images/gen.png"
        assert parsed.is_simplified is False

    def test_parse_memory_uri(self):
        """Test parsing @memory URI"""
        parsed = URIParser.parse("@memory[alice]://profile_001.json")
        assert parsed.type == "memory"
        assert parsed.subtype == "alice"
        assert parsed.path == "profile_001.json"
        assert parsed.is_simplified is False

    def test_parse_shared_storage_uri(self):
        """Test parsing @storage[shared] URI"""
        parsed = URIParser.parse("@storage[shared]://logo.png")
        assert parsed.type == "storage"
        assert parsed.subtype == "shared"
        assert parsed.path == "logo.png"
        assert parsed.is_simplified is False

    def test_parse_resource_uri(self):
        """Test parsing @resource[type] URI"""
        parsed = URIParser.parse("@resource[agent]://agt_001.json")
        assert parsed.type == "resource"
        assert parsed.subtype == "agent"
        assert parsed.path == "agt_001.json"
        assert parsed.is_simplified is False

    def test_parse_dataset_uri(self):
        """Test parsing @dataset[name] URI"""
        parsed = URIParser.parse("@dataset[customer_data]://rec_001.json")
        assert parsed.type == "dataset"
        assert parsed.subtype == "customer_data"
        assert parsed.path == "rec_001.json"
        assert parsed.is_simplified is False

    def test_parse_knowledge_uri(self):
        """Test parsing @knowledge[name] URI"""
        parsed = URIParser.parse("@knowledge[design_docs]://doc_001.pdf")
        assert parsed.type == "knowledge"
        assert parsed.subtype == "design_docs"
        assert parsed.path == "doc_001.pdf"
        assert parsed.is_simplified is False

    def test_parse_nested_path(self):
        """Test parsing URI with nested path"""
        parsed = URIParser.parse("@storage://documents/contracts/agreement.pdf")
        assert parsed.type == "storage"
        assert parsed.path == "documents/contracts/agreement.pdf"

    def test_parse_invalid_format(self):
        """Test parsing invalid URI format"""
        with pytest.raises(ValueError, match="Invalid URI"):
            URIParser.parse("not-a-uri")

        with pytest.raises(ValueError, match="Invalid URI format"):
            URIParser.parse("@storage:missing-slashes")

    # ========================================================================
    # Expansion Tests
    # ========================================================================

    def test_expand_storage_uri(self):
        """Test expanding simplified @storage URI"""
        expanded = URIParser.expand("@storage://resume.pdf", client_id="alice", session_id=None)
        assert expanded == "@storage[alice]://resume.pdf"

    def test_expand_context_uri(self):
        """Test expanding simplified @context URI (replaces @session)"""
        expanded = URIParser.expand(
            "@context://images/gen.png", client_id="alice", session_id="sess_001"
        )
        assert expanded == "@context[alice/sess_001]://images/gen.png"

    def test_expand_memory_uri(self):
        """Test expanding simplified @memory URI"""
        expanded = URIParser.expand("@memory://profile_001.json", client_id="alice", session_id=None)
        assert expanded == "@memory[alice]://profile_001.json"

    def test_expand_complete_uri_unchanged(self):
        """Test that complete URI is unchanged"""
        original = "@storage[alice]://resume.pdf"
        expanded = URIParser.expand(original, client_id="bob", session_id=None)
        assert expanded == original

    def test_expand_shared_storage_unchanged(self):
        """Test that @storage[shared] is unchanged"""
        original = "@storage[shared]://logo.png"
        expanded = URIParser.expand(original, client_id="alice", session_id=None)
        assert expanded == original

    def test_expand_resource_requires_subtype(self):
        """Test that @resource without subtype raises error"""
        with pytest.raises(ValueError, match="requires subtype"):
            URIParser.expand("@resource://agt_001.json", client_id="alice", session_id=None)

    def test_expand_missing_client_id_raises(self):
        """Test expansion without client_id raises error"""
        with pytest.raises(ValueError, match="Missing client_id"):
            URIParser.expand("@storage://file.pdf", client_id=None, session_id=None)

    def test_expand_missing_session_id_raises(self):
        """Test @context expansion without session_id raises error"""
        with pytest.raises(ValueError, match="Missing client_id or session_id"):
            URIParser.expand("@context://images/gen.png", client_id="alice", session_id=None)

    # ========================================================================
    # Extraction Tests
    # ========================================================================

    def test_extract_single_uri(self):
        """Test extracting single URI from text"""
        text = "Please see @storage://document.pdf for details"
        uris = URIParser.extract_uris_from_text(text)
        assert uris == ["@storage://document.pdf"]

    def test_extract_multiple_uris(self):
        """Test extracting multiple URIs from text"""
        text = "Check @storage://doc.txt and @context[alice/s1]://img.png"
        uris = URIParser.extract_uris_from_text(text)
        assert uris == ["@storage://doc.txt", "@context[alice/s1]://img.png"]

    def test_extract_uris_with_punctuation(self):
        """Test extraction removes trailing punctuation"""
        text = "See @storage://file.pdf. Also @context://img.png!"
        uris = URIParser.extract_uris_from_text(text)
        assert uris == ["@storage://file.pdf", "@context://img.png"]

    def test_extract_uris_in_parentheses(self):
        """Test extraction works with URIs in parentheses"""
        text = "File (@storage://doc.txt) is important"
        uris = URIParser.extract_uris_from_text(text)
        assert uris == ["@storage://doc.txt"]

    def test_extract_no_uris(self):
        """Test extraction from text without URIs"""
        text = "This text has no URIs in it"
        uris = URIParser.extract_uris_from_text(text)
        assert uris == []

    def test_extract_from_empty_text(self):
        """Test extraction from empty text"""
        uris = URIParser.extract_uris_from_text("")
        assert uris == []

    def test_extract_from_none(self):
        """Test extraction from None"""
        uris = URIParser.extract_uris_from_text(None)
        assert uris == []

    # ========================================================================
    # v2.0 Specific Tests
    # ========================================================================

    def test_all_v2_uri_types(self):
        """Test all v2.0 URI types can be parsed"""
        test_uris = [
            "@context://images/gen.png",
            "@storage://resume.pdf",
            "@storage[shared]://logo.png",
            "@memory://profile_001.json",
            "@resource[agent]://agt_001.json",
            "@resource[toolset]://tls_001.json",
            "@resource[mcp]://mcp_001.json",
            "@dataset[customer_data]://rec_001.json",
            "@knowledge[design_docs]://doc_001.pdf",
        ]

        for uri in test_uris:
            parsed = URIParser.parse(uri)
            assert parsed.type is not None
            assert parsed.path is not None
            assert isinstance(parsed.is_simplified, bool)

    def test_backward_compatibility_session_renamed_to_context(self):
        """Test that @context replaces @session in v2.0"""
        # Old v1: @session://images/gen.png
        # New v2: @context://images/gen.png

        parsed = URIParser.parse("@context://images/gen.png")
        assert parsed.type == "context"

        # Expansion with session_id
        expanded = URIParser.expand(
            "@context://images/gen.png", client_id="alice", session_id="sess_001"
        )
        assert expanded == "@context[alice/sess_001]://images/gen.png"
