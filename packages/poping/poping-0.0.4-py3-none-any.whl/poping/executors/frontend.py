"""
[FrontendExecutor]
==================
Purpose: Execute canvas atoms in frontend browser via WebSocket RPC
Data Flow: execute() -> WebSocket -> Frontend AtomExecutor -> Response -> return
Core Data Structures:
- canvas_atoms: Set[str] - Tool names routed to frontend
- ws_manager: WebSocketManager - Connection manager from backend
- session_id: str - WebSocket session identifier

Main Functions:
1. supports() -> Check if tool is canvas atom
2. execute() -> Send RPC request, wait for response

Related Files:
    @/backend/websocket/manager.py -> WebSocket connection and RPC management
    @/frontend/AtomExecutor.ts -> Browser-side atom execution
"""

from typing import Any, Dict, Set, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class FrontendExecutor:
    """Execute canvas atoms in frontend browser via WebSocket RPC"""

    def __init__(self, ws_manager, session_id: str, canvas_atoms: Optional[Set[str]] = None):
        """
        Initialize FrontendExecutor
        
        Args:
            ws_manager: WebSocketManager from backend
            session_id: WebSocket connection identifier
            canvas_atoms: Set of atom names (defaults to all 11 canvas atoms)
        """
        self.ws_manager = ws_manager
        self.session_id = session_id
        self.canvas_atoms = canvas_atoms or {
            "set_view", "add_layer", "update_layer", "update_element",
            "add_element", "copy_layer", "copy_element", "delete_element",
            "delete_layer", "generate", "export", "finish"
        }

    def supports(self, tool_name: str) -> bool:
        """Check if tool is canvas atom"""
        return tool_name in self.canvas_atoms

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute tool in frontend via WebSocket
        
        Args:
            tool_name: Canvas atom type
            arguments: Atom parameters
            
        Returns:
            Execution result message
            
        Raises:
            TimeoutError: Frontend doesn't respond within 30s
            RuntimeError: Frontend returns error
        """
        logger.debug(f"Executing frontend tool: {tool_name}")

        try:
            response = await self.ws_manager.send_tool_request(
                session_id=self.session_id,
                tool_name=tool_name,
                parameters=arguments,
                timeout_ms=30000
            )

            if response.get("success"):
                result = response.get("result", {})
                message = result.get("message", f"Executed {tool_name}")
                logger.debug(f"Frontend tool success: {message}")
                return message
            else:
                error = response.get("error", {})
                error_msg = error.get("message", "Unknown error")
                logger.error(f"Frontend tool failed: {error_msg}")
                raise RuntimeError(f"Frontend execution failed: {error_msg}")

        except asyncio.TimeoutError:
            logger.error(f"Frontend tool timeout: {tool_name}")
            raise TimeoutError(f"Frontend did not respond within 30s for {tool_name}")

        except Exception as e:
            logger.error(f"Frontend tool error: {str(e)}")
            raise
