"""
[File: Storage]
===============
Purpose: File upload/download operations via backend storage API
Data Flow: local file → upload() → backend OSS → resource_id → get_url() → download()
Core Data Structures:
  - resource_id: string - Unique identifier for stored file
  - file_path: string - Local filesystem path
Related Files:
  @poping/client.py → _HTTPClient for API calls
  @poping/_agent.py → Session.storage property

Usage Examples:
  Auto-detection (recommended, OpenAI-style):
    import poping
    poping.set(api_key="...")
    storage = poping.Storage()  # Auto-detects global client
    rid = storage.upload("/path/to/file.png")

  Backward compatibility (explicit client):
    from poping import Poping
    client = Poping(api_key="...")
    storage = poping.Storage(client=client._http)  # Explicit HTTP client
    rid = storage.upload("/path/to/file.png")
"""

from typing import Optional
from pathlib import Path
from .uri_parser import URIParser


class Storage:
    """
    Storage operations for file upload/download

    Provides interface to backend storage API (OSS/S3).
    Files are uploaded, stored with unique IDs, and can be downloaded.

    Auto-detection behavior:
      If `client` is not provided, this class auto-detects the globally
      configured Poping client set via `poping.set(...)` and uses its
      internal HTTP client.
    """

    def __init__(
        self, client=None, session_id: Optional[str] = None, client_id: Optional[str] = None
    ):
        """
        Initialize storage with optional HTTP client and session scope

        Args:
            client: Optional `_HTTPClient` instance for API calls. If not
                provided, the global client configured via `poping.set(...)`
                is used automatically.
            session_id: Optional session identifier for URI expansion
            client_id: Optional user identifier for URI expansion
                NOTE: In SDK, client_id represents the CLIENT (SDK user).
                Backend uses client_id for this concept. The mapping is:
                SDK client_id → Backend client_id (who owns the project)

        Raises:
            ValueError: If no global client is configured and `client` is not provided

        Example (auto-detection):
            import poping
            poping.set(api_key="...")
            storage = poping.Storage()

        Example (explicit client, backward compatible):
            from poping import Poping
            client = Poping(api_key="...")
            storage = poping.Storage(client=client._http)

        Input: Optional _HTTPClient
        Output: Storage instance
        Role in Flow: Entry point for storage operations
        """
        if client is None:
            # Auto-detect global client (OpenAI-style), matching poping.agent()
            from . import get_client

            global_client = get_client()
            if global_client is None:
                raise ValueError(
                    "Storage not configured. Either:\n"
                    "1. Call poping.set(api_key='...') first, or\n"
                    "2. Pass client explicitly: Storage(client=...)"
                )

            self.client = global_client._http
        else:
            self.client = client

        # Reserved for future scoping of storage by session
        self.session_id = session_id
        self.client_id = client_id  # For URI expansion

    def _expand_uri(self, uri: str) -> str:
        """
        Expand simplified URI if session context available

        Args:
            uri: Input URI (simplified or complete)

        Returns:
            Expanded URI or original if no context/already complete

        Example:
            # With context
            storage = Storage(client=..., client_id="alice", session_id="sess_001")
            storage._expand_uri("@storage://file.pdf")
            # Returns: "@storage[alice]://file.pdf"

            # Without context - returns unchanged
            storage = Storage(client=...)
            storage._expand_uri("@storage://file.pdf")
            # Returns: "@storage://file.pdf"
        """
        if not uri.startswith("@"):
            # Not a URI, return as-is (might be raw resource_id)
            return uri

        if not (self.client_id or self.session_id):
            # No context available, return original
            return uri

        try:
            return URIParser.expand(uri, client_id=self.client_id, session_id=self.session_id)
        except ValueError:
            # Expansion failed (unsupported scheme or missing context)
            # Return original URI
            return uri

    def upload(self, file_path: str) -> str:
        """
        Upload file to backend storage

        Args:
            file_path: Path to local file

        Returns:
            uri: Full storage URI (e.g., "@context://images/abc123.png" for session artifacts,
                 "@storage://abc123.pdf" for persistent user files)

        Raises:
            FileNotFoundError: If file doesn't exist
            APIError: If upload fails

        Example:
            # Session context upload (temporary)
            storage = poping.Storage(client_id="alice", session_id="sess_001")
            uri = storage.upload("/path/to/image.png")
            # Returns: "@context://images/550e8400-e29b-41d4-a716-446655440000.png"

            # Persistent user file upload
            storage = poping.Storage(client_id="alice")
            uri = storage.upload("/path/to/document.pdf")
            # Returns: "@storage://550e8400-e29b-41d4-a716-446655440000.pdf"

            # Use directly in agent messages (no manual concatenation!)
            # conv.chat(f"Analyze this image: {uri}")
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path_obj.name, f, "application/octet-stream")}
            result = self.client._request(
                method="POST", endpoint="/api/v1/storage/upload", files=files
            )
            return result["uri"]  # Changed from resource_id to uri

    def get_url(self, uri: str, expires_in: int = 3600) -> str:
        """
        Get temporary download URL for a resource

        Args:
            uri: Storage URI (e.g., "@storage://file.pdf") or raw resource_id
            expires_in: URL validity in seconds (default: 1 hour)

        Returns:
            url: Temporary download URL

        Example:
            url = storage.get_url("@storage://file.pdf", expires_in=3600)
            # With client_id context, expands to "@storage[alice]://file.pdf"
        """
        # Expand simplified URI if context available
        expanded_uri = self._expand_uri(uri)

        # Do not URL-encode here. FastAPI `:path` captures raw path segments
        # including characters like '@' and '://', and the backend extracts
        # the resource_id from the URI server-side.
        response = self.client._request(
            method="GET",
            endpoint=f"/api/v1/storage/{expanded_uri}/url",
            params={"expires_in": expires_in},
        )

        return response["url"]

    def download(self, uri: str, output_path: str) -> str:
        """
        Download file from storage to local path

        Args:
            uri: Storage URI (e.g., "@storage://file.pdf") or raw resource_id
            output_path: Local path to save file

        Returns:
            output_path: Path where file was saved

        Example:
            storage.download("@storage://file.pdf", "/tmp/downloaded.pdf")
            # With client_id context, expands to "@storage[alice]://file.pdf"
        """
        # Expand simplified URI if context available
        expanded_uri = self._expand_uri(uri)

        # Get download stream from backend via HTTP client
        resp = self.client._request(
            method="GET", endpoint=f"/api/v1/storage/{expanded_uri}/download", stream=True
        )

        # Write to output file
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path
