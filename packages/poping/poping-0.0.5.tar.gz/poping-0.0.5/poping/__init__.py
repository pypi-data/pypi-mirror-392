"""
Poping SDK v2 - AI Agent Framework

OpenAI-style API for building AI agents with:
- Context (message management + AI operations)
- Memory (session + profile)
- Knowledge (RAG over documents)
- Data (structured JSON records)
- Tools (local + cloud)
- MCP integration

Quick Start (Simple Module-Level API):
    import poping

    # Configure once
    poping.set(api_key="your_api_key")

    # Create agent directly
    agent = poping.agent(llm="claude-3-5-sonnet-20241022").build(name="assistant")

    # Chat
    with agent.session(client_id="user_123") as conv:
        response = conv.chat("Hello!")

Alternative (Class-Based API for advanced use):
    from poping import Poping

    # Create client instance
    client = Poping(api_key="your_api_key")
    agent = client.agent(llm="...").build(name="...")
"""

import os
from typing import Optional, List, Dict, Any

from .client import Poping as _PopingClient, PopingClient
from .tool import tool
from .storage import Storage
from .context import Context

# from .knowledge import Knowledge  # TODO: Update to new API
from . import sessions
from .exceptions import (
    PopingError,
    AuthenticationError,
    ToolExecutionError,
    RateLimitError,
    ValidationError,
    ResourceNotFoundError,
)
from .executors import FrontendExecutor
from .frontend import FrontendBridge as _FrontendBridge, FrontendToolFactory as _FrontendToolFactory, start_frontend_bridge as _start_frontend_bridge

__version__ = "0.0.5"

# ============================================================================
# Module-Level Configuration (OpenAI-style)
# ============================================================================

# Global client instance
_global_client: Optional[_PopingClient] = None
_global_api_key: Optional[str] = None
_global_base_url: Optional[str] = None
_global_project: Optional[str] = None


def get_client() -> Optional[_PopingClient]:
    """
    Get the globally configured Poping client instance

    This allows standalone Context/Memory/Knowledge instances to auto-detect
    the backend client without explicit injection.

    Returns:
        Global client if configured via set(), else None

    Example:
        import poping
        poping.set(api_key="your_key")

        # Context can now auto-detect the client
        from poping import Context
        ctx = Context()  # Automatically uses global client
    """
    return _global_client


def get_default_project() -> Optional[str]:
    """
    Get the globally configured default project

    Returns:
        Global project name/ID if configured via set(), else None

    Example:
        import poping
        poping.set(api_key="your_key", project="My Project")

        project = poping.get_default_project()  # "My Project"
    """
    return _global_project


def set(api_key: str = None, base_url: str = None, project: str = None):
    """
    Configure Poping SDK globally (module-level API)

    This allows you to configure once and use `poping.agent()` directly
    without creating a client instance.

    Args:
        api_key: API key for authentication (or set POPING_API_KEY env var)
        base_url: Backend URL (default: http://localhost:8000 or POPING_BASE_URL env var)
        project: Default project name or ID to use for all sessions (optional)

    Example:
        import poping

        # Configure once
        poping.set(
            api_key="your_api_key",
            project="My Project"  # Optional: default project for all sessions
        )

        # Use directly
        agent = poping.agent(llm="claude-3-5-sonnet-20241022").build(name="assistant")

        # Sessions will use the configured project by default
        with agent.session(client_id="user_123") as conv:
            response = conv.chat("Hello!")
    """
    global _global_client, _global_api_key, _global_base_url, _global_project

    _global_api_key = api_key
    _global_base_url = base_url
    _global_project = project

    # Create/update global client
    _global_client = _PopingClient(api_key=api_key, base_url=base_url)


def agent(agent_id_or_llm: str = None, name: str = None, llm: str = None, description: str = None):
    """
    Create new agent or load existing agent (module-level API)

    This function uses the globally configured client (via `poping.set()`).
    If not configured, it will auto-initialize from environment variables.

    Usage:
        1. Create new agent:
           poping.agent(llm="claude-3-5-sonnet-20241022")
           poping.agent("claude-3-5-sonnet-20241022")  # shorthand

        2. Load by ID:
           poping.agent("agt_abc123")

        3. Load by name:
           poping.agent(name="my_assistant")

    Args:
        agent_id_or_llm: Agent ID (if starts with "agt_"), or LLM model name
        name: Agent name (for loading by name)
        llm: LLM model (for creating new agent)
        description: Agent description (for creating new agent)

    Returns:
        AgentBuilder (if creating) or Agent (if loading)

    Example:
        import poping

        poping.set(api_key="your_key")

        # Create new agent
        agent = poping.agent(llm="claude-3-5-sonnet-20241022").build(name="assistant")

        # Load existing agent
        agent = poping.agent("agt_abc123")
    """
    global _global_client

    # Auto-initialize if not configured
    if _global_client is None:
        api_key = _global_api_key or os.environ.get("POPING_API_KEY")
        base_url = _global_base_url or os.environ.get("POPING_BASE_URL", "http://localhost:8000")

        if not api_key:
            raise ValueError(
                "Poping SDK not configured. Either:\n"
                "1. Call poping.set(api_key='...') first, or\n"
                "2. Set POPING_API_KEY environment variable"
            )

        _global_client = _PopingClient(api_key=api_key, base_url=base_url)

    # Delegate to client instance
    return _global_client.agent(
        agent_id_or_llm=agent_id_or_llm, name=name, llm=llm, description=description
    )


def list_agents() -> List[Dict[str, Any]]:
    """
    List all agents for current user (module-level API)

    Returns:
        List of agent summaries with metadata

    Example:
        import poping

        poping.set(api_key="your_key")
        agents = poping.list_agents()

        for agent in agents:
            print(f"{agent['name']}: {agent['agent_id']}")
    """
    global _global_client

    if _global_client is None:
        raise ValueError("Poping SDK not configured. Call poping.set(api_key='...') first.")

    return _global_client.list_agents()


# Export class-based API as "Poping" for backward compatibility
Poping = _PopingClient

__all__ = [
    # Module-level API (recommended)
    "set",
    "get_client",
    "get_default_project",
    "agent",
    "list_agents",
    "tool",
    # Class-based API (advanced/backward compat)
    "Poping",
    "PopingClient",
    "Context",
    "Storage",
    # Submodules
    "sessions",
    # Exceptions
    "PopingError",
    "AuthenticationError",
    "ToolExecutionError",
    "RateLimitError",
    "ValidationError",
    "ResourceNotFoundError",
    # Executors
    "FrontendExecutor",
    # Frontend execution helpers (agent loop on backend, tools on frontend)
    "FrontendBridge",
    "FrontendToolFactory",
    "start_frontend_bridge",
]

# Back-compat friendly names
FrontendBridge = _FrontendBridge
FrontendToolFactory = _FrontendToolFactory
start_frontend_bridge = _start_frontend_bridge
