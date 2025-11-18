"""
Custom exceptions for gateway capability.
"""


class GatewayError(Exception):
    """Base exception for gateway errors."""
    pass


class ServerNotFoundError(GatewayError):
    """Requested server not found in registry."""
    pass


class ToolNotFoundError(GatewayError):
    """Requested tool not available on any server."""
    pass


class RoutingError(GatewayError):
    """Error during request routing."""
    pass


class ServerConnectionError(GatewayError):
    """Error connecting to MCP server."""
    pass
