"""
CLI interface for chora-gateway.
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from ...core.gateway import Gateway, ToolRequest, ServerConnection

console = Console()


@click.group()
@click.version_option()
def main():
    """chora-gateway: MCP Gateway for unified tool aggregation and request routing."""
    pass


@main.command()
def discover():
    """Discover all available tools across connected servers."""
    gateway = Gateway()

    async def _discover():
        await gateway.initialize()
        tools = await gateway.discover_tools()

        table = Table(title="Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Server", style="magenta")
        table.add_column("Description", style="green")

        for tool in tools:
            table.add_row(
                tool.get("name", ""),
                tool.get("server_name", ""),
                tool.get("description", "")
            )

        console.print(table)

    asyncio.run(_discover())


@main.command()
@click.option("--name", required=True, help="Server name")
@click.option("--url", required=True, help="Server URL")
@click.option("--protocol", default="stdio", help="Protocol (stdio, sse, http)")
def register(name: str, url: str, protocol: str):
    """Register an MCP server with the gateway."""
    gateway = Gateway()

    async def _register():
        await gateway.initialize()
        server = ServerConnection(
            name=name,
            url=url,
            protocol=protocol,
            status="connected"
        )
        await gateway.register_server(server)
        console.print(f"[green]✓[/green] Server registered: {name}")

    asyncio.run(_register())


@main.command()
@click.option("--tool", required=True, help="Tool name")
@click.option("--server", help="Server name (optional, auto-route if not specified)")
@click.option("--args", help="Tool arguments (JSON)")
def execute(tool: str, server: str, args: str):
    """Execute a tool via the gateway."""
    import json

    gateway = Gateway()
    arguments = json.loads(args) if args else {}

    async def _execute():
        await gateway.initialize()
        request = ToolRequest(
            tool_name=tool,
            server_name=server,
            arguments=arguments
        )
        response = await gateway.route_request(request)

        if response.success:
            console.print(f"[green]✓[/green] Tool executed successfully")
            console.print(f"Server: {response.server_name}")
            console.print(f"Result: {response.result}")
        else:
            console.print(f"[red]✗[/red] Tool execution failed")
            console.print(f"Error: {response.error}")

    asyncio.run(_execute())


@main.command()
@click.option("--mode", type=click.Choice(["http", "mcp-stdio", "mcp-sse"]), default="http")
@click.option("--port", default=8080, help="Port for HTTP/SSE mode")
def serve(mode: str, port: int):
    """Start gateway server."""
    if mode == "http":
        console.print(f"[cyan]Starting HTTP server on port {port}...[/cyan]")
        # TODO: Start FastAPI HTTP server
    elif mode == "mcp-stdio":
        console.print("[cyan]Starting MCP server (stdio mode)...[/cyan]")
        # TODO: Start MCP stdio server
    elif mode == "mcp-sse":
        console.print(f"[cyan]Starting MCP server (SSE mode) on port {port}...[/cyan]")
        # TODO: Start MCP SSE server
    else:
        console.print(f"[red]Unknown mode: {mode}[/red]")


@main.command()
def health():
    """Check gateway health."""
    gateway = Gateway()

    async def _health():
        await gateway.initialize()
        status = await gateway.health_check()

        console.print("\n[bold]Gateway Health Status[/bold]")
        console.print(f"Status: [green]{status['gateway_status']}[/green]")
        console.print(f"Total Servers: {status['total_servers']}")
        console.print(f"Connected Servers: {status['connected_servers']}")
        console.print(f"Total Tools: {status['total_tools']}\n")

    asyncio.run(_health())


if __name__ == "__main__":
    main()
