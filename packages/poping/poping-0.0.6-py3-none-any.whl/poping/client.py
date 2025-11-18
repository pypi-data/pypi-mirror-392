"""
Poping API Client - Handles communication with backend

Main Classes:
- Poping: Main SDK client (OpenAI-style API)
- _HTTPClient: Internal HTTP client for backend communication
"""

from typing import Dict, Any, List, Optional
import os
import requests
from .exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError,
    ResourceNotFoundError
)


class _HTTPClient:
    """
    Client for Poping backend API

    Handles:
    - Authentication
    - HTTP requests to backend
    - Error handling
    - Rate limiting
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 310
    ):
        """
        Initialize Poping client

        Args:
            api_key: API key for authentication
            base_url: Backend API base URL
            timeout: Request timeout in seconds (default: 310s)
                - Backend timeout is 300s, client adds 10s buffer
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        # Do not set a global Content-Type. requests will set
        # application/json when using json=..., and multipart/form-data
        # when using files=.... Setting it globally breaks file uploads.
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        files: Dict[str, Any] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request to backend

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/v1/tools/list")
            data: Request body data
            params: URL query parameters
            files: Files for multipart/form-data uploads
            stream: If True, return streaming response object

        Returns:
            Response JSON data

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            APIError: Other API errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if not files else None,  # Don't use json with files
                data=data if files else None,      # Use data with files
                params=params,
                files=files,
                stream=stream,
                timeout=self.timeout
            )

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(retry_after=int(retry_after) if retry_after else None)
            elif response.status_code == 404:
                try:
                    error_data = response.json()
                except ValueError:
                    # Non‑JSON 404 response
                    raise ResourceNotFoundError("Resource not found")

                message = (
                    error_data.get("message")
                    or error_data.get("detail")
                    or "Resource not found"
                )
                raise ResourceNotFoundError(message)
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                except ValueError:
                    raise APIError(
                        status_code=response.status_code,
                        message=f"HTTP {response.status_code} error",
                        details={},
                    )

                message = (
                    error_data.get("message")
                    or error_data.get("detail")
                    or f"HTTP {response.status_code} error"
                )
                raise APIError(
                    status_code=response.status_code,
                    message=message,
                    details=error_data.get("details", {}),
                )

            # Return response object if streaming, otherwise JSON
            if stream:
                return response
            else:
                return response.json()

        except requests.RequestException as e:
            raise APIError(status_code=0, message=f"Network error: {str(e)}")

    # Tool endpoints
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available cloud tools"""
        return self._request("GET", "/api/v1/tools/list")

    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Execute a cloud tool

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        return self._request("POST", "/api/v1/tools/execute", data={
            "tool_name": tool_name,
            "arguments": arguments
        })

    # LLM endpoints
    def llm_call(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct LLM calls via /api/v1/llm/create are no longer supported.

        The backend has moved to the unified agent chat API
        (/api/v1/agents/{agent_id}/chat). To migrate, create an agent
        with the desired model and call agent.session(...).chat(...)
        instead of using llm_call().
        """
        raise APIError(
            status_code=0,
            message=(
                "llm_call() is deprecated: the /api/v1/llm/create endpoint "
                "has been removed. Use agents and agent.session(...).chat(...) instead."
            ),
            details={},
        )

    # Memory endpoints
    def add_memory(
        self,
        client_id: str,
        memory_id: str,
        content: str,
        tags: List[str] = None,
        importance: float = 0.5
    ) -> str:
        """Add memory item"""
        return self._request("POST", f"/api/v1/memory/{memory_id}/items", data={
            "client_id": client_id,
            "content": content,
            "tags": tags or [],
            "importance": importance
        })

    def search_memory(
        self,
        client_id: str,
        memory_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memory items"""
        return self._request("GET", f"/api/v1/memory/{memory_id}/search", params={
            "client_id": client_id,
            "query": query,
            "top_k": top_k
        })

    # Knowledge endpoints
    def upload_document(
        self,
        client_id: str,
        kb_id: str,
        file_path: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Upload document to knowledge base"""
        # TODO: Implement file upload
        return self._request("POST", f"/api/v1/knowledge/{kb_id}/documents", data={
            "client_id": client_id,
            "file_path": file_path,
            "metadata": metadata or {}
        })

    def search_knowledge(
        self,
        client_id: str,
        kb_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        return self._request("GET", f"/api/v1/knowledge/{kb_id}/search", params={
            "client_id": client_id,
            "query": query,
            "top_k": top_k
        })

    def query_knowledge(
        self,
        client_id: str,
        kb_id: str,
        question: str,
        style: str = "detailed"
    ) -> Dict[str, Any]:
        """Query knowledge base with RAG"""
        return self._request("POST", f"/api/v1/knowledge/{kb_id}/query", data={
            "client_id": client_id,
            "question": question,
            "style": style
        })

    # Data endpoints
    def insert_record(
        self,
        client_id: str,
        dataset_id: str,
        data: Dict[str, Any]
    ) -> str:
        """Insert record into dataset"""
        return self._request("POST", f"/api/v1/data/{dataset_id}/records", data={
            "client_id": client_id,
            "data": data
        })

    def query_data(
        self,
        client_id: str,
        dataset_id: str,
        query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Query dataset with MongoDB-style filter"""
        return self._request("POST", f"/api/v1/data/{dataset_id}/query", data={
            "client_id": client_id,
            "query": query,
            "limit": limit
        })

    def search_data(
        self,
        client_id: str,
        dataset_id: str,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Semantic search in dataset"""
        return self._request("GET", f"/api/v1/data/{dataset_id}/search", params={
            "client_id": client_id,
            "query": query,
            "top_k": top_k
        })


# Backward compatibility alias
PopingClient = _HTTPClient


class Poping:
    """
    Main Poping SDK client (OpenAI-style API)

    This is the primary entry point for the SDK. Initialize once with your
    API key, then use it to create or load agents.

    Example:
        from poping import Poping

        # Initialize client
        poping = Poping(api_key="your_api_key")

        # Create new agent
        agent = poping.agent(llm="claude-3-5-sonnet-20241022").build(name="my_assistant")

        # Load existing agent
        agent = poping.agent("agt_abc123")  # By ID
        agent = poping.agent(name="my_assistant")  # By name

        # Chat
        with agent.session(client_id="user_123") as conv:
            response = conv.chat("Hello!")
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None
    ):
        """
        Initialize Poping client

        Args:
            api_key: API key for authentication (or set POPING_API_KEY env var)
            base_url: Backend URL (default: http://localhost:8000 or POPING_BASE_URL env var)

        Raises:
            ValueError: If API key not provided and not in environment
        """
        self.api_key = api_key or os.environ.get("POPING_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide api_key parameter or set POPING_API_KEY environment variable."
            )

        self.base_url = base_url or os.environ.get("POPING_BASE_URL", "http://localhost:8000")

        # Internal HTTP client
        self._http = _HTTPClient(api_key=self.api_key, base_url=self.base_url)

    def agent(
        self,
        agent_id_or_llm: str = None,
        name: str = None,
        llm: str = None,
        description: str = None
    ):
        """
        Create new agent or load existing agent

        This method is overloaded to support multiple use cases:

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

        Examples:
            # Create new agent
            builder = poping.agent(llm="claude-3-5-sonnet-20241022")
            agent = builder.with_memory(...).build(name="assistant")

            # Shorthand for create
            builder = poping.agent("claude-3-5-sonnet-20241022")

            # Load by ID
            agent = poping.agent("agt_abc123")

            # Load by name
            agent = poping.agent(name="my_assistant")
        """
        from ._agent import AgentBuilder, Agent, AgentConfig

        # Case 1: Load by ID (starts with "agt_")
        if agent_id_or_llm and agent_id_or_llm.startswith("agt_"):
            return self._load_agent_by_id(agent_id_or_llm)

        # Case 2: Load by name (name parameter provided, no llm)
        if name and not llm and not agent_id_or_llm:
            return self._load_agent_by_name(name)

        # Case 3: Create new agent
        if llm or agent_id_or_llm:
            llm_model = llm or agent_id_or_llm
            return AgentBuilder(
                client=self,
                llm=llm_model,
                name=name,
                description=description
            )

        raise ValueError(
            "Invalid arguments. Use:\n"
            "  poping.agent(llm='model_name') - Create new agent\n"
            "  poping.agent('agt_123') - Load by ID\n"
            "  poping.agent(name='my_assistant') - Load by name"
        )

    def _transform_backend_to_sdk_config(self, backend_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform backend AgentConfig format to SDK AgentConfig format

        Backend now uses grouped configuration objects (context/memory/knowledge/dataset/llm_params).
        Older configs used flat flags; this helper supports both shapes.
        """
        # Core LLM settings
        llm = backend_config.get("llm")

        # LLM params (grouped, new shape)
        llm_params = backend_config.get("llm_params") or {}
        max_tokens = llm_params.get("max_tokens", backend_config.get("max_tokens", 4096))
        temperature = llm_params.get("temperature", backend_config.get("temperature", 0.7))
        system_prompt = llm_params.get("system_prompt", backend_config.get("system_prompt"))

        # Context (grouped or legacy flag)
        context_cfg = backend_config.get("context")
        if isinstance(context_cfg, dict):
            enable_context = bool(context_cfg.get("enabled", False))
            context_config: Dict[str, Any] = {
                k: v for k, v in context_cfg.items() if k != "enabled"
            }
        else:
            enable_context = backend_config.get("enable_context", False)
            context_config = {}

        # Memory (grouped MemoryConfig or legacy flags)
        memory_cfg = backend_config.get("memory")
        if isinstance(memory_cfg, dict):
            mode = memory_cfg.get("mode")
            profile_id = memory_cfg.get("profile_id")

            memory_session = {"strategy": "summary"} if mode in ("session", "both") else None
            memory_profiles: List[Dict[str, Any]] = []
            if mode in ("profile", "both") and profile_id:
                memory_profiles.append({"id": profile_id})

            memory_toolset = memory_cfg.get("toolset", True)
            memory_subagent = memory_cfg.get("subagent", False)
            memory_mcp = memory_cfg.get("mcp", False)
        else:
            memory_session = (
                {"strategy": "summary"} if backend_config.get("enable_session_memory") else None
            )
            memory_profiles = (
                [{"id": backend_config.get("memory_id")}]
                if backend_config.get("enable_profile_memory") and backend_config.get("memory_id")
                else []
            )
            mem_strat = backend_config.get("memory_strategies", {}) or {}
            memory_toolset = mem_strat.get("toolset", False)
            memory_subagent = mem_strat.get("subagent", False)
            memory_mcp = mem_strat.get("mcp", False)

        # Knowledge (grouped KnowledgeConfig or legacy fields)
        knowledge_cfg = backend_config.get("knowledge")
        if isinstance(knowledge_cfg, dict):
            knowledge_bases = knowledge_cfg.get("knowledge_ids", []) or []
            knowledge_toolset = knowledge_cfg.get("toolset", True)
            knowledge_subagent = knowledge_cfg.get("subagent", False)
            knowledge_mcp = knowledge_cfg.get("mcp", False)
        else:
            knowledge_bases = backend_config.get("knowledge_bases", []) or []
            know_strat = backend_config.get("knowledge_strategies", {}) or {}
            knowledge_toolset = know_strat.get("toolset", False)
            knowledge_subagent = know_strat.get("subagent", False)
            knowledge_mcp = know_strat.get("mcp", False)

        # Dataset (grouped DatasetConfig or legacy fields)
        dataset_cfg = backend_config.get("dataset")
        if isinstance(dataset_cfg, dict):
            datasets = dataset_cfg.get("dataset_ids", []) or []
            data_toolset = dataset_cfg.get("toolset", True)
            data_subagent = dataset_cfg.get("subagent", False)
            data_mcp = dataset_cfg.get("mcp", False)
        else:
            datasets = backend_config.get("datasets", []) or []
            data_strat = backend_config.get("data_strategies", {}) or {}
            data_toolset = data_strat.get("toolset", False)
            data_subagent = data_strat.get("subagent", False)
            data_mcp = data_strat.get("mcp", False)

        sdk_config = {
            # Core
            "llm": llm,
            "enable_context": enable_context,
            "context_config": context_config,

            # Memory - map from backend's structure to SDK's
            "memory_session": memory_session,
            "memory_profiles": memory_profiles,
            "memory_toolset": memory_toolset,
            "memory_subagent": memory_subagent,
            "memory_mcp": memory_mcp,
            "memory_config": {},

            # Knowledge
            "knowledge_bases": knowledge_bases,
            "knowledge_toolset": knowledge_toolset,
            "knowledge_subagent": knowledge_subagent,
            "knowledge_mcp": knowledge_mcp,
            "knowledge_config": {},

            # Data
            "datasets": datasets,
            "data_toolset": data_toolset,
            "data_subagent": data_subagent,
            "data_mcp": data_mcp,
            "data_config": {},

            # Tools - backend calls it 'tools', SDK calls it 'local_tools'
            "local_tools": [],  # Tools can't be serialized from backend
            "cloud_tools": [],
            "tool_config": {},

            # MCP
            "mcp_servers": backend_config.get("mcp_servers", []),

            # LLM config
            "system_prompt": system_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        return sdk_config

    def _load_agent_by_id(self, agent_id: str):
        """Load agent from backend by ID"""
        from ._agent import Agent, AgentConfig

        # Call GET /api/v1/agents/{agent_id}
        try:
            response = self._http._request("GET", f"/api/v1/agents/{agent_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"Agent not found with ID: {agent_id}")

        # Parse response
        agent_data = response
        sdk_config = self._transform_backend_to_sdk_config(agent_data["config"])
        config = AgentConfig(**sdk_config)

        return Agent(
            agent_id=agent_data["agent_id"],
            name=agent_data["name"],
            description=agent_data.get("description", ""),
            config=config,
            client=self,
            persisted=True
        )

    def _load_agent_by_name(self, name: str):
        """Load agent from backend by name"""
        from ._agent import Agent, AgentConfig

        # Call GET /api/v1/agents (list all)
        try:
            response = self._http._request("GET", "/api/v1/agents")
        except Exception as e:
            raise APIError(status_code=0, message=f"Failed to list agents: {str(e)}")

        # Search for matching name
        # Backend returns a list directly (not wrapped in "agents" key)
        agents = response if isinstance(response, list) else response.get("agents", [])

        for agent_summary in agents:
            if agent_summary["name"] == name:
                # List endpoint only returns summary - fetch full agent with config
                agent_id = agent_summary["agent_id"]
                return self._load_agent_by_id(agent_id)

        raise ResourceNotFoundError(f"Agent not found with name: {name}")

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents for current user

        Returns:
            List of agent summaries with metadata

        Example:
            agents = poping.list_agents()
            for agent in agents:
                print(f"{agent['name']}: {agent['agent_id']}")
        """
        response = self._http._request("GET", "/api/v1/agents")
        # Backend returns a bare list; fall back to wrapped format if needed
        return response if isinstance(response, list) else response.get("agents", [])
