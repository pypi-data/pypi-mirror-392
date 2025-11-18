"""
chora-orchestration: Multi-MCP server orchestration and workflow management.

Multi-interface capability server supporting:
- Native API (Python library)
- CLI (command-line interface)
- HTTP REST API
- MCP server (AI agent integration)
"""

__version__ = "0.3.1"
__author__ = "Liminal Commons"
__license__ = "MIT"

# Export main classes for native API usage
from chora_orchestration.core.capability import BaseCapability
from chora_orchestration.core.orchestrator import DockerOrchestrator, ServerDefinition

__all__ = ["BaseCapability", "DockerOrchestrator", "ServerDefinition", "__version__"]
