"""Exceptions for MCP client."""


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class MCPConnectionError(MCPClientError):
    """Exception raised when connection to MCP server fails."""
    pass


class MCPAuthenticationError(MCPClientError):
    """Exception raised when authentication fails."""
    pass


class MCPRequestError(MCPClientError):
    """Exception raised when a request to MCP server fails."""
    pass


class MCPConfigError(MCPClientError):
    """Exception raised when configuration is invalid."""
    pass 