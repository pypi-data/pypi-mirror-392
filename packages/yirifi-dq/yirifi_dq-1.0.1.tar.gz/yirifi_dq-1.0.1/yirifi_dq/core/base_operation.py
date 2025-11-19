"""
Base Operation Abstract Class

For custom operations that don't fit validator/fixer/analyzer patterns.
Use this for complex multi-step workflows requiring custom orchestration.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from yirifi_dq.models.operation import OperationConfig, OperationResult
from yirifi_dq.utils.logging_config import get_logger


class BaseOperation(ABC):
    """
    Abstract base class for custom operations.

    Example Usage:
        class DataMigrationOperation(BaseOperation):
            def execute(self, config: OperationConfig) -> OperationResult:
                # Custom multi-step migration logic
                pass

            def verify(self, operation_id: str) -> bool:
                # Verification logic
                pass

            def rollback(self, operation_id: str) -> bool:
                # Rollback logic
                pass

    Use Cases:
    - Multi-collection migrations
    - Complex data transformations
    - Cross-database operations
    - Custom workflows with multiple steps
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize custom operation.

        Args:
            logger: Optional custom logger
        """
        self.logger = logger or get_logger(self.__class__.__name__)
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    @property
    def name(self) -> str:
        """Operation name (class name by default)."""
        return self.__class__.__name__

    @property
    @abstractmethod
    def is_destructive(self) -> bool:
        """
        Whether this operation modifies/deletes data.

        Returns:
            True if operation is destructive, False otherwise
        """
        pass

    @property
    @abstractmethod
    def requires_backup(self) -> bool:
        """
        Whether this operation requires backup before execution.

        Returns:
            True if backup is required, False otherwise
        """
        pass

    @abstractmethod
    def execute(self, config: OperationConfig) -> OperationResult:
        """
        Execute custom operation.

        Args:
            config: Operation configuration

        Returns:
            OperationResult with execution details

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def verify(self, operation_id: str) -> bool:
        """
        Verify operation succeeded.

        Args:
            operation_id: Operation ID to verify

        Returns:
            True if verification passed, False otherwise
        """
        pass

    @abstractmethod
    def rollback(self, operation_id: str) -> bool:
        """
        Rollback operation if failed.

        Args:
            operation_id: Operation ID to rollback

        Returns:
            True if rollback succeeded, False otherwise
        """
        pass

    def _start_timer(self):
        """Start execution timer."""
        self._start_time = datetime.utcnow()

    def _end_timer(self) -> float:
        """End execution timer and return elapsed seconds."""
        self._end_time = datetime.utcnow()
        if self._start_time:
            return (self._end_time - self._start_time).total_seconds()
        return 0.0

    def _log_operation_start(self, config: OperationConfig):
        """Log operation start."""
        self.logger.info(f"Starting {self.name} operation (database: {config.database}, collection: {config.collection})")

    def _log_operation_end(self, success: bool, execution_time: float):
        """Log operation completion."""
        status = "completed successfully" if success else "failed"
        self.logger.info(f"{self.name} operation {status} in {execution_time:.2f}s")

    def __repr__(self) -> str:
        return f"{self.name}(destructive={self.is_destructive}, requires_backup={self.requires_backup})"


# NOTE: Example implementation has been moved to docs/examples/custom_operation_example.py
# See that file for a complete example of how to implement a custom operation using BaseOperation.
