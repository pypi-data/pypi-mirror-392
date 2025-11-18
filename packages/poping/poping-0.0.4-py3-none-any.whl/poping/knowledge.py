"""
[File Overview]
===============
- Purpose: Layer 3 Knowledge OOP API - Standalone knowledge base interface
- Data Flow: User → Knowledge methods → Backend API → Return results
- Core Data Structures: Knowledge class
- Main Functions: create, upload, query, search, update, delete_document, list_documents
- Related Files:
    @/poping_sdk/poping/client.py → HTTP client
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import _HTTPClient


class Knowledge:
    """
    [Class: Knowledge]
    ==================
    Knowledge Base interface for standalone usage

    Provides object-oriented API for KB operations wrapping backend APIs.
    """

    def __init__(self, kb_id: str, client_id: str, api_client: Optional['_HTTPClient'] = None):
        """
        Initialize Knowledge instance

        Args:
            kb_id: Knowledge base ID
            client_id: User ID
            api_client: Optional API client (defaults to default client)
        """
        self.kb_id = kb_id
        self.client_id = client_id
        self.client = api_client or APIClient()

    @classmethod
    def create(
        cls,
        name: str,
        client_id: str,
        description: str = "",
        api_client: Optional[APIClient] = None
    ) -> 'Knowledge':
        """
        Create new knowledge base

        Args:
            name: KB name
            client_id: User ID
            description: KB description
            api_client: Optional API client

        Returns:
            Knowledge instance
        """
        client = api_client or APIClient()

        # Call backend API to create KB
        response = client.post("/knowledge/create", {
            "client_id": client_id,
            "name": name,
            "description": description
        })

        kb_id = response["kb_id"]
        return cls(kb_id=kb_id, client_id=client_id, api_client=client)

    def upload(
        self,
        file_path: str,
        name: str,
        tags: Optional[List[str]] = None,
        auto_process: bool = True
    ) -> Dict[str, Any]:
        """
        Upload document to knowledge base

        Args:
            file_path: Path to file
            name: Document name
            tags: Optional tags
            auto_process: Auto-process after upload (default True)

        Returns:
            Dict with document details
        """
        # Call backend upload API
        response = self.client.post(f"/knowledge/{self.kb_id}/upload", {
            "file_path": file_path,
            "name": name,
            "tags": tags or [],
            "auto_process": auto_process
        })

        return response

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Query knowledge base with semantic search

        Args:
            query_text: Query text
            top_k: Max results (default 5)
            filters: Optional filters

        Returns:
            Dict with search results
        """
        response = self.client.post(f"/knowledge/{self.kb_id}/query", {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {}
        })

        return response

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Alias for query() - semantic search
        """
        return self.query(query_text, top_k, filters)

    def update(
        self,
        document_id: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update document metadata

        Args:
            document_id: Document ID
            name: New name (optional)
            tags: New tags (optional)

        Returns:
            Dict with updated document details
        """
        updates = {}
        if name is not None:
            updates['name'] = name
        if tags is not None:
            updates['tags'] = tags

        response = self.client.put(
            f"/knowledge/{self.kb_id}/documents/{document_id}",
            updates
        )

        return response

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete document from knowledge base

        Args:
            document_id: Document ID

        Returns:
            Dict with deletion status
        """
        response = self.client.delete(
            f"/knowledge/{self.kb_id}/documents/{document_id}"
        )

        return response

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in knowledge base

        Returns:
            List of document dicts
        """
        response = self.client.get(f"/knowledge/{self.kb_id}/documents")

        return response.get("documents", [])


# Module-level function for KB deletion
def delete(kb_id: str, client_id: str, api_client: Optional[APIClient] = None) -> Dict[str, Any]:
    """
    Delete entire knowledge base

    Args:
        kb_id: Knowledge base ID
        client_id: User ID
        api_client: Optional API client

    Returns:
        Dict with deletion status
    """
    client = api_client or APIClient()

    response = client.delete(f"/knowledge/{kb_id}", {"client_id": client_id})

    return response
