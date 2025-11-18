"""
Heartbeat manager for health monitoring (SAP-044).
"""

import asyncio
from typing import Optional
from .client import ManifestClient

class HeartbeatManager:
    """Manages periodic heartbeat to manifest registry."""

    def __init__(self, client: ManifestClient, service_id: str, interval: int = 30):
        self.client = client
        self.service_id = service_id
        self.interval = interval
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start heartbeat task."""
        self._task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self):
        """Stop heartbeat task."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while True:
            try:
                await self.client.heartbeat(self.service_id)
                await asyncio.sleep(self.interval)
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(self.interval)
