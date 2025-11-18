"""
chora-gateway: MCP Gateway for unified tool aggregation and request routing.

Multi-interface capability server supporting:
- Native API (Python library)
- CLI (command-line interface)
- HTTP REST API
- MCP server (AI agent integration)
"""

__version__ = "0.1.0"
__author__ = "Liminal Commons"
__license__ = "MIT"

# Export main gateway class for native API usage
from chora_gateway.core.gateway import Gateway

__all__ = ["Gateway", "__version__"]
