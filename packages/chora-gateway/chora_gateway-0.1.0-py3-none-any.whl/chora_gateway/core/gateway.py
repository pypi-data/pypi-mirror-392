"""
Gateway core capability: Unified tool aggregation and request routing.
"""

from typing import Dict, List, Optional
import asyncio
from pydantic import BaseModel


class ServerConnection(BaseModel):
    """MCP server connection configuration."""
    name: str
    url: str
    protocol: str  # "stdio", "sse", "http"
    status: str = "unknown"  # "connected", "disconnected", "error"
    tools: List[Dict] = []


class ToolRequest(BaseModel):
    """Tool invocation request."""
    tool_name: str
    server_name: Optional[str] = None  # If None, auto-route
    arguments: Dict = {}


class ToolResponse(BaseModel):
    """Tool invocation response."""
    tool_name: str
    server_name: str
    result: Dict
    success: bool
    error: Optional[str] = None


class Gateway:
    """
    Gateway capability for unified tool aggregation and request routing.

    Features:
    - Service discovery via chora-manifest
    - Tool aggregation across multiple MCP servers
    - Intelligent request routing
    - Load balancing and failover
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.servers: Dict[str, ServerConnection] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize gateway and discover services."""
        if self._initialized:
            return

        # TODO: Connect to chora-manifest for service discovery
        # TODO: Establish connections to available MCP servers
        # TODO: Aggregate tool catalogs

        self._initialized = True
        print("✓ Gateway initialized")

    async def register_server(self, server: ServerConnection):
        """Register an MCP server with the gateway."""
        self.servers[server.name] = server
        print(f"✓ Registered server: {server.name}")

    async def discover_tools(self) -> List[Dict]:
        """Discover all available tools across all servers."""
        all_tools = []
        for server_name, server in self.servers.items():
            # TODO: Query each server for its tool catalog
            # TODO: Aggregate and deduplicate tools
            all_tools.extend(server.tools)

        return all_tools

    async def route_request(self, request: ToolRequest) -> ToolResponse:
        """
        Route a tool request to the appropriate MCP server.

        Routing strategy:
        1. If server_name specified, route directly
        2. Otherwise, find server that provides the tool
        3. Apply load balancing if multiple servers provide tool
        4. Handle failover if primary server unavailable
        """
        if request.server_name:
            # Direct routing
            server = self.servers.get(request.server_name)
            if not server:
                return ToolResponse(
                    tool_name=request.tool_name,
                    server_name=request.server_name,
                    result={},
                    success=False,
                    error=f"Server not found: {request.server_name}"
                )
        else:
            # Auto-routing: find server that provides this tool
            server = self._find_server_for_tool(request.tool_name)
            if not server:
                return ToolResponse(
                    tool_name=request.tool_name,
                    server_name="unknown",
                    result={},
                    success=False,
                    error=f"No server found for tool: {request.tool_name}"
                )

        # TODO: Execute tool on selected server
        # TODO: Handle errors and retries
        # TODO: Return response

        return ToolResponse(
            tool_name=request.tool_name,
            server_name=server.name,
            result={"status": "not_implemented"},
            success=False,
            error="Tool execution not yet implemented"
        )

    def _find_server_for_tool(self, tool_name: str) -> Optional[ServerConnection]:
        """Find a server that provides the requested tool."""
        for server in self.servers.values():
            if server.status != "connected":
                continue

            for tool in server.tools:
                if tool.get("name") == tool_name:
                    return server

        return None

    async def health_check(self) -> Dict:
        """Check health of gateway and all connected servers."""
        healthy_servers = sum(
            1 for s in self.servers.values() if s.status == "connected"
        )

        return {
            "gateway_status": "healthy" if self._initialized else "not_initialized",
            "total_servers": len(self.servers),
            "connected_servers": healthy_servers,
            "total_tools": sum(len(s.tools) for s in self.servers.values())
        }

    async def shutdown(self):
        """Gracefully shutdown gateway and disconnect all servers."""
        # TODO: Disconnect from all servers
        # TODO: Clean up resources

        self._initialized = False
        print("✓ Gateway shutdown")
