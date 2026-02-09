"""
MCP (Model Context Protocol) Server Implementation
This module implements the MCP server that exposes todo operations as tools for the OpenAI Agent.
"""

import asyncio
from typing import Dict, Any, Callable, Awaitable
from functools import wraps
import inspect


# Global registry for MCP tools
_mcp_tools_registry: Dict[str, Callable] = {}


def mcp_tool(name: str, description: str):
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: The name of the tool
        description: A description of what the tool does
    """
    def decorator(func: Callable) -> Callable:
        # Register the function in the global registry
        _mcp_tools_registry[name] = {
            'function': func,
            'description': description,
            'signature': inspect.signature(func)
        }
        return func
    return decorator


class MCPServer:
    """
    MCP Server class that manages the registered tools and handles tool execution.
    """
    
    def __init__(self):
        self.tools = _mcp_tools_registry.copy()
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """
        Get a registered tool by name.
        
        Args:
            name: The name of the tool
            
        Returns:
            Dictionary containing the tool function and metadata
        """
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """
        List all available tools with their descriptions.
        
        Returns:
            Dictionary mapping tool names to their descriptions
        """
        return {name: tool['description'] for name, tool in self.tools.items()}
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a registered tool with the provided arguments.
        
        Args:
            name: The name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        tool_info = self.get_tool(name)
        if not tool_info:
            return {
                "success": False,
                "error_code": "TOOL_NOT_FOUND",
                "message": f"Tool '{name}' not found"
            }
        
        # Get the function and its signature
        func = tool_info['function']
        sig = tool_info['signature']
        
        # Validate arguments against the function signature
        try:
            bound_args = sig.bind(**kwargs)
            bound_args.apply_defaults()
        except TypeError as e:
            return {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": f"Invalid arguments for tool '{name}': {str(e)}"
            }
        
        # Execute the function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(**bound_args.arguments)
            else:
                result = func(**bound_args.arguments)
            return result
        except Exception as e:
            return {
                "success": False,
                "error_code": "EXECUTION_ERROR",
                "message": f"Error executing tool '{name}': {str(e)}"
            }


# Create a global instance of the MCP server
mcp_server = MCPServer()


# Export the decorator and server instance
__all__ = ['mcp_tool', 'mcp_server', 'MCPServer']