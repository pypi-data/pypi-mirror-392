"""
Poping Sessions - Session management

Access existing sessions and their contexts.
"""

from typing import Optional, List


class SessionProxy:
    """
    Proxy for accessing existing session

    Provides access to session context without full session instance.

    Usage:
        from poping import sessions
        ctx = sessions.get("session_123").context
    """

    def __init__(self, session_id: str, client_id: str = None, client=None):
        """
        Initialize session proxy

        Args:
            session_id: Session identifier
            client_id: User identifier (optional)
            client: API client for backend communication
        """
        self.session_id = session_id
        self.client_id = client_id
        self.client = client
        self._context = None

    @property
    def context(self):
        """
        Access session context

        Returns:
            Context instance for this session

        Example:
            from poping import sessions
            ctx = sessions.get("session_123").context
            msg = ctx.get(key)

        TODO: Implement backend loading
        """
        if self._context is None:
            from .context import Context
            self._context = Context(
                session_id=self.session_id,
                client_id=self.client_id,
                client=self.client
            )
        return self._context


def get(session_id: str, client_id: str = None, api_key: str = None, base_url: str = None) -> SessionProxy:
    """
    Get existing session

    Args:
        session_id: Session identifier
        client_id: User identifier (optional)
        api_key: API key (optional, from env if not provided)
        base_url: Backend URL (optional, from env if not provided)

    Returns:
        SessionProxy for accessing session context

    Example:
        from poping import sessions

        # Get session context
        ctx = sessions.get("session_123").context

        # CRUD operations
        key = ctx.add("user", "Hello")
        msg = ctx.get(key)

        # AI operations (TODO)
        result = await ctx.query("What did we discuss?")

    TODO: Implement backend API call to load session
    """
    import os
    from .client import PopingClient

    # Initialize client if credentials provided
    client = None
    if api_key or os.environ.get("POPING_API_KEY"):
        api_key = api_key or os.environ.get("POPING_API_KEY")
        base_url = base_url or os.environ.get("POPING_BASE_URL", "http://localhost:8000")
        client = PopingClient(api_key=api_key, base_url=base_url)

    return SessionProxy(
        session_id=session_id,
        client_id=client_id,
        client=client
    )


def list(client_id: Optional[str] = None, api_key: str = None, base_url: str = None) -> List[str]:
    """
    List all sessions

    Args:
        client_id: Filter by user (optional)
        api_key: API key (optional)
        base_url: Backend URL (optional)

    Returns:
        List of session IDs

    Example:
        from poping import sessions

        # List all sessions
        all_sessions = sessions.list()

        # List user's sessions
        user_sessions = sessions.list(client_id="user_123")

    TODO: Implement backend API call
    """
    raise NotImplementedError("sessions.list() will be implemented in next phase")


__all__ = [
    'SessionProxy',
    'get',
    'list',
]
