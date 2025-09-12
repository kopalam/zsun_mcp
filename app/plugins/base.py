"""Base plugin class for FastMCP API service framework."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Union, Optional

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """Base class for all plugins in the FastMCP API service framework."""

    def __init__(self, name: str):
        """Initialize the plugin with a name."""
        self.name = name

    @abstractmethod
    def tools(self) -> List[Callable]:
        """Return a list of tool functions to register with MCP.
        
        Returns:
            List of callable functions that will be registered as MCP tools.
        """
        pass

    def json_ok(self, data: Any) -> Dict[str, Any]:
        """Create a successful JSON response (legacy format for backward compatibility).
        
        Args:
            data: The data to return in the response.
            
        Returns:
            Dictionary with success status and data.
        """
        return {
            "status": "success",
            "data": data
        }

    def json_err(self, code: str, message: str, detail: Any = None) -> Dict[str, Any]:
        """Create an error JSON response (legacy format for backward compatibility).
        
        Args:
            code: Error code identifier.
            message: Human-readable error message.
            detail: Optional additional error details.
            
        Returns:
            Dictionary with error status and details.
        """
        error_response = {
            "status": "error",
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if detail is not None:
            error_response["error"]["detail"] = detail
            
        return error_response

    def jsonrpc_ok(self, data: Any, request_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """Create a successful JSON-RPC 2.0 response.
        
        Args:
            data: The data to return in the response.
            request_id: Optional request ID for matching requests.
            
        Returns:
            Dictionary with JSON-RPC 2.0 success response format.
        """
        from utils.jsonrpc import JSONRPCProtocol
        response = JSONRPCProtocol.create_success_response(data, request_id)
        return JSONRPCProtocol.to_dict(response)

    def jsonrpc_err(self, error_code: int, error_message: str, 
                   error_data: Any = None, request_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """Create an error JSON-RPC 2.0 response.
        
        Args:
            error_code: JSON-RPC error code.
            error_message: Human-readable error message.
            error_data: Optional additional error details.
            request_id: Optional request ID for matching requests.
            
        Returns:
            Dictionary with JSON-RPC 2.0 error response format.
        """
        from utils.jsonrpc import JSONRPCProtocol
        response = JSONRPCProtocol.create_error_response(
            error_code, error_message, error_data, request_id
        )
        return JSONRPCProtocol.to_dict(response)
