"""
Data models for gateway capability.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class ServiceManifest(BaseModel):
    """Service manifest from chora-manifest registry."""
    name: str
    version: str
    capabilities: List[str]
    endpoints: Dict[str, str]
    health_check_url: Optional[str] = None


class ToolDefinition(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict
    server_name: str  # Which server provides this tool


class RoutingStrategy(BaseModel):
    """Configuration for request routing."""
    strategy: Literal["round_robin", "least_connections", "random"] = "round_robin"
    enable_failover: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30


class GatewayConfig(BaseModel):
    """Gateway configuration."""
    manifest_url: str = "http://localhost:8080"
    routing: RoutingStrategy = Field(default_factory=RoutingStrategy)
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
