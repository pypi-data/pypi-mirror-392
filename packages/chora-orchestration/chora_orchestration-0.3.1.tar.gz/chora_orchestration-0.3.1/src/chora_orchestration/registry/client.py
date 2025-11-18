"""
Registry client for chora-manifest integration (SAP-044).
"""

from typing import Dict, Optional
import httpx

class ManifestClient:
    """Client for chora-manifest registry."""

    def __init__(self, manifest_url: str = "http://localhost:8080"):
        self.manifest_url = manifest_url
        self.client = httpx.AsyncClient(base_url=manifest_url)

    async def register(self, manifest: Dict) -> Dict:
        """Register this service with manifest registry."""
        response = await self.client.post("/api/v1/register", json=manifest)
        response.raise_for_status()
        return response.json()

    async def heartbeat(self, service_id: str) -> Dict:
        """Send heartbeat to manifest registry."""
        response = await self.client.post(f"/api/v1/heartbeat/{service_id}")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
