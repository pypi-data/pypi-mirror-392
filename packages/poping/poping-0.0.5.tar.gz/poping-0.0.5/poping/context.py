"""
Poping Context - Message management with AI-powered operations
"""

import uuid
from typing import List, Dict, Any, Optional, Union
from .client import PopingClient


class Context:
    """
    Context for message management

    Provides:
    - Layer 1: CRUD operations (add/get/update/delete)
    - Layer 2: AI-powered operations (query/revise/forget)

    Usage:
        # Option 1: Direct instantiation (in-memory)
        from poping import Context
        ctx = Context()
        key = ctx.add("user", "Hello")

        # Option 2: From session (with backend storage)
        with agent.session() as conv:
            key = conv.context.add("user", "Hello")
            result = await conv.context.query("What?")

        # Option 3: Get existing session context
        from poping import sessions
        ctx = sessions.get("session_123").context
    """

    def __init__(self, session_id: str = None, client_id: str = None, client: PopingClient = None):
        """
        Initialize context with dual-mode support (standalone vs backend)

        Args:
            session_id: Session identifier (auto-generated if None)
            client_id: User identifier (default if None)
                NOTE: In SDK, client_id represents the CLIENT (SDK user).
                Backend uses client_id for this concept. The mapping is:
                SDK client_id → Backend client_id (who owns the project)
            client: API client for backend communication (auto-detected if None)

        Mode detection logic:
            - If client is provided: use backend mode
            - Else try to auto-detect via poping.get_client();
              if found: backend mode, else: standalone mode

        Standalone mode (in-memory):
            - Messages stored locally in Python dict
            - No backend API calls
            - Good for testing/prototyping

        Backend mode:
            - Messages persisted to backend storage via HTTP API
            - Enables future AI operations
        """
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:12]}"
        self.client_id = client_id or "default_user"

        # Auto-detect backend client if not explicitly provided
        detected_client = None
        if client is None:
            try:
                # Prefer absolute import to match runtime usage: `import poping`
                import poping  # type: ignore

                if hasattr(poping, "get_client"):
                    detected_client = poping.get_client()
            except Exception:
                # Fallback to package-relative import to avoid NameError in embedded usage
                try:
                    from . import get_client as _get_client  # type: ignore

                    detected_client = _get_client()
                except Exception:
                    detected_client = None

        # Store client and mode
        self.client = client or detected_client
        self._mode = "backend" if self.client is not None else "standalone"

        # In-memory storage for standalone mode
        self._messages: Dict[str, Dict[str, Any]] = {}

    # ========================================================================
    # Layer 1: CRUD Operations
    # ========================================================================

    def add(
        self, role: str, content: Union[str, List[Dict[str, Any]]], metadata: dict = None
    ) -> str:
        """
        [Function: add]
        =================
        - Input: role (str), content (str | list[dict]), metadata (dict|None)
        - Output: key (str) - message identifier
        - Role in Flow: Entry point for message creation
        - Logic:
            1. Backend mode: POST to API, return key from response
            2. Standalone mode: Generate key, store in _messages dict

        Content formats:
            - Simple text: "Hello world"
            - Multimodal (Anthropic format): [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.jpg"
                    }
                }
              ]

        Example:
            # Text only
            key = ctx.add("user", "Hello")

            # With image (URL)
            key = ctx.add("user", [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image", "source": {"type": "url", "url": "https://..."}}
            ])

            # With image (Base64)
            key = ctx.add("user", [
                {"type": "text", "text": "Analyze this"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": "<base64-encoded-data>"
                    }
                }
            ])
        """
        from datetime import datetime

        # Backend mode
        if self._mode == "backend":
            if not self.client:
                raise RuntimeError("Backend mode requires a valid client; none found.")
            http = getattr(self.client, "_http", self.client)
            if not hasattr(http, "_request"):
                raise RuntimeError("Invalid backend client: missing _request() method.")

            response = http._request(
                "POST",
                f"/api/v1/context/{self.session_id}/messages",
                data={
                    "role": role,
                    "content": content,
                    "metadata": metadata,
                },
            )
            # Expecting backend to return {"key": "...", ...}
            key = response.get("key") if isinstance(response, dict) else None
            if not key:
                raise RuntimeError("Backend did not return a message key.")
            return key

        # Standalone mode
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        key = f"{role}_{msg_id[:8]}#{timestamp[:10]}"

        self._messages[key] = {
            "id": msg_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": timestamp,
            "key": key,
        }

        return key

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        [Function: get]
        ==============
        - Input: key (str)
        - Output: message (dict|None)
        - Role in Flow: Retrieve a message by key
        - Logic:
            1. Backend mode: GET from API and return message dict
            2. Standalone mode: Lookup in _messages dict
        """
        if self._mode == "backend":
            if not self.client:
                raise RuntimeError("Backend mode requires a valid client; none found.")
            http = getattr(self.client, "_http", self.client)
            if not hasattr(http, "_request"):
                raise RuntimeError("Invalid backend client: missing _request() method.")

            return http._request(
                "GET",
                f"/api/v1/context/{self.session_id}/messages/{key}",
            )

        # Standalone mode
        return self._messages.get(key)

    def update(self, key: str, **updates) -> None:
        """
        [Function: update]
        ==================
        - Input: key (str), updates (kwargs: content, metadata)
        - Output: None
        - Role in Flow: Modify an existing message's content/metadata
        - Logic:
            1. Backend mode: PATCH to API with provided fields
            2. Standalone mode: Update local dict (merge metadata)
        """
        if self._mode == "backend":
            if not self.client:
                raise RuntimeError("Backend mode requires a valid client; none found.")
            http = getattr(self.client, "_http", self.client)
            if not hasattr(http, "_request"):
                raise RuntimeError("Invalid backend client: missing _request() method.")

            body: Dict[str, Any] = {}
            if "content" in updates:
                body["content"] = updates["content"]
            if "metadata" in updates:
                body["metadata"] = updates["metadata"]

            http._request(
                "PATCH",
                f"/api/v1/context/{self.session_id}/messages/{key}",
                data=body,
            )
            return

        # Standalone mode
        if key not in self._messages:
            raise KeyError(f"Message not found: {key}")

        msg = self._messages[key]
        if "content" in updates:
            msg["content"] = updates["content"]
        if "metadata" in updates and updates["metadata"] is not None:
            # Merge dictionaries if both present
            if isinstance(msg.get("metadata"), dict) and isinstance(updates["metadata"], dict):
                msg["metadata"].update(updates["metadata"])
            else:
                msg["metadata"] = updates["metadata"]

    def delete(self, key: str) -> None:
        """
        [Function: delete]
        ==================
        - Input: key (str)
        - Output: None
        - Role in Flow: Remove a message by key
        - Logic:
            1. Backend mode: DELETE via API
            2. Standalone mode: Remove from _messages dict
        """
        if self._mode == "backend":
            if not self.client:
                raise RuntimeError("Backend mode requires a valid client; none found.")
            http = getattr(self.client, "_http", self.client)
            if not hasattr(http, "_request"):
                raise RuntimeError("Invalid backend client: missing _request() method.")

            http._request(
                "DELETE",
                f"/api/v1/context/{self.session_id}/messages/{key}",
            )
            return

        # Standalone mode
        self._messages.pop(key, None)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        [Function: list_all]
        ====================
        - Input: None
        - Output: List[dict] - messages in chronological order
        - Role in Flow: Enumerate context messages
        - Logic:
            1. Backend mode: GET list from API
            2. Standalone mode: Return sorted local messages
        """
        if self._mode == "backend":
            if not self.client:
                raise RuntimeError("Backend mode requires a valid client; none found.")
            http = getattr(self.client, "_http", self.client)
            if not hasattr(http, "_request"):
                raise RuntimeError("Invalid backend client: missing _request() method.")

            result = http._request(
                "GET",
                f"/api/v1/context/{self.session_id}/messages",
            )
            # Expect list of messages from backend
            if isinstance(result, list):
                return result
            # Some backends may wrap result under a key
            if isinstance(result, dict) and "items" in result:
                return result.get("items", [])
            return []

        # Standalone mode
        return sorted(self._messages.values(), key=lambda m: m["created_at"])

    def export(self, type: str = "anthropic") -> List[Dict[str, Any]]:
        """
        [Function: export]
        ==================
        - Input: type ("openai" | "anthropic")
        - Output: List[dict] - Messages in specified format
        - Role in Flow: Export messages for LLM API consumption
        - Logic:
            1. Get all messages via list_all()
            2. Convert to requested format
            3. Return formatted messages array

        Formats:
            - "openai": Simple text format, multimodal content → text only
            - "anthropic": Content blocks format, preserves multimodal

        Example:
            # OpenAI format (text only)
            messages = ctx.export(type="openai")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )

            # Anthropic format (full multimodal)
            messages = ctx.export(type="anthropic")
            response = anthropic.messages.create(
                model="claude-haiku-4-5-20251001",
                messages=messages
            )

            # Default is Anthropic
            messages = ctx.export()
        """
        if type not in ["openai", "anthropic"]:
            raise ValueError(f"Invalid export type: {type}. Must be 'openai' or 'anthropic'")

        all_messages = self.list_all()
        result = []

        if type == "openai":
            # OpenAI format: simple text, strip images
            for msg in all_messages:
                content = msg["content"]

                # Handle multimodal content: extract text only
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    content = " ".join(text_parts)

                result.append({"role": msg["role"], "content": content})

        else:  # anthropic
            # Anthropic format: content blocks, preserve multimodal
            for msg in all_messages:
                content = msg["content"]

                # Convert string content to content blocks format
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]

                result.append({"role": msg["role"], "content": content})

        return result

    def _require_cloud(self):
        """
        [Function: _require_cloud]
        ==========================
        - Input: None
        - Output: None (raises on failure)
        - Role in Flow: Validation gate for cloud-only operations
        - Logic:
            1. Check if backend mode is enabled
            2. Check if valid client_id is present
            3. Raise clear errors if validation fails

        Raises:
            RuntimeError: If standalone mode or invalid client_id
        """
        if self._mode != "backend":
            raise RuntimeError(
                "This operation requires backend mode. "
                "Configure backend via poping.set(api_key='...') or pass client explicitly."
            )

        if not self.client_id or self.client_id == "default_user":
            raise RuntimeError(
                "This operation requires a valid client_id. "
                "Provide client_id when creating Context or Session."
            )

    def _get_context_tool_ids(self) -> List[str]:
        """
        [Function: _get_context_tool_ids]
        =================================
        - Input: None
        - Output: List[str] - Cloud tool IDs for context operations
        - Role in Flow: Specify which backend tools to enable
        - Logic:
            Return list of context.* tool IDs registered in backend

        Design:
            - Uses cloud tools from backend/tools/context/
            - Tools execute on backend with proper session context
            - No local tool wrappers needed
        """
        return ["context.list_all", "context.get", "context.update", "context.delete"]

    # ========================================================================
    # Layer 2: AI-Powered Operations (High-level APIs)
    # ========================================================================

    async def search(self, query: str, top_k: int = 5, scope: str = "session") -> Dict[str, Any]:
        """
        [Function: search]
        ==================
        - Input: query (str), top_k (int), scope (str)
        - Output: dict - {"results": [...], "count": N}
        - Role in Flow: Semantic search using internal agent
        - Logic:
            1. Validate cloud mode
            2. Create internal agent with CRUD tools
            3. Execute search task
            4. Parse and return results

        Args:
            query: Search query
            top_k: Number of results
            scope: "session" or "profile" or "both"

        Returns:
            {"results": [{"key": "...", "content": "...", "score": 0.95}], "count": N}

        Example:
            results = await ctx.search("budget discussion", top_k=3)
            for result in results["results"]:
                print(f"{result['score']}: {result['content']}")
        """
        self._require_cloud()

        import poping

        tool_ids = self._get_context_tool_ids()
        agent = (
            poping.agent(llm="claude-haiku-4-5-20251001")
            .with_tools(cloud=tool_ids)
            .build(name=f"_search_agent_{self.session_id[:8]}")
        )

        task = f"""Search messages for: "{query}"
Return top {top_k} most relevant messages.
Scope: {scope}

Output JSON format:
{{
    "results": [{{"key": "...", "content": "...", "score": 0.95}}],
    "count": N
}}"""

        # Internal agent uses unique session to avoid polluting parent history
        # But context tools will operate on parent session via injected _session_id
        internal_session_id = f"_internal_{uuid.uuid4().hex[:16]}"
        with agent.session(client_id=self.client_id, session_id=internal_session_id) as conv:
            # Inject parent session context into conv for tool execution
            conv._parent_session_id = self.session_id
            conv._parent_client_id = self.client_id
            response = conv.chat(task)

        return response

    async def query(
        self, query: str, style: str = "brief", scope: str = "session"
    ) -> Dict[str, Any]:
        """
        [Function: query]
        =================
        - Input: query (str), style (str), scope (str)
        - Output: dict - {"answer": "...", "sources": [...]}
        - Role in Flow: Q&A using internal agent
        - Logic:
            1. Validate cloud mode
            2. Create internal agent with CRUD tools
            3. Execute query task
            4. Parse and return answer with sources

        Args:
            query: Question to ask
            style: "brief" | "bullet" | "detailed"
            scope: "session" or "profile" or "both"

        Returns:
            {"answer": "...", "sources": [...]}

        Example:
            result = await ctx.query("What did we discuss about the budget?", style="bullet")
            print(result["answer"])
        """
        self._require_cloud()

        import poping

        tool_ids = self._get_context_tool_ids()
        agent = (
            poping.agent(llm="claude-haiku-4-5-20251001")
            .with_tools(cloud=tool_ids)
            .build(name=f"_query_agent_{self.session_id[:8]}")
        )

        task = f"""Answer this question based on conversation messages: "{query}"

Style: {style}
Scope: {scope}

Instructions:
1. Search messages using context_list_all tool
2. Find relevant information
3. Generate answer in {style} style
4. Include sources (message keys)

Output JSON format:
{{
    "answer": "...",
    "sources": [{{"key": "...", "content": "..."}}]
}}"""

        # Internal agent uses unique session to avoid polluting parent history
        internal_session_id = f"_internal_{uuid.uuid4().hex[:16]}"
        with agent.session(client_id=self.client_id, session_id=internal_session_id) as conv:
            # Inject parent session context into conv for tool execution
            conv._parent_session_id = self.session_id
            conv._parent_client_id = self.client_id
            response = conv.chat(task)

        return response

    async def summarize(self, scope: str = "window", style: str = "brief") -> str:
        """
        [Function: summarize]
        =====================
        - Input: scope (str), style (str)
        - Output: str - Summary text
        - Role in Flow: Conversation summarization using internal agent
        - Logic:
            1. Validate cloud mode
            2. Create internal agent with CRUD tools
            3. Execute summarization task
            4. Return summary text

        Args:
            scope: "window" (recent) or "all"
            style: "brief" | "detailed"

        Returns:
            Summary text

        Example:
            summary = await ctx.summarize(scope="all", style="detailed")
            print(summary)
        """
        self._require_cloud()

        import poping

        tool_ids = self._get_context_tool_ids()
        agent = (
            poping.agent(llm="claude-haiku-4-5-20251001")
            .with_tools(cloud=tool_ids)
            .build(name=f"_summarize_agent_{self.session_id[:8]}")
        )

        task = f"""Summarize the conversation messages.

Scope: {scope}
Style: {style}

Instructions:
1. Use context_list_all to read all messages
2. {"Focus on recent messages" if scope == "window" else "Include all messages"}
3. Generate {style} summary
4. Return plain text summary (not JSON)"""

        # Internal agent uses unique session to avoid polluting parent history
        internal_session_id = f"_internal_{uuid.uuid4().hex[:16]}"
        with agent.session(client_id=self.client_id, session_id=internal_session_id) as conv:
            # Inject parent session context into conv for tool execution
            conv._parent_session_id = self.session_id
            conv._parent_client_id = self.client_id
            response = conv.chat(task)

        return response

    async def revise(self, about: str, correction: str, scope: str = "session") -> Dict[str, Any]:
        """
        [Function: revise]
        ==================
        - Input: about (str), correction (str), scope (str)
        - Output: dict - {"affected": {"messages": N, "profile_items": 0}}
        - Role in Flow: AI-assisted message correction using internal agent
        - Logic:
            1. Validate cloud mode
            2. Create internal agent with CRUD tools
            3. Execute revision task
            4. Parse and return affected counts

        Args:
            about: Topic to revise
            correction: Correction to apply
            scope: "session" or "profile" or "both"

        Returns:
            {"affected": {"messages": 2, "profile_items": 0}}

        Example:
            result = await ctx.revise(
                about="project budget",
                correction="Actually $15k not $10k"
            )
            print(f"Updated {result['affected']['messages']} messages")
        """
        self._require_cloud()

        import poping

        tool_ids = self._get_context_tool_ids()
        agent = (
            poping.agent(llm="claude-haiku-4-5-20251001")
            .with_tools(cloud=tool_ids)
            .build(name=f"_revise_agent_{self.session_id[:8]}")
        )

        task = f"""Revise messages about: "{about}"
Correction: {correction}
Scope: {scope}

Instructions:
1. Use context_list_all to find messages about "{about}"
2. Update relevant messages with the correction using context_update
3. Return JSON with count of affected messages

Output JSON format:
{{
    "affected": {{"messages": N, "profile_items": 0}}
}}"""

        # Internal agent uses unique session to avoid polluting parent history
        internal_session_id = f"_internal_{uuid.uuid4().hex[:16]}"
        with agent.session(client_id=self.client_id, session_id=internal_session_id) as conv:
            # Inject parent session context into conv for tool execution
            conv._parent_session_id = self.session_id
            conv._parent_client_id = self.client_id
            response = conv.chat(task)

        return response

    async def forget(
        self, about: str, reason: str = None, scope: str = "session"
    ) -> Dict[str, Any]:
        """
        [Function: forget]
        ==================
        - Input: about (str), reason (str|None), scope (str)
        - Output: dict - {"affected": {"messages": N, "profile_items": 0}}
        - Role in Flow: Semantic deletion using internal agent
        - Logic:
            1. Validate cloud mode
            2. Create internal agent with CRUD tools
            3. Execute deletion task
            4. Parse and return affected counts

        Args:
            about: Topic to forget
            reason: Reason for forgetting
            scope: "session" or "profile" or "both"

        Returns:
            {"affected": {"messages": 1, "profile_items": 0}}

        Example:
            result = await ctx.forget(
                about="personal email",
                reason="User privacy request"
            )
            print(f"Deleted {result['affected']['messages']} messages")
        """
        self._require_cloud()

        import poping

        tool_ids = self._get_context_tool_ids()
        agent = (
            poping.agent(llm="claude-haiku-4-5-20251001")
            .with_tools(cloud=tool_ids)
            .build(name=f"_forget_agent_{self.session_id[:8]}")
        )

        reason_text = f"\nReason: {reason}" if reason else ""
        task = f"""Delete messages about: "{about}"{reason_text}
Scope: {scope}

Instructions:
1. Use context_list_all to find messages about "{about}"
2. Delete relevant messages using context_delete
3. Return JSON with count of deleted messages

Output JSON format:
{{
    "affected": {{"messages": N, "profile_items": 0}}
}}"""

        # Internal agent uses unique session to avoid polluting parent history
        internal_session_id = f"_internal_{uuid.uuid4().hex[:16]}"
        with agent.session(client_id=self.client_id, session_id=internal_session_id) as conv:
            # Inject parent session context into conv for tool execution
            conv._parent_session_id = self.session_id
            conv._parent_client_id = self.client_id
            response = conv.chat(task)

        return response

    def pin(self, instruction: str) -> Dict[str, Any]:
        """
        Pin high-priority instruction

        Args:
            instruction: Instruction to pin

        Returns:
            {"pinned": True, "instruction": "..."}

        Example:
            ctx.pin("User is non-technical. Explain simply.")

        TODO: Implement backend API call
        """
        raise NotImplementedError("pin() will be implemented in next phase")

    def unpin(self) -> None:
        """
        Remove pinned instruction

        Example:
            ctx.unpin()

        TODO: Implement backend API call
        """
        raise NotImplementedError("unpin() will be implemented in next phase")

    async def assemble(
        self, user_message: str, include_profiles: bool = True
    ) -> List[Dict[str, str]]:
        """
        Assemble full context for conversation

        Args:
            user_message: User message to append
            include_profiles: Include profile memory

        Returns:
            Anthropic-compatible message array

        Example:
            messages = await ctx.assemble("How to deploy?")

        TODO: Implement backend API call
        """
        raise NotImplementedError("assemble() will be implemented in next phase")
