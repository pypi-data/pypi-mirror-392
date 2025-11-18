"""
Frontend Bridge and Tool Factory for executing tools on the user's frontend.

This module enables the pattern: agent loop on backend, tool execution on frontend.

High-level usage:
    from poping import FrontendToolFactory, start_frontend_bridge

    # 1) Start bridge (WebSocket server) in background
    bridge, loop, thread = start_frontend_bridge(host="127.0.0.1", port=8765)

    # 2) Create forwarding tools (schemas + names live in backend)
    factory = FrontendToolFactory(bridge)
    ui_alert = factory.make_tool(
        name="ui.alert",
        schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "severity": {"type": "string", "enum": ["info", "warn", "error"], "default": "info"},
            },
            "required": ["message"],
        },
        description="Show an alert in the user interface.",
    )

    # 3) Build agent with these local tools (real poping agent on backend)
    agent = poping.agent(llm="claude-3-5-sonnet-20241022").with_tools(local=[ui_alert]).build(name="assistant")

    # 4) Bind session before using the tools
    with agent.session(client_id="user_1", session_id="sess_demo") as conv:
        factory.set_session("sess_demo")
        print(conv.chat("Please show 'Hello' as an alert"))

On the frontend, register handlers with a small browser SDK that understands the
tool_request/tool_result protocol. See frontend_exec/sdk for a reference.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, Tuple, Callable

try:
    # Optional dependency; only needed when starting the bridge
    from websockets.server import WebSocketServerProtocol  # type: ignore
    import websockets  # type: ignore
except Exception:  # pragma: no cover - defer import errors until use
    WebSocketServerProtocol = object  # type: ignore
    websockets = None  # type: ignore

from .tool import tool


class FrontendBridge:
    """
    Minimal WebSocket bridge for routing backend tool calls to the user's browser.

    Protocol (JSON):
      Frontend → Backend (on connect):
        { "type": "register", "session_id": "sess_123", "tools": [{ name, description?, input_schema? }] }

      Backend → Frontend (execute a tool):
        { "type": "tool_request", "request_id": "rpc_...", "tool_name": "ui.alert", "parameters": { ... } }

      Frontend → Backend (tool result):
        { "type": "tool_result", "request_id": "rpc_...", "success": true, "result": { ... }, "error"?: { ... } }
    """

    def __init__(self) -> None:
        self._clients: Dict[str, WebSocketServerProtocol] = {}
        self._tool_catalog: Dict[str, Dict[str, Any]] = {}
        self._pending: Dict[str, asyncio.Future] = {}
        self._server = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self, host: str = "127.0.0.1", port: int = 8765):
        if websockets is None:
            raise RuntimeError(
                "websockets package is required to start the frontend bridge. Install with: pip install websockets"
            )

        async def handler(ws: WebSocketServerProtocol, path: str = "/"):
            session_id: Optional[str] = None
            try:
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue
                    mtype = msg.get("type")
                    if mtype == "register":
                        session_id = str(msg.get("session_id") or "default")
                        self._clients[session_id] = ws
                        tools = msg.get("tools") or []
                        self._tool_catalog[session_id] = {t.get("name"): t for t in tools if t and t.get("name")}
                        await ws.send(json.dumps({"type": "registered", "session_id": session_id}))
                    elif mtype == "tool_result":
                        req_id = msg.get("request_id")
                        fut = self._pending.pop(req_id, None)
                        if fut and not fut.done():
                            fut.set_result(msg)
            finally:
                if session_id and self._clients.get(session_id) is ws:
                    self._clients.pop(session_id, None)
                    self._tool_catalog.pop(session_id, None)

        self._loop = asyncio.get_running_loop()
        self._server = await websockets.serve(handler, host=host, port=port)
        return self._server

    async def wait_for_session(self, session_id: str, timeout: float = 30.0):
        end = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < end:
            if session_id in self._clients:
                return
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Frontend not connected for session_id={session_id}")

    async def send_tool_request(self, session_id: str, tool_name: str, parameters: Dict[str, Any], timeout_ms: int = 30000) -> Dict[str, Any]:
        ws = self._clients.get(session_id)
        if not ws:
            raise RuntimeError(f"No frontend connected for session_id={session_id}")
        request_id = f"rpc_{uuid.uuid4().hex[:8]}"
        fut = asyncio.get_event_loop().create_future()
        self._pending[request_id] = fut
        payload = {
            "type": "tool_request",
            "request_id": request_id,
            "tool_name": tool_name,
            "parameters": parameters,
        }
        await ws.send(json.dumps(payload))
        try:
            result: Dict[str, Any] = await asyncio.wait_for(fut, timeout=timeout_ms / 1000)
            return result
        finally:
            self._pending.pop(request_id, None)

    def send_tool_request_blocking(self, session_id: str, tool_name: str, parameters: Dict[str, Any], timeout_ms: int = 30000) -> Dict[str, Any]:
        if not self._loop:
            raise RuntimeError("Bridge loop not initialized. Call start() in an event loop first.")
        fut = asyncio.run_coroutine_threadsafe(
            self.send_tool_request(session_id=session_id, tool_name=tool_name, parameters=parameters, timeout_ms=timeout_ms),
            self._loop,
        )
        return fut.result(timeout=timeout_ms / 1000 + 5)


def start_frontend_bridge(host: str = "127.0.0.1", port: int = 8765) -> Tuple[FrontendBridge, asyncio.AbstractEventLoop, Any]:
    """
    Convenience: Start a FrontendBridge in a background thread.

    Returns: (bridge, loop, thread)
    """
    bridge = FrontendBridge()

    loop = asyncio.new_event_loop()

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bridge.start(host=host, port=port))
        loop.run_forever()

    import threading

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return bridge, loop, t


class FrontendToolFactory:
    """
    Factory that creates @tool-decorated callables which forward execution to the frontend via a FrontendBridge.
    """

    def __init__(self, bridge: FrontendBridge) -> None:
        self._bridge = bridge
        self._session_id: Optional[str] = None

    def set_session(self, session_id: str) -> None:
        self._session_id = session_id

    def _call_frontend(self, tool_name: str, params: Dict[str, Any]) -> Any:
        if not self._session_id:
            raise RuntimeError(
                "FrontendToolFactory has no session bound. Call set_session(session_id) before tool execution."
            )
        msg = self._bridge.send_tool_request_blocking(
            session_id=self._session_id,
            tool_name=tool_name,
            parameters=params,
            timeout_ms=30000,
        )
        if msg.get("success"):
            res = msg.get("result", {})
            # Prefer returning the full tool result so the agent can see
            # structured data (e.g., canvas_state, canvas_preview).
            # Backwards-compat: if result is a dict with only a 'message'
            # field, return that message as before.
            if isinstance(res, dict) and set(res.keys()) <= {"message"}:
                return res.get("message") or f"Executed {tool_name}"
            return res
        else:
            err = msg.get("error", {}).get("message", "frontend tool failed")
            return f"{tool_name} failed: {err}"

    def make_tool(self, name: str, schema: Dict[str, Any], description: Optional[str] = None) -> Callable:
        """
        Create an @tool-decorated callable that forwards to the frontend.

        The function signature accepts **kwargs based on schema properties.
        """

        @tool(name=name, schema=schema)
        def _forwarder(**kwargs) -> Any:  # type: ignore[misc]
            return self._call_frontend(name, kwargs)

        if description:
            _forwarder.__doc__ = description
        else:
            _forwarder.__doc__ = f"Forward execution of {name} to frontend via FrontendBridge."

        return _forwarder
