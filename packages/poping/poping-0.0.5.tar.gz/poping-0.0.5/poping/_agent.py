"""
Poping Agent Builder and Session
"""

from typing import Dict, Any, List, Optional, Iterator, Union
from dataclasses import dataclass, field
from .client import PopingClient
from .tool import ToolRegistry, get_tool_metadata
from .frontend import FrontendToolFactory
from .exceptions import ValidationError
import os
from .uri_parser import URIParser


@dataclass
class SubagentConfig:
    """
    Subagent configuration

    Subagents are specialized agents with their own context window (200K tokens).
    They can access tools but cannot have nested subagents (depth limit = 1).

    Data Flow:
    - Main agent detects complex task → Routes to subagent via tool call
    - Subagent executes in isolated context → Returns result
    - Main agent receives result → Continues conversation
    """

    name: str  # Tool name (e.g., "memory_specialist", "custom_analyst")
    prompt: str  # System prompt for subagent

    # Optional configuration
    tools: List[str] = field(default_factory=list)  # Explicit tool names (no auto-inheritance)
    model: Optional[str] = None  # LLM model (inherits from parent if None)

    # Built-in subagent type (for backward compatibility)
    builtin_type: Optional[str] = None  # "memory" | "knowledge" | "data" | None (custom)

    # Additional LLM parameters
    max_tokens: int = 4096
    temperature: float = 0.7
    description: Optional[str] = None  # Tool description shown to main agent


@dataclass
class AgentConfig:
    """Agent configuration"""

    llm: str
    name: Optional[str] = None
    description: Optional[str] = None

    # Context
    enable_context: bool = False
    context_config: Dict[str, Any] = field(default_factory=dict)

    # Memory
    memory_session: Optional[Dict[str, Any]] = None
    memory_profiles: List[Dict[str, Any]] = field(default_factory=list)
    memory_toolset: Union[bool, Dict[str, Any]] = True
    memory_subagent: Union[bool, Dict[str, Any]] = False
    memory_mcp: Union[bool, Dict[str, Any]] = False
    memory_config: Dict[str, Any] = field(default_factory=dict)

    # Knowledge
    knowledge_bases: List[str] = field(default_factory=list)  # List of KB IDs
    knowledge_toolset: Union[bool, Dict[str, Any]] = True
    knowledge_subagent: Union[bool, Dict[str, Any]] = False
    knowledge_mcp: Union[bool, Dict[str, Any]] = False
    knowledge_config: Dict[str, Any] = field(default_factory=dict)

    # Data
    datasets: List[str] = field(default_factory=list)
    data_toolset: Union[bool, Dict[str, Any]] = True
    data_subagent: Union[bool, Dict[str, Any]] = False
    data_mcp: Union[bool, Dict[str, Any]] = False
    data_config: Dict[str, Any] = field(default_factory=dict)

    # Tools
    local_tools: List = field(default_factory=list)
    cloud_tools: List[str] = field(default_factory=list)
    tool_config: Dict[str, Any] = field(default_factory=dict)

    # MCP
    mcp_servers: List[str] = field(default_factory=list)

    # LLM config
    system_prompt: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7

    # Subagents (NEW - replaces memory_subagent, knowledge_subagent, data_subagent)
    subagents: List[SubagentConfig] = field(default_factory=list)

    def __post_init__(self):
        """
        Convert legacy subagent flags to SubagentConfig entries

        This runs when AgentConfig is created directly (e.g., from dict
        deserialization). For builder pattern, see Agent._convert_legacy_subagents()
        """
        self._convert_legacy_subagents()

    def _convert_legacy_subagents(self):
        """
        Convert legacy subagent flags to SubagentConfig entries

        Called both by __post_init__ and by Agent.__init__() to handle
        both direct instantiation and builder pattern cases.
        """
        # Memory subagent conversion
        if self.memory_subagent and not any(s.builtin_type == "memory" for s in self.subagents):
            if isinstance(self.memory_subagent, dict):
                memory_config = self.memory_subagent
            else:
                memory_config = {}

            subagent = SubagentConfig(
                name=memory_config.get("name", "memory_specialist"),
                prompt=memory_config.get(
                    "system_prompt",
                    "You are a memory organization expert. Help organize, find, and curate memories.",
                ),
                tools=[],
                model=memory_config.get("llm"),
                description=memory_config.get(
                    "description",
                    "Specialized agent for complex memory operations like organizing, "
                    "finding contradictions, and curating memories.",
                ),
                max_tokens=memory_config.get("max_tokens", 4096),
                temperature=memory_config.get("temperature", 0.7),
                builtin_type="memory",
            )

            self.subagents.append(subagent)

        # Knowledge subagent conversion
        if self.knowledge_subagent and not any(
            s.builtin_type == "knowledge" for s in self.subagents
        ):
            if isinstance(self.knowledge_subagent, dict):
                knowledge_config = self.knowledge_subagent
            else:
                knowledge_config = {}

            subagent = SubagentConfig(
                name=knowledge_config.get("name", "knowledge_specialist"),
                prompt=knowledge_config.get(
                    "system_prompt",
                    "You are a knowledge retrieval specialist. "
                    "You can search across all available knowledge bases.",
                ),
                tools=[],
                model=knowledge_config.get("llm"),
                description=knowledge_config.get(
                    "description",
                    "Specialized agent for complex knowledge queries. "
                    "Use for multi-document analysis and synthesis across all available knowledge bases.",
                ),
                max_tokens=knowledge_config.get("max_tokens", 8192),
                temperature=knowledge_config.get("temperature", 0.3),
                builtin_type="knowledge",
            )

            self.subagents.append(subagent)

        # Data subagent conversion
        if self.data_subagent and not any(s.builtin_type == "data" for s in self.subagents):
            if isinstance(self.data_subagent, dict):
                data_config = self.data_subagent
            else:
                data_config = {}

            subagent = SubagentConfig(
                name=data_config.get("name", "data_analyst"),
                prompt=data_config.get(
                    "system_prompt",
                    "You are a data analytics specialist. Analyze datasets and provide insights.",
                ),
                tools=[],
                model=data_config.get("llm"),
                description=data_config.get(
                    "description",
                    "Specialized agent for complex data analysis across all available datasets.",
                ),
                max_tokens=data_config.get("max_tokens", 4096),
                temperature=data_config.get("temperature", 0.7),
                builtin_type="data",
            )

            self.subagents.append(subagent)


class AgentBuilder:
    """
    Fluent builder for agent configuration

    Example:
        from poping import Poping

        poping = Poping(api_key="...")
        agent = (
            poping.agent(llm="claude-3-5-sonnet-20241022")
            .with_context()
            .with_memory(session={"strategy": "summary"}, toolset=True)
            .with_knowledge(["kb_docs"], toolset=True)
            .with_tools(local=[search_web], cloud=["jira.create_ticket"])
            .build(name="my_assistant")
        )
    """

    def __init__(self, client: "Poping", llm: str, name: str = None, description: str = None):
        """
        Initialize agent builder

        Args:
            client: Poping client instance
            llm: Model identifier (e.g., "claude-3-5-sonnet-20241022")
            name: Agent name (optional, can be set in build())
            description: Agent description (optional, can be set in build())
        """
        self.client = client
        self.config = AgentConfig(llm=llm, name=name, description=description)
        self._initial_name = name
        self._initial_description = description
        # Feature flags
        self._enable_storage: bool = False
        # Frontend factories for auto session binding
        self._frontend_factories = []

    def with_context(self, config: Dict[str, Any] = None) -> "AgentBuilder":
        """
        Enable conversation context management

        Args:
            config: Context configuration

        Returns:
            Self for chaining
        """
        self.config.enable_context = True
        if config:
            self.config.context_config = config
        return self

    def with_memory(
        self,
        session: Dict[str, Any] = None,
        profiles: List[Dict[str, Any]] = None,
        toolset: Union[bool, Dict[str, Any]] = True,
        subagent: Union[bool, Dict[str, Any]] = False,
        mcp: Union[bool, Dict[str, Any]] = False,
        config: Dict[str, Any] = None,
    ) -> "AgentBuilder":
        """
        Configure memory (session + profile)

        Args:
            session: Session memory config
                - strategy: "summary" | "vector" | "hybrid"
                - persist_to: Profile ID to merge into
            profiles: List of profile memory configs
                - id: Profile ID
                - write: Whether agent can write to this profile
            toolset: Enable memory toolset strategy. bool or dict for options.
            subagent: Enable memory subagent strategy. bool or dict for config.
            mcp: Enable memory MCP strategy. bool or dict for config.
            config: Additional configuration

        Returns:
            Self for chaining
        """
        self.config.memory_session = session
        if profiles:
            self.config.memory_profiles = profiles
        self.config.memory_toolset = toolset
        self.config.memory_subagent = subagent
        self.config.memory_mcp = mcp
        if config:
            self.config.memory_config = config
        return self

    def with_knowledge(
        self,
        kb_ids: List[str],
        toolset: Union[bool, Dict[str, Any]] = True,
        subagent: Union[bool, Dict[str, Any]] = False,
        mcp: Union[bool, Dict[str, Any]] = False,
        config: Dict[str, Any] = None,
    ) -> "AgentBuilder":
        """
        Attach knowledge bases (supports multiple KBs simultaneously)

        Args:
            kb_ids: List of knowledge base IDs to attach
            toolset: Enable knowledge toolset. bool or dict for options.
            subagent: Enable knowledge subagent. bool or dict for config.
            mcp: Enable knowledge MCP strategy. bool or dict for config.
            config: Additional configuration

        Returns:
            Self for chaining

        Example:
            # Single KB
            agent.with_knowledge(["kb_001"], toolset=True)

            # Multiple KBs
            agent.with_knowledge(["kb_docs", "kb_api_specs"], toolset=True)

            # With subagent
            agent.with_knowledge([
                "kb_001"
            ], toolset=True, subagent={"name": "doc_expert"})
        """
        self.config.knowledge_bases = kb_ids
        self.config.knowledge_toolset = toolset
        self.config.knowledge_subagent = subagent
        self.config.knowledge_mcp = mcp
        if config:
            self.config.knowledge_config = config
        # If knowledge toolset is enabled, register cloud tools
        if toolset:
            # URI-based knowledge tools (returns URIs + metadata, not content)
            # Use storage.read() to fetch actual content from URIs
            knowledge_tool_ids = [
                "knowledge.list_kb",  # List knowledge bases
                "knowledge.list_docs",  # List documents with URIs
                "knowledge.get_doc",  # Get document structure with URIs
                "knowledge.search",  # Search (returns URIs + scores)
            ]
            for tool_id in knowledge_tool_ids:
                if tool_id not in self.config.cloud_tools:
                    self.config.cloud_tools.append(tool_id)
        return self

    def with_storage(self) -> "AgentBuilder":
        """
        Enable storage.read cloud tool for the agent

        Adds a cloud tool that allows the agent to read files from storage
        using URIs. Supports text files (returns content) and images
        (returns base64-encoded data).

        Returns:
            self (AgentBuilder) for method chaining

        Example:
            agent = poping.agent(llm="claude-3-5-sonnet-20241022")\
                .with_storage()\
                .build(name="storage_agent")

            with agent.session() as conv:
                # Upload a file
                uri = conv.storage.upload("chart.png")

                # Agent can now read it using the tool
                conv.chat(f"What's in this chart? {uri}")
                # Agent will call storage.read tool with the URI
        """
        self._enable_storage = True
        # Also add to runtime cloud tools so SDK-managed loop includes it
        if "storage.read" not in self.config.cloud_tools:
            self.config.cloud_tools.append("storage.read")
        return self

    def with_datasets(
        self,
        dataset_ids: List[str],
        toolset: Union[bool, Dict[str, Any]] = True,
        subagent: Union[bool, Dict[str, Any]] = False,
        mcp: Union[bool, Dict[str, Any]] = False,
        config: Dict[str, Any] = None,
    ) -> "AgentBuilder":
        """
        Attach datasets

        Args:
            dataset_ids: List of dataset IDs
            toolset: Enable data toolset. bool or dict for options.
            subagent: Enable data subagent. bool or dict for config.
            mcp: Enable data MCP strategy. bool or dict for config.
            config: Additional configuration

        Returns:
            Self for chaining
        """
        self.config.datasets = dataset_ids
        self.config.data_toolset = toolset
        self.config.data_subagent = subagent
        self.config.data_mcp = mcp
        if config:
            self.config.data_config = config

        # Auto-register unified data cloud tools when toolset is enabled
        if toolset:
            # Unified tools work across ALL datasets (dataset_id is a parameter)
            unified_data_tools = ["data.list_datasets", "data.list_records", "data.get_record"]
            for tool_id in unified_data_tools:
                if tool_id not in self.config.cloud_tools:
                    self.config.cloud_tools.append(tool_id)

        return self

    def with_tools(
        self, local: List = None, cloud: List[str] = None, config: Dict[str, Any] = None
    ) -> "AgentBuilder":
        """
        Attach tools

        SDK distinguishes tool types for execution routing:
        - local: Python functions executed in SDK process (instant)
        - cloud: Backend operations executed via HTTP API (network overhead)
        - subagent: Configured via with_memory/knowledge/data (not here)

        Args:
            local: Local Python functions decorated with @tool
                - Executed in SDK process
                - Direct function calls
                - Examples: search_web, get_weather, custom_parser
            cloud: Cloud tool IDs
                - Executed in Backend via /api/v1/tools/execute
                - Examples: "memory.search", "knowledge.query_kb123", "data.filter_ds456"
            config: Tool configuration
                - timeout: Execution timeout (seconds)
                - concurrency: Max parallel tool executions

        Returns:
            Self for chaining

        Example:
            @tool
            def search_web(query: str) -> str:
                '''Search the web for information'''
                return requests.get(f"https://api.search.com?q={query}").text

            @tool
            def get_weather(city: str) -> dict:
                '''Get current weather for a city'''
                return {"temp": 72, "condition": "sunny"}

            agent = (
                poping.agent(llm="claude-3-5-sonnet-20241022")
                .with_tools(
                    local=[search_web, get_weather],
                    cloud=["memory.search", "knowledge.query_kb_docs"]
                )
                .build(api_key="...")
            )

        Note:
            - Subagent tools are NOT configured here
            - Use with_memory(subagent=True), with_knowledge(subagent=True), etc.
            - Subagents appear as tools but are auto-generated from module configs
        """
        if local:
            self.config.local_tools = local
        if cloud:
            self.config.cloud_tools = cloud
        if config:
            self.config.tool_config = config
        return self

    def with_subagent(
        self,
        name: str,
        prompt: str,
        tools: List[str] = None,
        model: str = None,
        description: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> "AgentBuilder":
        """
        Register a custom subagent

        Subagents are specialized agents with isolated 200K context windows.
        Use for complex, multi-step tasks requiring focus and tool orchestration.

        Design Principles:
        - Explicit tool inheritance: Subagents do NOT auto-inherit parent tools
        - No nesting: Subagents cannot have subagents (depth limit = 1)
        - Clear purpose: Every subagent must have a specific prompt/role

        Args:
            name: Subagent tool name (shown to main agent)
                - Must be unique across all tools
                - Use snake_case (e.g., "code_reviewer", "data_analyst")
            prompt: System prompt defining subagent's role and behavior
                - Be specific about what the subagent should do
                - Example: "You are a code review expert. Analyze code for bugs and style."
            tools: Explicit list of tool names subagent can use (optional)
                - Local tools: Python function names (e.g., ["search_web", "get_weather"])
                - Cloud tools: Backend tool IDs (e.g., ["memory.search", "knowledge.query_kb123"])
                - Default: [] (no tools)
            model: LLM model for subagent (optional)
                - Default: Inherits from parent agent
                - Example: "claude-3-5-sonnet-20241022"
            description: Tool description shown to main agent (optional)
                - Helps main agent decide when to invoke this subagent
                - Default: Auto-generated from name
            max_tokens: Max tokens for subagent responses (default: 4096)
            temperature: Temperature for subagent LLM (default: 0.7)

        Returns:
            Self for chaining

        Raises:
            ValidationError: If name is empty or conflicts with existing tools

        Example:
            # Custom code reviewer subagent
            agent = (
                poping.agent(llm="claude-3-5-sonnet-20241022")
                .with_tools(local=[read_file, write_file])
                .with_subagent(
                    name="code_reviewer",
                    prompt="You are a code review expert. Check for bugs, style issues, and best practices.",
                    tools=["read_file"],  # Explicit - only gets read_file, not write_file
                    description="Specialized code review agent"
                )
                .build(name="dev_assistant")
            )

            # Custom data analyst (no tools)
            agent = (
                poping.agent(llm="claude-3-5-sonnet-20241022")
                .with_knowledge(["kb_reports"], toolset=True)
                .with_subagent(
                    name="report_analyst",
                    prompt="You are a data analyst. Synthesize insights from reports.",
                    tools=[],  # No tools - pure reasoning
                    model="claude-3-opus-20240229",  # Different model
                    max_tokens=8192
                )
                .build(name="analyst")
            )

        Note:
            - Subagents appear as tools to the main agent
            - Main agent decides when to invoke based on description
            - Subagent executes in isolated context, returns result to main agent
            - Cannot nest: Subagents registered via with_subagent() cannot call other subagents
        """
        # Validation
        if not name or not name.strip():
            raise ValidationError("Subagent name cannot be empty")

        if not prompt or not prompt.strip():
            raise ValidationError("Subagent prompt cannot be empty")

        # Check for name conflicts with existing subagents
        existing_names = {s.name for s in self.config.subagents}
        if name in existing_names:
            raise ValidationError(f"Subagent with name '{name}' already registered")

        # Check for conflicts with local tool names
        if self.config.local_tools:
            local_tool_names = set()
            for func in self.config.local_tools:
                meta = get_tool_metadata(func)
                if meta and meta.get("name"):
                    local_tool_names.add(meta["name"])
                else:
                    # Fall back to function __name__ if not decorated
                    local_tool_names.add(getattr(func, "__name__", ""))
            if name in local_tool_names:
                raise ValidationError(
                    f"Subagent name '{name}' conflicts with existing local tool name"
                )

        # Check for conflicts with cloud tool IDs
        if self.config.cloud_tools and name in set(self.config.cloud_tools):
            raise ValidationError(f"Subagent name '{name}' conflicts with existing cloud tool ID")

        # Create SubagentConfig
        subagent_config = SubagentConfig(
            name=name,
            prompt=prompt,
            tools=tools or [],
            model=model,
            description=description,
            max_tokens=max_tokens,
            temperature=temperature,
            builtin_type=None,  # Custom subagent (not memory/knowledge/data)
        )

        # Append to config
        self.config.subagents.append(subagent_config)

        # Return self for chaining
        return self

    def with_tool(
        self, local: List = None, cloud: List[str] = None, config: Dict[str, Any] = None
    ) -> "AgentBuilder":
        """
        DEPRECATED: Use with_tools() instead

        This method is deprecated and will be removed in a future version.
        Use with_tools() (plural) instead.

        Args:
            local: Local functions decorated with @tool
            cloud: Cloud tool IDs
            config: Tool configuration

        Returns:
            Self for chaining
        """
        import warnings

        warnings.warn(
            "with_tool() is deprecated. Use with_tools() instead.", DeprecationWarning, stacklevel=2
        )
        return self.with_tools(local=local, cloud=cloud, config=config)

    def with_mcp(self, servers: List[str]) -> "AgentBuilder":
        """
        Connect to MCP servers

        Args:
            servers: MCP server URLs

        Returns:
            Self for chaining
        """
        self.config.mcp_servers = servers
        return self

    def with_system_prompt(self, prompt: str) -> "AgentBuilder":
        """
        Set system prompt

        Args:
            prompt: System prompt text

        Returns:
            Self for chaining
        """
        self.config.system_prompt = prompt
        return self

    def with_frontend_tools(
        self,
        bridge,
        tools: List[Dict[str, Any]],
    ) -> "AgentBuilder":
        """
        Register frontend-executed tools (schemas on backend, execution in browser).

        Args:
            bridge: FrontendBridge instance (from poping.start_frontend_bridge or constructed manually)
            tools: List of tool definitions:
                [{ 'name': str, 'schema': dict, 'description': Optional[str] }]

        Returns:
            Self for chaining

        Example:
            bridge, _, _ = poping.start_frontend_bridge()
            builder.with_frontend_tools(bridge, [
                { 'name': 'ui.alert', 'schema': {...}, 'description': 'Show alert' },
            ])
        """
        factory = FrontendToolFactory(bridge)
        for t in tools:
            name = t.get("name")
            schema = t.get("schema")
            if not name or not schema:
                raise ValueError("Each frontend tool must have 'name' and 'schema'")
            desc = t.get("description")
            fn = factory.make_tool(name=name, schema=schema, description=desc)
            self.config.local_tools.append(fn)

        # Hold reference for auto session binding later
        self._frontend_factories.append(factory)
        return self

    def with_llm_config(
        self, max_tokens: int = 4096, temperature: float = 0.7, system_prompt: Optional[str] = None
    ) -> "AgentBuilder":
        """
        Configure LLM parameters

        Args:
            max_tokens: Maximum tokens
            temperature: Temperature (0-1)
            system_prompt: System prompt for the agent

        Returns:
            Self for chaining
        """
        self.config.max_tokens = max_tokens
        self.config.temperature = temperature
        if system_prompt is not None:
            self.config.system_prompt = system_prompt
        return self

    def build(self, name: str = None, description: str = None, project: str = None) -> "Agent":
        """
        Build and persist the agent (upsert pattern)

        If an agent with the same name already exists for this user, it will be
        updated with the new configuration. Otherwise, a new agent is created.

        Args:
            name: Agent name (required, used for upsert detection)
            description: Agent description
            project: Project name or ID (optional, uses global default if not provided)

        Returns:
            Agent: The created or updated agent instance

        Raises:
            ValidationError: If name not provided or project not found
            APIError: If backend request fails

        Example:
            # Use global default project (set via poping.set())
            poping.set(project="My Project")
            agent = poping.agent("claude-3-5-sonnet-20241022").build(name="assistant")

            # Override with specific project
            agent = poping.agent("claude-3-5-sonnet-20241022").build(
                name="assistant",
                project="Another Project"
            )

            # Later, reload by ID or name
            agent = poping.agent(agent.agent_id)
            agent = poping.agent(name="assistant")
        """
        # Get final name and description
        final_name = name or self._initial_name
        final_description = description or self._initial_description or ""

        if not final_name:
            raise ValidationError(
                "Agent name is required for persistence. "
                "Provide name parameter to build() or agent() method."
            )

        # Resolve project_id
        project_id = None
        try:
            if project:
                # Use provided project (name or ID)
                if project.startswith("prj_"):
                    project_id = project
                else:
                    # Resolve project name to ID
                    response = self.client._http._request(
                        "GET", "/api/v1/projects/resolve", params={"name": project}
                    )
                    project_id = response["project_id"]
            else:
                # Use global default project
                from . import get_default_project

                global_project = get_default_project()

                if global_project:
                    if global_project.startswith("prj_"):
                        project_id = global_project
                    else:
                        response = self.client._http._request(
                            "GET", "/api/v1/projects/resolve", params={"name": global_project}
                        )
                        project_id = response["project_id"]
                else:
                    # Fetch user's default project
                    response = self.client._http._request("GET", "/api/v1/projects/default")
                    project_id = response["project_id"]
        except Exception as e:
            raise ValidationError(f"Failed to resolve project: {e}")

        if not project_id:
            raise ValidationError(
                "No project specified. Use build(project='...') or poping.set(project='...')"
            )

        # If storage tool is enabled, ensure it's included in runtime cloud tools
        if self._enable_storage and "storage.read" not in self.config.cloud_tools:
            self.config.cloud_tools.append("storage.read")

        # Serialize config to dict
        config_dict = self._serialize_config()

        # Call backend to create and persist agent
        try:
            response = self.client._http._request(
                "POST",
                "/api/v1/agents",
                data={
                    "name": final_name,
                    "description": final_description,
                    "config": config_dict,
                    "project_id": project_id,
                },
            )
        except Exception as e:
            raise ValidationError(f"Failed to create agent on backend: {str(e)}")

        # Extract agent_id from response
        agent_id = response.get("agent_id")
        if not agent_id:
            raise ValidationError("Backend did not return agent_id")

        # Update config with final name/description
        self.config.name = final_name
        self.config.description = final_description

        # Return Agent instance
        return Agent(
            agent_id=agent_id,
            name=final_name,
            description=final_description,
            config=self.config,
            client=self.client,
            persisted=True,
            frontend_factories=self._frontend_factories,
        )

    def _serialize_config(self) -> Dict[str, Any]:
        """
        Serialize AgentConfig to dict for backend API (NEW grouped format)

        Returns:
            Config dict suitable for POST /api/v1/agents with grouped structure
        """
        # NOTE: Local tools are NOT sent to backend
        # They execute in SDK process during chat sessions
        # Backend's "tools" field is for backend-defined callable functions

        config = {
            "llm": self.config.llm,
            "description": self.config.description,
        }

        # Context (grouped)
        if self.config.enable_context:
            config["context"] = {"enabled": True}

        # Memory (grouped)
        has_memory = bool(self.config.memory_session or self.config.memory_profiles)
        if has_memory:
            # Determine mode
            if self.config.memory_session and self.config.memory_profiles:
                mode = "both"
            elif self.config.memory_profiles:
                mode = "profile"
            else:
                mode = "session"

            memory_config = {
                "mode": mode,
                "toolset": self.config.memory_toolset,
                "subagent": self.config.memory_subagent,
                "mcp": self.config.memory_mcp,
            }

            # Add profile_id if using profile memory
            if self.config.memory_profiles:
                memory_config["profile_id"] = self.config.memory_profiles[0].get("id")

            config["memory"] = memory_config

        # Knowledge (grouped)
        if self.config.knowledge_bases:
            config["knowledge"] = {
                "knowledge_ids": self.config.knowledge_bases,  # NEW: use knowledge_ids
                "toolset": self.config.knowledge_toolset,
                "subagent": self.config.knowledge_subagent,
                "mcp": self.config.knowledge_mcp,
            }

        # Dataset (grouped)
        if self.config.datasets:
            config["dataset"] = {
                "dataset_ids": self.config.datasets,
                "toolset": self.config.data_toolset,
                "subagent": self.config.data_subagent,
                "mcp": self.config.data_mcp,
            }

        # Tools - empty list (local tools stay in SDK)
        config["tools"] = []

        # MCP servers
        if self.config.mcp_servers:
            config["mcp_servers"] = self.config.mcp_servers

        # LLM params (grouped)
        config["llm_params"] = {
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        if self.config.system_prompt:
            config["llm_params"]["system_prompt"] = self.config.system_prompt

        return config


class Agent:
    """
    Configured agent instance

    Usage:
        # From builder
        agent = poping.agent(llm="...").build(name="assistant")

        # Load existing
        agent = poping.agent("agt_123")
        agent = poping.agent(name="assistant")

        # Chat
        with agent.session(client_id="user_123") as conv:
            response = conv.chat("Hello!")
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        config: AgentConfig,
        client: "Poping",
        persisted: bool = True,
        frontend_factories: Optional[List[Any]] = None,
    ):
        """
        Initialize agent

        Args:
            agent_id: Agent ID from backend
            name: Agent name
            description: Agent description
            config: Agent configuration
            client: Poping client instance
            persisted: Whether agent is persisted to backend
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.client = client
        self.persisted = persisted
        self._frontend_factories = frontend_factories or []

        # Convert legacy subagent flags BEFORE tool registration
        # Handles builder pattern where flags are set after AgentConfig creation
        config._convert_legacy_subagents()
        self.config = config

        # Initialize tool registry (schemas for local tools only)
        self.tool_registry = ToolRegistry()

        # Register local tools
        for func in config.local_tools:
            self.tool_registry.register_local(func)

        # Register cloud tools
        if config.cloud_tools:
            self.tool_registry.register_cloud(config.cloud_tools)

        # Register subagent tools
        self._register_subagent_tools()

    def session(
        self,
        client_id: str = None,
        session_id: str = None,
        **kwargs,
    ) -> "Session":
        """
        [Method: session]
        =================
        - Input:
            client_id: User identifier (optional, extracted from API key if None)
            session_id: Existing session to resume (optional, creates new if None)
            **kwargs: Additional session options
        - Output: Session object
        - Logic:
            1. Use global default project from poping.set() if configured
            2. Resolve global project (name → ID), or fetch user's default from backend
            3. Create or resume session with project context
            4. Return Session object for interaction

        - Usage:
            # Use global default project (set via poping.set())
            poping.set(project="My Project")
            session = agent.session(client_id="user_123")
        """
        import uuid

        # Fail fast: project cannot be set at session level
        if "project" in kwargs:
            raise ValueError(
                "Project cannot be set at session level. "
                "Use poping.set(project='...') to configure project globally."
            )

        # Import here to avoid circular dependency
        try:
            from . import get_default_project

            global_project = get_default_project()
        except:
            global_project = None

        # Resolve project_id
        project_id = None
        try:
            if global_project:
                # Check if it's already a project_id (starts with prj_)
                if isinstance(global_project, str) and global_project.startswith("prj_"):
                    project_id = global_project
                else:
                    # Resolve project name to ID via API
                    try:
                        response = self.client._http._request(
                            "GET", "/api/v1/projects/resolve", params={"name": global_project}
                        )
                        project_id = response["project_id"]
                    except Exception as e:
                        raise ValueError(f"Failed to resolve project '{global_project}': {e}")
            else:
                # Fetch default project
                try:
                    response = self.client._http._request("GET", "/api/v1/projects/default")
                    project_id = response["project_id"]
                except Exception as e:
                    raise ValueError(f"No default project found. Create a project first: {e}")
        except Exception as e:
            # Re-raise as ValueError with clear context while preserving message
            raise ValueError(str(e))

        session_id = session_id or f"session_{uuid.uuid4().hex[:12]}"

        # Auto-bind session_id to any frontend tool factories
        try:
            for f in getattr(self, "_frontend_factories", []) or []:
                f.set_session(session_id)
        except Exception:
            pass

        return Session(
            agent=self,
            client_id=client_id,
            session_id=session_id,
            client=self.client,
            project_id=project_id,
        )

    def reload(self) -> None:
        """
        Reload agent configuration from backend

        Useful if agent was updated via API or by another process.
        Re-fetches the agent config and re-initializes tools.

        Raises:
            ValueError: If agent not persisted
            ResourceNotFoundError: If agent no longer exists

        Example:
            agent = poping.agent("agt_123")
            # ... agent updated elsewhere ...
            agent.reload()  # Refresh config
        """
        if not self.persisted:
            raise ValueError("Cannot reload non-persisted agent")

        # Load from backend
        response = self.client._http._request("GET", f"/api/v1/agents/{self.agent_id}")

        # Update attributes
        self.name = response["name"]
        self.description = response.get("description", "")
        # Transform backend (grouped) AgentConfig into SDK AgentConfig shape
        sdk_config = self.client._transform_backend_to_sdk_config(response["config"])
        self.config = AgentConfig(**sdk_config)

        # Re-initialize tool registry
        self.tool_registry = ToolRegistry()

        # Re-register tools
        for func in self.config.local_tools:
            self.tool_registry.register_local(func)

        if self.config.cloud_tools:
            self.tool_registry.register_cloud(self.config.cloud_tools)

        self._register_subagent_tools()

    def update(self, name: str = None, description: str = None, config: AgentConfig = None) -> None:
        """
        Update agent on backend

        Args:
            name: New name (optional)
            description: New description (optional)
            config: New configuration (optional)

        Raises:
            ValueError: If agent not persisted

        Example:
            agent.update(description="Updated description")
            agent.update(name="new_name", description="new description")
        """
        if not self.persisted:
            raise ValueError("Cannot update non-persisted agent")

        # Build update dict
        updates = {}
        if name:
            updates["name"] = name
        if description:
            updates["description"] = description
        if config:
            # Serialize new config
            updates["config"] = self._serialize_config_for_update(config)

        if not updates:
            return  # Nothing to update

        # Call backend
        self.client._http._request("PATCH", f"/api/v1/agents/{self.agent_id}", data=updates)

        # Reload to get updated state
        self.reload()

    def delete(self) -> None:
        """
        Delete agent from backend

        After deletion, this agent instance should not be used.

        Raises:
            ValueError: If agent not persisted

        Example:
            agent = poping.agent("agt_123")
            agent.delete()
            # Agent is now deleted from backend
        """
        if not self.persisted:
            raise ValueError("Cannot delete non-persisted agent")

        self.client._http._request("DELETE", f"/api/v1/agents/{self.agent_id}")
        self.persisted = False

    def _serialize_config_for_update(self, config: AgentConfig) -> Dict[str, Any]:
        """
        Serialize config for update request using the NEW grouped backend format.

        Mirrors AgentBuilder._serialize_config() so that create() and update()
        send consistent AgentConfig structures to the backend.
        """
        payload: Dict[str, Any] = {
            "llm": config.llm,
            "description": config.description,
        }

        # Context (grouped)
        if config.enable_context:
            payload["context"] = {"enabled": True}

        # Memory (grouped)
        has_memory = bool(config.memory_session or config.memory_profiles)
        if has_memory:
            if config.memory_session and config.memory_profiles:
                mode = "both"
            elif config.memory_profiles:
                mode = "profile"
            else:
                mode = "session"

            memory_cfg: Dict[str, Any] = {
                "mode": mode,
                "toolset": config.memory_toolset,
                "subagent": config.memory_subagent,
                "mcp": config.memory_mcp,
            }

            if config.memory_profiles:
                first = config.memory_profiles[0]
                if isinstance(first, dict) and "id" in first:
                    memory_cfg["profile_id"] = first["id"]

            payload["memory"] = memory_cfg

        # Knowledge (grouped)
        if config.knowledge_bases:
            payload["knowledge"] = {
                "knowledge_ids": config.knowledge_bases,
                "toolset": config.knowledge_toolset,
                "subagent": config.knowledge_subagent,
                "mcp": config.knowledge_mcp,
            }

        # Dataset (grouped)
        if config.datasets:
            payload["dataset"] = {
                "dataset_ids": config.datasets,
                "toolset": config.data_toolset,
                "subagent": config.data_subagent,
                "mcp": config.data_mcp,
            }

        # Tools: backend "tools" field is for backend-defined callables only.
        # Local tools stay in the SDK process, so we send an empty list here.
        payload["tools"] = []

        # MCP servers
        if config.mcp_servers:
            payload["mcp_servers"] = config.mcp_servers

        # LLM params (grouped)
        llm_params: Dict[str, Any] = {
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
        if config.system_prompt:
            llm_params["system_prompt"] = config.system_prompt
        payload["llm_params"] = llm_params

        return payload

    def _register_subagent_tools(self):
        """Generate and register subagent tool schemas from config"""

        # Iterate over all configured subagents and register
        for subagent_config in self.config.subagents:
            self._register_subagent(subagent_config)

    def _register_subagent(self, subagent_config: SubagentConfig) -> None:
        """
        Register a subagent as a tool

        Core Logic:
        1. Build tool schema from SubagentConfig
        2. Inject builtin-specific context if builtin_type is set
        3. Register tool in registry

        Args:
            subagent_config: SubagentConfig instance

        Data Flow:
            SubagentConfig → tool_schema → tool_registry → LLM sees as tool
        """
        # Build base tool schema
        tool_schema = {
            "name": subagent_config.name,
            "description": subagent_config.description
            or f"Specialized subagent: {subagent_config.name}",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task for the subagent to complete",
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context from main agent",
                        "default": {},
                    },
                },
                "required": ["task"],
            },
            "_is_subagent": True,
            "_subagent_config": {
                "llm": subagent_config.model or self.config.llm,
                "name": subagent_config.name,
                "description": subagent_config.description or "",
                "system_prompt": subagent_config.prompt,
                "max_tokens": subagent_config.max_tokens,
                "temperature": subagent_config.temperature,
            },
        }

        # Inject builtin-specific configuration if applicable
        if subagent_config.builtin_type == "memory":
            tool_schema["_subagent_config"]["memory_session"] = self.config.memory_session
            tool_schema["_subagent_config"]["memory_profiles"] = self.config.memory_profiles
            tool_schema["_subagent_config"]["memory_toolset"] = True

        elif subagent_config.builtin_type == "knowledge":
            tool_schema["_subagent_config"]["knowledge_bases"] = self.config.knowledge_bases
            tool_schema["_subagent_config"]["knowledge_toolset"] = True
            tool_schema["input_schema"]["properties"]["top_k"] = {
                "type": "integer",
                "description": "Number of documents to retrieve per search",
                "default": 10,
            }

        elif subagent_config.builtin_type == "data":
            tool_schema["_subagent_config"]["datasets"] = self.config.datasets
            tool_schema["_subagent_config"]["data_toolset"] = True

        # Register in tool registry
        self.tool_registry.register_subagent(tool_schema)


def _normalize_message(
    message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Normalize message to Anthropic content blocks format

    Supports three input formats:
    1. Plain string: "Hello" → [{"type": "text", "text": "Hello"}]
    2. Single content block: {"type": "text", "text": "Hello"} → [{"type": "text", "text": "Hello"}]
    3. Array of content blocks: [{"type": "text", ...}, {"type": "image", ...}] → [..., ...]

    Args:
        message: Input in any supported format

    Returns:
        List of content blocks in Anthropic format

    Raises:
        ValueError: If format is invalid

    Example:
        # Text message
        blocks = _normalize_message("Hello")

        # Image message
        blocks = _normalize_message({
            "type": "image",
            "source": {
                "type": "url",
                "url": "https://example.com/image.png"
            }
        })

        # Multimodal message
        blocks = _normalize_message([
            {"type": "text", "text": "What's in this image?"},
            {"type": "image", "source": {"type": "url", "url": "..."}}
        ])
    """
    # Case 1: Plain string
    if isinstance(message, str):
        return [{"type": "text", "text": message}]

    # Case 2: Single content block (dict)
    if isinstance(message, dict):
        # Validate it's a proper content block
        block_type = message.get("type")

        if block_type == "text":
            if "text" not in message:
                raise ValueError("Text block must have 'text' field")
            return [message]

        elif block_type == "image":
            if "source" not in message:
                raise ValueError("Image block must have 'source' field")
            source = message["source"]
            if not isinstance(source, dict):
                raise ValueError("Image 'source' must be an object")
            source_type = source.get("type")

            if source_type == "url":
                if "url" not in source:
                    raise ValueError("URL image source must have 'url' field")
            elif source_type == "base64":
                if "media_type" not in source or "data" not in source:
                    raise ValueError("Base64 image source must have 'media_type' and 'data' fields")
            else:
                raise ValueError(
                    f"Invalid image source type: {source_type}. Must be 'url' or 'base64'"
                )

            return [message]

        elif block_type == "tool_result":
            if "tool_use_id" not in message:
                raise ValueError("Tool result block must have 'tool_use_id' field")
            if "content" not in message:
                raise ValueError("Tool result block must have 'content' field")
            return [message]

        else:
            raise ValueError(
                f"Invalid content block type: {block_type}. Must be 'text', 'image', or 'tool_result'"
            )

    # Case 3: Array of content blocks
    if isinstance(message, list):
        if len(message) == 0:
            raise ValueError("Message array cannot be empty")

        # Validate each block
        normalized: List[Dict[str, Any]] = []
        for i, block in enumerate(message):
            if not isinstance(block, dict):
                raise ValueError(f"Block {i} must be a dict, got {type(block).__name__}")

            # Recursively normalize each block (reuse single-block logic)
            normalized.extend(_normalize_message(block))

        return normalized

    # Invalid type
    raise ValueError(f"Message must be str, dict, or list. Got {type(message).__name__}")


class Session:
    """
    Conversation session

    Supports context manager:
        with agent.session(client_id="user_123") as conv:
            conv.chat("Hello")
    """

    def __init__(
        self,
        agent: Agent,
        client_id: str,
        session_id: str,
        client: PopingClient,
        project_id: str = None,
    ):
        """
        Initialize session

        Args:
            agent: Parent agent
            client_id: User ID
            session_id: Session ID
            client: API client
            project_id: Optional project scope for this session
        """
        self.agent = agent
        self.client_id = client_id
        self.session_id = session_id
        self.client = client
        self.closed = False
        # Optional project context for this session
        self.project_id = project_id

        # Message history for SDK-managed mode (when using local tools)
        self._messages: List[Dict[str, Any]] = []

        # Initialize context if enabled
        self._context = None
        if agent.config.enable_context:
            from .context import Context

            self._context = Context(session_id=session_id, client_id=client_id, client=client)

        # Usage tracking for this session
        self._usage_accumulator = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost": 0.0,
        }

    @property
    def context(self):
        """
        Access context for message CRUD and AI operations

        Returns:
            Context instance if enabled, otherwise raises error

        Example:
            with agent.session() as conv:
                # CRUD operations
                key = conv.context.add("user", "Hello")
                msg = conv.context.get(key)

                # AI operations
                result = await conv.context.query("What?")

        Raises:
            AttributeError: If context not enabled (call .with_context() on agent)
        """
        if self._context is None:
            raise AttributeError(
                "Context not enabled. Use agent.with_context() to enable context API."
            )
        return self._context

    @property
    def storage(self):
        """
        Access storage for file upload/download operations

        Returns:
            Storage instance

        Raises:
            None - storage always available

        Example:
            with agent.session(client_id="user_123") as conv:
                # Upload file (returns URI)
                uri = conv.storage.upload("/path/to/image.png")

                # Get download URL (accepts URI or raw resource_id)
                url = conv.storage.get_url(uri)

                # Download file (accepts URI or raw resource_id)
                conv.storage.download(uri, "/tmp/output.png")
        """
        # Lazy initialization
        if not hasattr(self, "_storage"):
            from .storage import Storage

            self._storage = Storage(
                client=self.agent.client._http,
                client_id=self.client_id,
                session_id=self.session_id,
            )

        return self._storage

    @property
    def messages(self) -> List[Dict[str, Any]]:
        """
        Read-only access to all messages

        Returns:
            List of message dicts (chronological order)

        Example:
            with agent.session() as conv:
                conv.chat("Hello")
                conv.chat("How are you?")

                # Read messages
                for msg in conv.messages:
                    print(f"{msg['role']}: {msg['content']}")

        Note:
            For CRUD operations, use conv.context.add/update/delete
        """
        if self._context is None:
            # Context not enabled - return empty list
            # TODO: Load from backend API
            return []

        return self._context.list_all()

    @property
    def usage(self) -> Dict[str, Any]:
        """
        Get accumulated token usage for this session

        Returns:
            Dict with usage statistics:
                {
                    "input_tokens": int,
                    "output_tokens": int,
                    "total_tokens": int,
                    "cost": float  # In credits
                }

        Example:
            with agent.session(client_id="user_123") as conv:
                conv.chat("Hello")
                conv.chat("What's 5 + 3?")

                print(f"Input tokens: {conv.usage['input_tokens']}")
                print(f"Output tokens: {conv.usage['output_tokens']}")
                print(f"Total tokens: {conv.usage['total_tokens']}")
                print(f"Cost: {conv.usage['cost']} credits")

        Note:
            - Usage is accumulated across all chat() calls in this session
            - Only tracks usage from chat() calls made through this Session instance
            - Does not include historical usage from previous sessions
        """
        return self._usage_accumulator.copy()

    def _expand_uri(self, uri: str) -> str:
        """
        Expand simplified URI using session context

        Args:
            uri: Input URI (simplified or complete)

        Returns:
            Expanded URI string

        Example:
            "@storage://file.pdf" → "@storage[alice]://file.pdf"
            "@session://img.png" → "@session[alice/sess_001]://img.png"
        """
        try:
            return URIParser.expand(
                uri,
                client_id=self.client_id,
                session_id=self.session_id,
            )
        except ValueError:
            # If expansion fails, return original URI
            # (might be unsupported scheme or already complete)
            return uri

    def _expand_uris_in_text(self, text: str) -> str:
        """
        Find and expand all URIs in text

        Args:
            text: Input text containing URIs

        Returns:
            Text with all URIs expanded
        """
        uris = URIParser.extract_uris_from_text(text)
        expanded_text = text

        for uri in uris:
            expanded = self._expand_uri(uri)
            expanded_text = expanded_text.replace(uri, expanded)

        return expanded_text

    def _expand_uris_in_content(self, content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Expand URIs in content blocks (text and image sources)

        Args:
            content_blocks: List of content blocks from message

        Returns:
            Content blocks with expanded URIs

        Example:
            Input: [{"type": "text", "text": "Check @storage://file.pdf"}]
            Output: [{"type": "text", "text": "Check @storage[alice]://file.pdf"}]
        """
        expanded_blocks = []

        for block in content_blocks:
            block_copy = block.copy()

            if block.get("type") == "text":
                # Expand URIs in text content
                block_copy["text"] = self._expand_uris_in_text(block["text"])

            elif block.get("type") == "image":
                # Expand image source if it's a URI string
                source = block.get("source", {})
                if isinstance(source, str):
                    # Direct URI reference
                    block_copy["source"] = self._expand_uri(source)
                elif isinstance(source, dict) and source.get("type") == "url":
                    # URL source - expand if it's a URI
                    url = source.get("url", "")
                    if url.startswith("@"):
                        source_copy = source.copy()
                        source_copy["url"] = self._expand_uri(url)
                        block_copy["source"] = source_copy

            expanded_blocks.append(block_copy)

        return expanded_blocks

    def chat(
        self,
        message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        tool: Optional[List[str] | bool] = None,
        stream: bool = False,
    ) -> str:
        """
        Send message to agent with SDK-managed agentic loop for local tools

        Two modes:
        1. With local tools: SDK-managed agentic loop
           - Submit user message to backend
           - Call backend for single LLM turn
           - Execute local tools in SDK
           - Submit tool results to backend
           - Loop until end_turn

        2. Without local tools: Backend-managed (legacy)
           - Backend handles everything
           - Returns final response

        Args:
            message: User message in one of three formats:
                - String: "Hello"
                - Single content block: {"type": "text", "text": "Hello"}
                - Array of content blocks: [{"type": "text", ...}, {"type": "image", ...}]

                Content block types:
                - text: {"type": "text", "text": "..."}
                - image: {"type": "image", "source": {"type": "url", "url": "..."}}
                - image (base64): {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}
            tool: Tool override
                - None: Use all tools
                - False: Disable all tools
                - List[str]: Use only specified tools
            stream: Stream response (not yet implemented)

        Returns:
            Final agent response text

        Raises:
            ValueError: If session is closed
            APIError: If backend chat fails

        Example:
            @tool()
            def add(a: int, b: int) -> int:
                return a + b

            agent = poping.agent(...).with_tools(local=[add]).build()
            with agent.session(client_id="user_123") as conv:
                resp = conv.chat("What is 5 + 3?")  # SDK executes add() locally
        """
        if self.closed:
            raise ValueError("Session is closed")

        # Normalize message to content blocks
        content_blocks = _normalize_message(message)

        # Check if agent has ANY tools (local OR cloud)
        has_any_tools = (
            len(self.agent.config.local_tools) > 0 or len(self.agent.tool_registry.cloud_tools) > 0
        )

        if has_any_tools:
            # SDK-managed mode: Execute tools in SDK (local) or via backend (cloud)
            return self._chat_with_local_tools(content_blocks, tool)
        else:
            # Legacy mode: Backend-managed (no tools)
            return self._chat_legacy(content_blocks)

    def _chat_legacy(self, content_blocks: List[Dict[str, Any]]) -> str:
        """
        Legacy mode: Backend-managed agentic loop

        Backend handles everything via POST /api/v1/agents/{agent_id}/chat:
        - Loads conversation history
        - Executes full agentic loop
        - Saves responses
        - Returns final text
        """
        expanded_content = self._expand_uris_in_content(content_blocks)
        # Backend legacy chat expects a plain text `message` field, not content blocks
        message_text = self._extract_text(expanded_content)

        # Build request payload and include end_user_id when available so backend
        # can bind conversation storage to the correct end user.
        request_data: Dict[str, Any] = {
            "message": message_text,
            "session_id": self.session_id,
            "project_id": self.project_id,
        }
        if self.client_id:
            request_data["end_user_id"] = self.client_id

        response = self.client._http._request(
            "POST",
            f"/api/v1/agents/{self.agent.agent_id}/chat",
            data=request_data,
        )

        # Accumulate usage if present in response (for future backend support)
        if "usage" in response:
            self._accumulate_usage(response["usage"])

        return response["message"]

    def _chat_with_local_tools(
        self, content_blocks: List[Dict[str, Any]], tool_override: Optional[List[str] | bool] = None
    ) -> str:
        """
        SDK-managed agentic loop with local tools

        Flow:
        1. Submit user message to backend (saves to OSS)
        2. Build tool schemas (local + cloud + subagent)
        3. Agentic loop:
           a. Call backend for single LLM turn
           b. Backend returns tool_use blocks (no execution)
           c. SDK executes tools (local/cloud/subagent routing)
           d. Submit tool results to backend
           e. Loop until end_turn
        4. Return final response text
        """
        # Step 1: Submit user message to backend (with URI expansion)
        expanded_content = self._expand_uris_in_content(content_blocks)
        message_payload: Dict[str, Any] = {
            "role": "user",
            "content": expanded_content,
            "project_id": self.project_id,
        }
        # Pass through end_user_id so storage context can resolve @context URIs per end user
        if self.client_id:
            message_payload["end_user_id"] = self.client_id

        self.client._http._request(
            "PUT",
            f"/api/v1/agents/{self.agent.agent_id}/sessions/{self.session_id}/message",
            data=message_payload,
        )

        # Step 2: Build tool schemas (local + subagent only)
        tools_to_use = self._build_tool_schemas(tool_override)

        # Step 3: Agentic loop
        max_iterations = 10
        for iteration in range(max_iterations):
            # Call backend for single LLM turn
            # Build request payload and split local vs cloud tools by ID prefix
            request_data: Dict[str, Any] = {"session_id": self.session_id}
            if self.project_id:
                request_data["project_id"] = self.project_id
            # Hint backend about end user so it can bind StorageContext correctly
            if self.client_id:
                request_data["end_user_id"] = self.client_id

            # Local tool schemas (from SDK)
            if tools_to_use:
                local_tool_schemas = tools_to_use
                request_data["local_tools"] = local_tool_schemas

            # Cloud tool IDs (registry-managed)
            cloud_tool_ids = list(self.agent.tool_registry.cloud_tools)
            if cloud_tool_ids:
                request_data["cloud_tools"] = cloud_tool_ids

            response = self.client._http._request(
                "POST", f"/api/v1/agents/{self.agent.agent_id}/chat", data=request_data
            )

            # Accumulate usage if present in response
            if "usage" in response:
                self._accumulate_usage(response["usage"])

            stop_reason = response["stop_reason"]
            content = response["content"]

            # Check if done
            if stop_reason == "end_turn":
                # Extract text from content blocks
                return self._extract_text(content)

            # Execute tools if tool_use blocks present
            if stop_reason == "tool_use":
                # Extract tool_use blocks from content
                tool_calls = [
                    block
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "tool_use"
                ]

                # Execute tools (local/cloud/subagent routing)
                tool_results = self._execute_tools(tool_calls)

                # Submit tool results to backend (saves to OSS)
                tool_message_payload: Dict[str, Any] = {
                    "role": "user",
                    "content": tool_results,  # List of tool_result blocks
                    "project_id": self.project_id,
                }
                if self.client_id:
                    tool_message_payload["end_user_id"] = self.client_id

                self.client._http._request(
                    "PUT",
                    f"/api/v1/agents/{self.agent.agent_id}/sessions/{self.session_id}/message",
                    data=tool_message_payload,
                )

                # Continue loop
                continue

            # Handle max_tokens
            if stop_reason == "max_tokens":
                return self._extract_text(content)

        # Max iterations reached
        raise RuntimeError(f"Max iterations ({max_iterations}) exceeded")

    def _extract_text(self, content: List[Dict]) -> str:
        """
        Extract text from content blocks

        Args:
            content: List of content blocks from LLM response
                [
                    {"type": "text", "text": "Hello"},
                    {"type": "tool_use", ...}
                ]

        Returns:
            Concatenated text from all text blocks
        """
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return " ".join(text_parts) if text_parts else ""

    def _build_tool_schemas(self, tool_override) -> Optional[List[Dict]]:
        """
        Build tool schemas for LLM call

        Args:
            tool_override: None (all tools) | False (no tools) | List[str] (specific tools)

        Returns:
            List of tool schemas in Anthropic format, or None if tools disabled
        """
        if tool_override is False:
            # Tools explicitly disabled
            return None

        # Get all tool schemas
        all_schemas = self.agent.tool_registry.to_anthropic_schema()

        if tool_override is None:
            # Use all tools
            return all_schemas if all_schemas else None

        if isinstance(tool_override, list):
            # Filter to specified tools
            filtered = [s for s in all_schemas if s["name"] in tool_override]
            return filtered if filtered else None

        # Invalid override - use all tools
        return all_schemas if all_schemas else None

    def _accumulate_usage(self, usage: Dict[str, Any]) -> None:
        """
        Accumulate token usage from API response

        Args:
            usage: Usage dict from backend response
                {
                    "input_tokens": int,
                    "output_tokens": int
                }

        Logic:
            1. Extract input_tokens and output_tokens
            2. Add to session accumulator
            3. Calculate cost using pricing module

        Note:
            - Cost calculation uses backend's pricing.py via import
            - Falls back to 0 if pricing module unavailable
        """
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        # Accumulate tokens
        self._usage_accumulator["input_tokens"] += input_tokens
        self._usage_accumulator["output_tokens"] += output_tokens
        self._usage_accumulator["total_tokens"] = (
            self._usage_accumulator["input_tokens"] + self._usage_accumulator["output_tokens"]
        )

        # Calculate cost for this turn
        # We need the model name from the agent config
        model = self.agent.config.llm
        try:
            # Import pricing module to calculate cost
            # This assumes backend's pricing.py is accessible
            # In production, backend should return cost in the response
            from llm.pricing import calculate_cost  # type: ignore

            turn_cost = calculate_cost(model, input_tokens, output_tokens)
            self._usage_accumulator["cost"] += turn_cost
        except ImportError:
            # Pricing module not available (SDK-only environment)
            # Backend should include cost in response for production
            pass

    def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """
        Execute tool calls (local, cloud, or subagent)

        For each tool call:
        1. Check if it's a subagent tool → Execute subagent
        2. Check if it's a local tool → Execute Python function directly in SDK
        3. Otherwise → Call backend API (POST /api/v1/tools/execute)
        4. Collect results and build tool_result blocks

        Args:
            tool_calls: List of tool call dicts
                [
                    {
                        "id": "toolu_123",
                        "name": "tool_name",
                        "input": {"arg1": "value1"}
                    }
                ]

        Returns:
            List of tool_result blocks for next LLM call
                [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_123",
                        "content": "result text"
                    }
                ]
        """
        tool_results = []
        print(tool_calls)
        for tool_call in tool_calls:
            tool_id = tool_call["id"]
            tool_name = tool_call["name"]
            tool_input = tool_call["input"]

            # Normalize tool name: AI returns names with underscores (Anthropic constraint)
            # Try to find the original tool name by replacing the first underscore with a dot
            original_tool_name = tool_name

            if tool_name not in self.agent.tool_registry.local_tools:
                # Check dotted version in both local and cloud tool registries
                dotted_name = tool_name.replace("_", ".", 1)
                if dotted_name in self.agent.tool_registry.local_tools:
                    original_tool_name = dotted_name
                elif dotted_name in self.agent.tool_registry.cloud_tools:
                    original_tool_name = dotted_name

            try:
                # Check if this is a subagent tool
                if self._is_subagent_tool(original_tool_name):
                    # Execute subagent (NEW)
                    result = self._execute_subagent(original_tool_name, tool_input)

                # Check if local tool
                elif original_tool_name in self.agent.tool_registry.local_tools:
                    # Execute locally (call Python function)
                    func = self.agent.tool_registry.local_tools[original_tool_name]
                    result = func._original_func(**tool_input)

                # Check if cloud tool or predefined tool (memory.*, knowledge.*, data.*)
                elif original_tool_name in self.agent.tool_registry.cloud_tools:
                    # For context.* tools, inject parent session context if available
                    if original_tool_name.startswith("context."):
                        # Check if this session has parent context injected (for internal agents)
                        if hasattr(self, "_parent_session_id") and hasattr(self, "_parent_client_id"):
                            tool_input_with_context = tool_input.copy()
                            tool_input_with_context["_session_id"] = self._parent_session_id
                            tool_input_with_context["_client_id"] = self._parent_client_id
                            tool_input_with_context["_project_id"] = self.project_id or "default"
                            result = self.client._http.execute_tool(
                                original_tool_name, tool_input_with_context
                            )
                        else:
                            # Use current session context
                            tool_input_with_context = tool_input.copy()
                            tool_input_with_context["_session_id"] = self.session_id
                            tool_input_with_context["_client_id"] = self.client_id
                            tool_input_with_context["_project_id"] = self.project_id or "default"
                            result = self.client._http.execute_tool(
                                original_tool_name, tool_input_with_context
                            )
                    else:
                        # Non-context tools: execute as-is
                        result = self.client._http.execute_tool(original_tool_name, tool_input)
                    print(result, "*" * 100)
                else:
                    # Unknown tool
                    result = f"Error: Unknown tool '{tool_name}'"

                # Handle result format - support m
                # ultiple formats
                # Format 1: Dict with "content" key (cloud tools return this)
                #   {"content": [...], "is_error": False}
                # Format 2: List of content blocks
                #   [{"type": "text", "text": "..."}, ...]
                # Format 3: Plain string
                #   "result text"
                # Format 4: Other types - convert to JSON

                if isinstance(result, dict) and "content" in result:
                    # Cloud tool format: extract content and is_error
                    content = result["content"]
                    is_error = result.get("is_error", False)

                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": content,
                    }

                    if is_error:
                        tool_result["is_error"] = True

                    tool_results.append(tool_result)

                elif isinstance(result, list):
                    # Result is already List[ContentBlock] - use directly
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tool_id, "content": result}
                    )

                elif isinstance(result, str):
                    # String result - use as-is
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tool_id, "content": result}
                    )

                else:
                    # Other types - convert to JSON string
                    import json

                    try:
                        content = json.dumps(result)
                    except:
                        content = str(result)

                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": tool_id, "content": content}
                    )

            except Exception as e:
                # Tool execution error
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": f"Error executing tool: {str(e)}",
                        "is_error": True,
                    }
                )

        return tool_results

    def _extract_tool_calls(self, content: List[Dict]) -> List[Dict]:
        """
        Extract tool_use blocks from content

        Args:
            content: Content blocks from LLM response
                [
                    {"type": "text", "text": "I'll help with that"},
                    {"type": "tool_use", "id": "toolu_123", "name": "search", "input": {...}}
                ]

        Returns:
            List of tool call dicts
                [
                    {"id": "toolu_123", "name": "search", "input": {...}}
                ]
        """
        tool_calls = []
        for block in content:
            if block.get("type") == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id"),
                        "name": block.get("name"),
                        "input": block.get("input", {}),
                    }
                )
        return tool_calls

    def _extract_text(self, content: List[Dict]) -> str:
        """
        Extract text from content blocks

        Args:
            content: Content blocks from LLM response
                [
                    {"type": "text", "text": "Hello"},
                    {"type": "text", "text": " world"}
                ]

        Returns:
            Combined text string: "Hello world"
        """
        text_parts = []
        for block in content:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "".join(text_parts)

    def _is_subagent_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is a subagent

        Looks for _is_subagent flag in tool schema

        Args:
            tool_name: Tool name to check

        Returns:
            True if tool is a subagent, False otherwise
        """
        # Get all tool schemas
        all_schemas = self.agent.tool_registry.to_anthropic_schema()

        for schema in all_schemas:
            if schema["name"] == tool_name:
                return schema.get("_is_subagent", False)

        return False

    def _get_subagent_config(self, tool_name: str) -> Dict[str, Any]:
        """
        Extract subagent configuration from tool schema

        Args:
            tool_name: Tool name

        Returns:
            Subagent configuration dict
        """
        all_schemas = self.agent.tool_registry.to_anthropic_schema()

        for schema in all_schemas:
            if schema["name"] == tool_name:
                return schema.get("_subagent_config", {})

        return {}

    def _execute_subagent(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a subagent

        Core logic:
        1. Get subagent configuration from tool schema
        2. Create new Agent instance with subagent config
        3. Inject context into subagent's first message
        4. Execute subagent.chat() in NEW context window
        5. Return subagent's response

        Args:
            tool_name: Subagent tool name
            tool_input: Tool arguments
                {
                    "query" or "task": The task for subagent,
                    "context": Optional context from main agent
                }

        Returns:
            Subagent response as string
        """
        import json

        # Get subagent configuration
        subagent_config = self._get_subagent_config(tool_name)

        if not subagent_config:
            return f"Error: Subagent configuration not found for {tool_name}"

        # Extract task and context from tool input
        task = tool_input.get("query") or tool_input.get("task")
        context = tool_input.get("context", {})
        top_k = tool_input.get("top_k")

        if not task:
            return "Error: No query or task provided to subagent"

        # Build subagent message with context injection
        context_str = json.dumps(context, indent=2) if context else "None"

        subagent_message = f"""Task: {task}

Context from main agent:
{context_str}

Please complete the task and return a concise, well-structured response."""

        if top_k:
            subagent_message += f"\n\nRetrieve top {top_k} results."

        # Create subagent Agent instance
        from . import agent as agent_module

        subagent_builder = agent_module.AgentBuilder(
            client=self.client,  # Pass Poping client
            llm=subagent_config.get("llm", self.agent.config.llm),
            name=subagent_config.get("name"),
            description=subagent_config.get("description"),
        )

        # Configure LLM settings
        subagent_builder = subagent_builder.with_llm_config(
            max_tokens=subagent_config.get("max_tokens", 4096),
            temperature=subagent_config.get("temperature", 0.7),
            system_prompt=subagent_config.get("system_prompt"),
        )

        # Configure modules based on subagent_config
        # Memory module
        if subagent_config.get("enable_session_memory") or subagent_config.get("memory_toolset"):
            memory_session = {}
            if subagent_config.get("enable_session_memory"):
                memory_session["strategy"] = "summary"

            memory_profiles = []
            if subagent_config.get("memory_id"):
                memory_profiles.append({"id": subagent_config["memory_id"]})

            subagent_builder = subagent_builder.with_memory(
                session=memory_session if memory_session else None,
                profiles=memory_profiles if memory_profiles else None,
                toolset=subagent_config.get("memory_toolset", False),
                subagent=False,  # CRITICAL: Subagents cannot have subagents (depth limit)
            )

        # Knowledge module
        if subagent_config.get("knowledge_bases"):
            subagent_builder = subagent_builder.with_knowledge(
                subagent_config["knowledge_bases"],
                toolset=subagent_config.get("knowledge_toolset", False),
                subagent=False,  # CRITICAL: Depth limit
            )

        # Data module
        if subagent_config.get("datasets"):
            subagent_builder = subagent_builder.with_data(
                subagent_config["datasets"],
                toolset=subagent_config.get("data_toolset", False),
                subagent=False,  # CRITICAL: Depth limit
            )

        # Build subagent (use temporary name for internal subagent)
        import uuid

        temp_name = f"_subagent_{uuid.uuid4().hex[:8]}"
        subagent_instance = subagent_builder.build(name=temp_name)

        # Execute subagent in NEW context window
        # This is the key: subagent has its own 200K context, separate from main agent
        with subagent_instance.session(
            client_id=self.client_id, project=self.project_id
        ) as subagent_session:
            subagent_response = subagent_session.chat(
                subagent_message,
                tool=True,  # Subagent can use tools
            )

        # Return subagent's response to main agent
        return subagent_response

    def close(self) -> None:
        """
        Close session and persist memory

        Automatically called when using context manager
        """
        if self.closed:
            return

        # TODO: Trigger memory persistence via API
        # self.client.persist_session_memory(self.client_id, self.session_id)

        self.closed = True

    def _serialize_config(self) -> Dict[str, Any]:
        """Serialize agent config for API"""
        return {
            "llm": self.agent.config.llm,
            "name": self.agent.config.name,
            "description": self.agent.config.description,
            "enable_context": self.agent.config.enable_context,
            "memory": {
                "session": self.agent.config.memory_session,
                "profiles": self.agent.config.memory_profiles,
                "toolset": self.agent.config.memory_toolset,
                "subagent": self.agent.config.memory_subagent,
            },
            "knowledge": {
                "kb_ids": self.agent.config.knowledge_bases,
                "toolset": self.agent.config.knowledge_toolset,
                "subagent": self.agent.config.knowledge_subagent,
            },
            "data": {
                "dataset_ids": self.agent.config.datasets,
                "toolset": self.agent.config.data_toolset,
                "subagent": self.agent.config.data_subagent,
            },
            "tools": self.agent.tool_registry.to_anthropic_schema(),
            "system_prompt": self.agent.config.system_prompt,
            "max_tokens": self.agent.config.max_tokens,
            "temperature": self.agent.config.temperature,
        }

    def __enter__(self) -> "Session":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - auto close"""
        self.close()


def agent(llm: str, name: str = None, description: str = None) -> AgentBuilder:
    """
    Create agent builder

    Args:
        llm: Model identifier
        name: Agent name
        description: Agent description

    Returns:
        AgentBuilder instance

    Example:
        agent = poping.agent(llm="claude-3-5-sonnet-20241022")
    """
    return AgentBuilder(llm=llm, name=name, description=description)
