"""
URI parsing and expansion utilities for ARCHITECTURE.md v2.0.

This module provides a small, focused API to:
  - Parse a URI into components (type, subtype, path)
  - Expand simplified URIs using user/session context
  - Extract all URIs from free-form text using regex

URI Format (v2.0)
-----------------
- Pattern: ``@<type>(?:[<subtype>])?://<path>``
- Examples (simplified):
  - ``@context://images/gen.png``
  - ``@storage://resume.pdf``
  - ``@memory://profile_001.json``
- Examples (complete):
  - ``@context[alice/sess_001]://images/gen.png``
  - ``@storage[alice]://resume.pdf``
  - ``@storage[shared]://logo.png``
  - ``@resource[agent]://agt_001.json``

URI Types (v2.0)
----------------
- ``@context://``          - Session temporary files
- ``@storage://``          - End user persistent files
- ``@storage[shared]://``  - Project shared files
- ``@memory://``           - Memory profiles
- ``@resource[type]://``   - Configurations (agent/toolset/mcp)
- ``@dataset[name]://``    - Dataset records
- ``@knowledge[name]://``  - Knowledge base documents

Expansion Rules
---------------
- Expandable types:
  - ``@context``  → requires ``client_id`` and ``session_id`` → ``@context[{client_id}/{session_id}]://``
  - ``@storage``  → requires ``client_id`` → ``@storage[{client_id}]://``
  - ``@memory``   → requires ``client_id`` → ``@memory[{client_id}]://``

- Non-expandable (already complete):
  - ``@storage[shared]`` - Shared project files
  - ``@resource[type]`` - Configurations
  - ``@dataset[name]`` - Dataset records
  - ``@knowledge[name]`` - Knowledge base docs

Error Handling
--------------
- ``ValueError`` for invalid URI format
- ``ValueError`` if required expansion context is missing
- URI extraction logs a warning on issues but does not raise

Design Principles
-----------------
- Simple, flat logic (minimal branching)
- Clear naming (e.g., ``is_simplified``)
- One purpose per function
- Comprehensive docstrings with examples
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import logging
import re


logger = logging.getLogger(__name__)


# Single pattern for all URI types
# Pattern: @{type}[{subtype}]://{path}
# [subtype] is optional
_URI_RE = re.compile(r"^@(?P<type>\w+)(?:\[(?P<subtype>[^\]]+)\])?://(?P<path>.+)$")

# Liberal matcher for extracting URIs from text (no capture groups → full match)
_URI_EXTRACT_RE = re.compile(r"@(?:\w+)(?:\[[^\[\]\s]+\])?://[^\s)\]>\]\\'\"]+")


@dataclass(frozen=True)
class ParsedURI:
    """
    Parsed URI components (v2.0).

    Attributes:
        type: The URI type (e.g., ``context``, ``storage``, ``memory``).
        subtype: Resource identifier inside ``[...]`` or ``None`` when simplified.
        path: The path part after ``://`` (non-empty).
        is_simplified: True when ``subtype`` is ``None``.

    Example:
        >>> from poping.uri_parser import URIParser
        >>> parsed = URIParser.parse("@context://images/gen_001.png")
        >>> parsed.type
        'context'
        >>> parsed.subtype is None
        True
        >>> parsed.path
        'images/gen_001.png'
        >>> parsed.is_simplified
        True
    """

    type: str
    subtype: Optional[str]
    path: str
    is_simplified: bool


class URIParser:
    """
    Utilities for parsing, expanding, and extracting URIs (v2.0).

    Example:
        Parsing:
            >>> URIParser.parse("@context[alice/sess_001]://images/gen_001.png")
            ParsedURI(type='context', subtype='alice/sess_001', path='images/gen_001.png', is_simplified=False)

        Expansion:
            >>> URIParser.expand("@storage://resume.pdf", client_id="alice", session_id=None)
            '@storage[alice]://resume.pdf'

            >>> URIParser.expand("@context://images/gen.png", client_id="alice", session_id="sess_001")
            '@context[alice/sess_001]://images/gen.png'

        Extraction:
            >>> text = "See @storage://doc.txt and also @context[alice/s1]://img.png"
            >>> URIParser.extract_uris_from_text(text)
            ['@storage://doc.txt', '@context[alice/s1]://img.png']
    """

    _EXPANDABLE_TYPES = {"context", "storage", "memory"}

    @classmethod
    def parse(cls, uri: str) -> ParsedURI:
        """
        Parse a URI string into components.

        Args:
            uri: A string like ``@context://images/gen.png`` or ``@storage[alice]://resume.pdf``.

        Returns:
            ParsedURI: Components of the parsed URI.

        Raises:
            ValueError: If the URI does not match the expected format.

        Example:
            >>> URIParser.parse("@memory[alice]://profile_001.json")
            ParsedURI(type='memory', subtype='alice', path='profile_001.json', is_simplified=False)
        """
        if not isinstance(uri, str) or not uri.startswith("@"):
            raise ValueError(f"Invalid URI: {uri!r}")

        m = _URI_RE.match(uri)
        if not m:
            raise ValueError(f"Invalid URI format: {uri!r}")

        uri_type = m.group("type")
        subtype = m.group("subtype")
        path = m.group("path")

        if not path:
            # Defensive: regex enforces non-empty, but keep explicit guard
            raise ValueError(f"Invalid URI path: {uri!r}")

        return ParsedURI(
            type=uri_type,
            subtype=subtype,
            path=path,
            is_simplified=(subtype is None),
        )

    @classmethod
    def expand(cls, uri: str, client_id: Optional[str], session_id: Optional[str]) -> str:
        """
        Expand a simplified URI using the provided context.

        - If the URI already contains a ``[subtype]``, it is returned unchanged.
        - ``@context`` requires ``client_id`` and ``session_id`` → ``@context[{client_id}/{session_id}]://``
        - ``@storage`` requires ``client_id`` → ``@storage[{client_id}]://``
        - ``@memory``  requires ``client_id`` → ``@memory[{client_id}]://``

        Args:
            uri: The input URI.
            client_id: User identifier for expansion.
            session_id: Session identifier for expansion (``@context`` only).

        Returns:
            str: Expanded URI string.

        Raises:
            ValueError: If the URI is invalid, has unknown type for expansion, or
                required context is missing.

        Examples:
            >>> URIParser.expand("@storage://resume.pdf", client_id="alice", session_id=None)
            '@storage[alice]://resume.pdf'

            >>> URIParser.expand("@context://images/gen.png", client_id="alice", session_id="sess_001")
            '@context[alice/sess_001]://images/gen.png'

            >>> URIParser.expand("@storage[shared]://logo.png", client_id="alice", session_id=None)
            '@storage[shared]://logo.png'
        """
        parsed = cls.parse(uri)
        if not parsed.is_simplified:
            # Already complete (includes special cases like [shared], [agent], etc.)
            return uri

        uri_type = parsed.type
        path = parsed.path

        if uri_type not in cls._EXPANDABLE_TYPES:
            # Non-expandable types (@resource, @dataset, @knowledge) must be complete
            raise ValueError(f"URI type @{uri_type} requires subtype (e.g., @{uri_type}[...]://)")

        if uri_type == "context":
            if not client_id or not session_id:
                raise ValueError("Missing client_id or session_id for @context expansion")
            subtype = f"{client_id}/{session_id}"
        elif uri_type in ("storage", "memory"):
            if not client_id:
                raise ValueError(f"Missing client_id for @{uri_type} expansion")
            subtype = client_id
        else:
            # Defensive: should be unreachable due to earlier type check
            raise ValueError(f"Unsupported type for expansion: {uri_type!r}")

        return f"@{uri_type}[{subtype}]://{path}"

    @classmethod
    def extract_uris_from_text(cls, text: str) -> list[str]:
        """
        Extract all URIs from a block of text.

        Uses a liberal regex that tries to stop at whitespace or common
        closing punctuation, and avoids raising on extraction issues.

        Args:
            text: Arbitrary input text.

        Returns:
            list[str]: A list of matched URI strings in order of appearance.

        Example:
            >>> text = "Please open @storage://doc.txt (see also @context[alice/s1]://img.png)"
            >>> URIParser.extract_uris_from_text(text)
            ['@storage://doc.txt', '@context[alice/s1]://img.png']
        """
        try:
            matches = _URI_EXTRACT_RE.findall(text or "")
        except Exception as exc:  # Extremely defensive; regex shouldn't raise here
            logger.warning("URI extraction failed: %s", exc)
            return []

        # Minor cleanup for potential trailing punctuation that may slip through
        # in edge cases; keep simple and non-destructive.
        cleaned: list[str] = []
        for m in matches:
            cleaned.append(m.rstrip(".,;:!?"))
        return cleaned


__all__ = ["ParsedURI", "URIParser"]
