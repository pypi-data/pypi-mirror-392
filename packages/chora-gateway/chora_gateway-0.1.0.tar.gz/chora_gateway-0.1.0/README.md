# chora-gateway

[![PyPI version](https://badge.fury.io/py/chora-gateway.svg)](https://pypi.org/project/chora-gateway/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP Gateway for unified tool aggregation and request routing across multiple MCP servers.

## Features

- **Tool Aggregation**: Discover and aggregate tools from multiple MCP servers
- **Request Routing**: Route MCP requests to appropriate backend servers
- **Service Discovery**: Integration with chora-manifest for automatic server discovery
- **Unified Endpoint**: Single MCP endpoint exposing all available tools
- **Health Monitoring**: Track health status of all registered MCP servers
- **Multi-Interface Support**: Native API, CLI, REST API, and MCP server modes

## Installation

### From PyPI (Recommended)

```bash
pip install chora-gateway
```

### From Source (Development)

```bash
git clone https://github.com/liminalcommons/chora-gateway.git
cd chora-gateway
poetry install
```

## Quick Start

### 1. Native API (Python Library)

```python
from chora_gateway import Gateway

# Initialize gateway with manifest integration
gateway = Gateway(manifest_url="http://localhost:8081")

# List all available tools
tools = gateway.list_tools()

# Route a tool invocation
result = gateway.invoke_tool("manifest.list_servers", {})
```

### 2. CLI (Command-Line Interface)

```bash
# Start gateway server
chora-gateway serve --port 8080

# List all aggregated tools
chora-gateway list-tools

# Check gateway health
chora-gateway health
```

### 3. REST API (HTTP Server)

```bash
# Start HTTP server
chora-gateway serve --mode http --port 8080

# Query tools via HTTP
curl http://localhost:8080/tools

# Invoke tool via HTTP
curl -X POST http://localhost:8080/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "manifest.list_servers", "arguments": {}}'
```

### 4. MCP Server (AI Agent Integration)

```bash
# Start MCP stdio server (for Cline, Claude Desktop)
chora-gateway serve --mode mcp-stdio

# Or start MCP HTTP server
chora-gateway serve --mode mcp-http --port 8080
```

## Architecture

```
┌─────────────────────────────────────────────┐
│          AI Client (Claude, Cline)          │
└──────────────────┬──────────────────────────┘
                   │ MCP Protocol
         ┌─────────▼──────────┐
         │   chora-gateway    │
         │   (Unified MCP)    │
         └────────┬───────────┘
                  │
      ┌───────────┼────────────┐
      │           │            │
  ┌───▼───┐   ┌──▼───┐    ┌──▼─────┐
  │Manifest│   │ n8n  │    │ GitHub │
  │Server  │   │Server│    │ Server │
  └────────┘   └──────┘    └────────┘
```

## Configuration

The gateway can be configured via:

1. **Environment variables**: `CHORA_GATEWAY_*`
2. **Configuration file**: `~/.chora/gateway.yaml`
3. **CLI arguments**: `--manifest-url`, `--port`, etc.

Example configuration file:

```yaml
# ~/.chora/gateway.yaml
manifest_url: http://localhost:8081
port: 8080
log_level: INFO
health_check_interval: 30
```

## Documentation

- [Full Documentation](docs/README.md)
- [Architecture](docs/architecture/)
- [How-To Guides](docs/user-docs/how-to/)
- [API Reference](docs/user-docs/reference/)
- [Contributing](docs/dev-docs/contributing.md)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/liminalcommons/chora-gateway.git
cd chora-gateway

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov
```

### Running Locally

```bash
# Start gateway server (requires manifest server running)
poetry run chora-gateway serve --port 8080
```

## Contributing

See [CONTRIBUTING.md](docs/dev-docs/contributing.md) for contribution guidelines.

## License

MIT

## Related Projects

- [chora-manifest](https://github.com/liminalcommons/chora-manifest) - MCP server registry and discovery
- [chora-orchestration](https://github.com/liminalcommons/chora-orchestration) - Docker orchestration for MCP servers
- [chora-base](https://github.com/liminalcommons/chora-base) - Shared adoption patterns (SAPs)
