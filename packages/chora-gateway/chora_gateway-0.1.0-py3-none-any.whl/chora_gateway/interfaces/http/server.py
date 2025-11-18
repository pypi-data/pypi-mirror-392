"""
HTTP REST API interface for chora-gateway.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from ...core.gateway import Gateway, ToolRequest, ServerConnection

app = FastAPI(
    title="chora-gateway API",
    description="MCP Gateway for unified tool aggregation and request routing",
    version="0.1.0"
)

# Global gateway instance
gateway = Gateway()


@app.on_event("startup")
async def startup_event():
    """Initialize gateway on server startup."""
    await gateway.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown gateway gracefully."""
    await gateway.shutdown()


class ToolExecuteRequest(BaseModel):
    """Request to execute a tool."""
    tool_name: str
    server_name: Optional[str] = None
    arguments: Dict = {}


class ServerRegisterRequest(BaseModel):
    """Request to register a server."""
    name: str
    url: str
    protocol: str


@app.get("/api/v1/health")
async def health():
    """Health check endpoint."""
    return await gateway.health_check()


@app.get("/api/v1/tools")
async def list_tools():
    """List all available tools."""
    tools = await gateway.discover_tools()
    return {"tools": tools}


@app.post("/api/v1/tools/execute")
async def execute_tool(request: ToolExecuteRequest):
    """Execute a tool via the gateway."""
    tool_request = ToolRequest(
        tool_name=request.tool_name,
        server_name=request.server_name,
        arguments=request.arguments
    )

    response = await gateway.route_request(tool_request)

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)

    return {
        "tool_name": response.tool_name,
        "server_name": response.server_name,
        "result": response.result
    }


@app.post("/api/v1/servers/register")
async def register_server(request: ServerRegisterRequest):
    """Register an MCP server."""
    server = ServerConnection(
        name=request.name,
        url=request.url,
        protocol=request.protocol,
        status="connected"
    )

    await gateway.register_server(server)

    return {
        "status": "registered",
        "server_name": request.name
    }


@app.get("/api/v1/servers")
async def list_servers():
    """List all registered servers."""
    return {
        "servers": [
            {
                "name": name,
                "url": server.url,
                "protocol": server.protocol,
                "status": server.status,
                "tool_count": len(server.tools)
            }
            for name, server in gateway.servers.items()
        ]
    }


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run HTTP server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
