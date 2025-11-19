"""
CLI utilities for Yirifi Data Quality Framework.
"""

from .error_handling import (
    BackupError,
    ConfigurationError,
    FixerError,
    LockError,
    StateError,
    ValidationError,
    VerificationError,
    YirifiDQError,
    format_error_message,
    handle_operation_error,
)
from .logging_config import (
    get_logger,
    setup_logging,
    setup_operation_logging,
)
from .mongodb_helpers import (
    batch_operation,
    format_aggregation_pipeline,
    log_collection_info,
    mongodb_operation,
    timed_operation,
)
from .yaml_utils import (
    YAMLError,
    YAMLValidationError,
    load_yaml,
    save_yaml,
    save_yaml_with_metadata,
    validate_yaml_structure,
)

__all__ = [
    "BackupError",
    "ConfigurationError",
    "FixerError",
    "LockError",
    "StateError",
    "ValidationError",
    "VerificationError",
    "YAMLError",
    "YAMLValidationError",
    # Error handling (NEW: standardized exceptions)
    "YirifiDQError",
    "batch_operation",
    "format_aggregation_pipeline",
    "format_error_message",
    # Logging utilities
    "get_logger",
    "handle_operation_error",
    # YAML utilities
    "load_yaml",
    "log_collection_info",
    # MongoDB utilities
    "mongodb_operation",
    "save_yaml",
    "save_yaml_with_metadata",
    "setup_logging",
    "setup_operation_logging",
    "timed_operation",
    "validate_yaml_structure",
]
