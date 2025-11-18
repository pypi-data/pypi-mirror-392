"""
Base capability interface (SAP-047).

All capability servers must inherit from BaseCapability and implement
the standardized interface for execute, health_check, initialize, and shutdown.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseCapability(ABC):
    """
    Base capability interface for all chora capability servers.

    This abstract class defines the standard interface that all
    capability servers must implement to ensure consistent behavior
    across the ecosystem.
    """

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the core capability.

        Args:
            input_data: Input data for the capability execution.
                       Format depends on the specific capability.

        Returns:
            Dict containing the execution result.

        Raises:
            Exception: If execution fails.
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, str]:
        """
        Check the health status of the capability.

        Returns:
            Dict with status and additional health information.
            Example: {"status": "healthy", "details": "..."}
        """
        pass

    @abstractmethod
    async def initialize(self):
        """
        Initialize capability resources.

        This method is called during startup to prepare the capability
        for operation. It should set up any required connections,
        load configuration, and prepare resources.

        Raises:
            Exception: If initialization fails.
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """
        Cleanup capability resources.

        This method is called during graceful shutdown to release
        resources, close connections, and perform cleanup.
        Should not raise exceptions.
        """
        pass
