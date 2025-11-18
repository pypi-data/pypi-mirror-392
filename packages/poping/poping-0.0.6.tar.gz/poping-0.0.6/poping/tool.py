"""
Poping Tool Decorator and Management
"""

from typing import Callable, Dict, Any, Optional, List
from functools import wraps
import inspect



def tool(
    name: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    network: bool = True,
    side_effects: bool = True
) -> Callable:
    """
    Decorator for local tools

    Args:
        name: Tool identifier (defaults to function name)
        schema: JSON schema for parameters
        network: Whether tool requires network access
        side_effects: Whether tool modifies external state

    Returns:
        Decorated function

    Example:
        @tool(
            name="calc.add",
            schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
        def add(a: float, b: float) -> float:
            return a + b
    """
    def decorator(func: Callable) -> Callable:
        # Generate schema from function signature if not provided
        tool_schema = schema or _generate_schema(func)

        # Attach metadata to function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_poping_tool = True
        wrapper._tool_name = name or func.__name__
        wrapper._tool_schema = tool_schema
        wrapper._tool_network = network
        wrapper._tool_side_effects = side_effects
        wrapper._original_func = func

        return wrapper

    return decorator


def _generate_schema(func: Callable) -> Dict[str, Any]:
    """
    Generate JSON schema from function signature

    Args:
        func: Function to analyze

    Returns:
        JSON schema for function parameters
    """
    sig = inspect.signature(func)
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        # Get type annotation
        param_type = "string"  # Default
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == list or str(param.annotation).startswith("List"):
                param_type = "array"
            elif param.annotation == dict or str(param.annotation).startswith("Dict"):
                param_type = "object"

        properties[param_name] = {"type": param_type}

        # Check if required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    schema = {
        "type": "object",
        "properties": properties
    }

    if required:
        schema["required"] = required

    return schema


def get_tool_metadata(func: Callable) -> Optional[Dict[str, Any]]:
    """
    Get tool metadata from decorated function

    Args:
        func: Function to check

    Returns:
        Tool metadata if decorated, None otherwise
    """
    if not hasattr(func, "_is_poping_tool"):
        return None

    return {
        "name": func._tool_name,
        "schema": func._tool_schema,
        "network": func._tool_network,
        "side_effects": func._tool_side_effects
    }


class ToolRegistry:
    """
    Registry for local and cloud tools

    Manages tool availability and execution
    """

    def __init__(self):
        """
        Initialize tool registry

        Args:
            None
        """
        self.local_tools: Dict[str, Callable] = {}
        self.cloud_tools: List[str] = []
        self.subagent_tools: Dict[str, Dict[str, Any]] = {}

    def register_local(self, func: Callable) -> None:
        """
        Register a local tool

        Args:
            func: Function decorated with @tool
        """
        metadata = get_tool_metadata(func)
        if not metadata:
            raise ValueError(f"Function {func.__name__} is not decorated with @tool")

        self.local_tools[metadata["name"]] = func

    def register_cloud(self, tool_ids: List[str]) -> None:
        """
        Register cloud tool IDs (schemas managed by backend)
        
        Args:
            tool_ids: List of cloud tool IDs (e.g., "oplus.text_to_image")
        """
        self.cloud_tools.extend(tool_ids)

    def register_subagent(self, tool_schema: Dict[str, Any]) -> None:
        """
        Register a subagent tool schema

        Args:
            tool_schema: Complete tool schema with _is_subagent and _subagent_config
        """
        tool_name = tool_schema["name"]
        self.subagent_tools[tool_name] = tool_schema

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool (local or cloud)

        Args:
            tool_name: Tool name/ID
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Check if local tool
        if tool_name in self.local_tools:
            func = self.local_tools[tool_name]
            return func._original_func(**arguments)

        # Check if cloud tool
        if tool_name in self.cloud_tools:
            # Cloud tool execution is routed via Session._execute_tools()
            # ToolRegistry no longer executes cloud tools directly.
            raise RuntimeError(
                "Cloud tool execution is handled by the Session; "
                "ToolRegistry.execute() supports only local tools."
            )

        raise ValueError(f"Tool not found: {tool_name}")

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available tools

        Returns:
            Dict with 'local' and 'cloud' tool lists
        """
        local_info = []
        for name, func in self.local_tools.items():
            metadata = get_tool_metadata(func)
            local_info.append({
                "name": name,
                "schema": metadata["schema"],
                "network": metadata["network"],
                "side_effects": metadata["side_effects"],
                "source": "local"
            })

        cloud_info = [{"name": tool_id, "source": "cloud"} for tool_id in self.cloud_tools]

        return {
            "local": local_info,
            "cloud": cloud_info
        }

    def to_anthropic_schema(self) -> List[Dict[str, Any]]:
        """
        Convert local tools to Anthropic tool schema

        Returns:
            List of local tool schemas for Anthropic API
        """
        schemas = []

        # Local tools
        for name, func in self.local_tools.items():
            metadata = get_tool_metadata(func)
            schema = {
                "name": name,
                "description": func.__doc__ or f"Execute {name}",
                "input_schema": metadata["schema"]
            }
            schemas.append(schema)

        # Subagent tools (treated as local for schema exposure)
        for tool_schema in self.subagent_tools.values():
            schemas.append(tool_schema)

        return schemas
