"""Data models and schemas."""

from .operation import (
    BackupResult,
    CustomOperationConfig,
    DataNormalizationConfig,
    DuplicateCleanupConfig,
    DuplicateCleanupResult,
    Environment,
    FieldMigrationConfig,
    KeepStrategy,
    OperationConfig,
    OperationMetadata,
    OperationResult,
    OperationStatus,
    OperationType,
    OrphanCleanupConfig,
    OrphanCleanupResult,
    RollbackResult,
    VerificationResult,
)
from .results import (
    AnalyzerResult,
    FixerResult,
    OperationSummary,
    ValidationResult,
)
from .state import (
    FrameworkStats,
    OperationLock,
    OperationLog,
    OperationState,
)

__all__ = [
    "AnalyzerResult",
    "BackupResult",
    "CustomOperationConfig",
    "DataNormalizationConfig",
    "DuplicateCleanupConfig",
    "DuplicateCleanupResult",
    "Environment",
    "FieldMigrationConfig",
    "FixerResult",
    "FrameworkStats",
    "KeepStrategy",
    # Configs
    "OperationConfig",
    "OperationLock",
    "OperationLog",
    # Metadata and Results
    "OperationMetadata",
    "OperationResult",
    # State
    "OperationState",
    "OperationStatus",
    "OperationSummary",
    # Enums
    "OperationType",
    "OrphanCleanupConfig",
    "OrphanCleanupResult",
    "RollbackResult",
    # Standardized Results (functional approach)
    "ValidationResult",
    "VerificationResult",
]
