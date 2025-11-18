"""
Startup sequencing for orchestration service (SAP-045).
"""

import asyncio
from typing import Dict, Optional
from chora_orchestration.core.orchestrator import DockerOrchestrator
from chora_orchestration.registry.client import ManifestClient
from chora_orchestration.registry.heartbeat import HeartbeatManager

class StartupSequence:
    """Manages dependency-ordered initialization."""

    def __init__(self, config: Dict):
        self.config = config
        self.orchestrator: Optional[DockerOrchestrator] = None
        self.manifest_client: Optional[ManifestClient] = None
        self.heartbeat: Optional[HeartbeatManager] = None

    async def initialize(self):
        """Execute startup sequence in dependency order."""
        # Phase 1: Initialize core services
        registry_path = self.config.get("registry_path")
        self.orchestrator = DockerOrchestrator(registry_path=registry_path)
        await self.orchestrator.initialize()

        # Phase 2: Connect to manifest registry
        if self.config.get("enable_registry", True):
            self.manifest_client = ManifestClient(
                self.config.get("manifest_url", "http://localhost:8080")
            )

            # Phase 3: Register service
            manifest = {
                "name": "chora-orchestration",
                "version": "0.3.0",
                "capabilities": ["orchestration", "workflow"],
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

        print("✓ Startup sequence complete")

    async def shutdown(self):
        """Graceful shutdown in reverse dependency order."""
        if self.heartbeat:
            await self.heartbeat.stop()

        if self.manifest_client:
            await self.manifest_client.close()

        if self.orchestrator:
            await self.orchestrator.shutdown()

        print("✓ Shutdown complete")
