"""
Startup sequencing for gateway service (SAP-045).
"""

import asyncio
from typing import Dict, Optional
from ..core.gateway import Gateway
from ..registry.client import ManifestClient
from ..registry.heartbeat import HeartbeatManager


class StartupSequence:
    """Manages dependency-ordered initialization."""

    def __init__(self, config: Dict):
        self.config = config
        self.gateway: Optional[Gateway] = None
        self.manifest_client: Optional[ManifestClient] = None
        self.heartbeat: Optional[HeartbeatManager] = None

    async def initialize(self):
        """Execute startup sequence in dependency order."""
        # Phase 1: Initialize core gateway
        self.gateway = Gateway(self.config)
        await self.gateway.initialize()

        # Phase 2: Connect to manifest registry
        if self.config.get("enable_registry", True):
            self.manifest_client = ManifestClient(
                self.config.get("manifest_url", "http://localhost:8080")
            )

            # Phase 3: Register gateway service
            manifest = {
                "name": "chora-gateway",
                "version": "0.1.0",
                "capabilities": ["gateway", "routing", "aggregation"],
                "endpoints": {
                    "http": self.config.get("http_port", 8080),
                    "mcp": self.config.get("mcp_mode", "stdio")
                }
            }
            response = await self.manifest_client.register(manifest)
            service_id = response["service_id"]

            # Phase 4: Start heartbeat
            self.heartbeat = HeartbeatManager(
                self.manifest_client,
                service_id,
                interval=self.config.get("heartbeat_interval", 30)
            )
            await self.heartbeat.start()

            # Phase 5: Discover available services
            services = await self.manifest_client.discover_services()
            print(f"✓ Discovered {len(services)} services")

        print("✓ Startup sequence complete")

    async def shutdown(self):
        """Graceful shutdown in reverse dependency order."""
        if self.heartbeat:
            await self.heartbeat.stop()

        if self.manifest_client:
            await self.manifest_client.close()

        if self.gateway:
            await self.gateway.shutdown()

        print("✓ Shutdown complete")
