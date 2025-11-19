"""
Standardized Error Handling

Provides custom exception classes and error handling utilities for the
yirifi_dq framework. Replaces scattered error handling with a consistent approach.

Created: 2025-11-17 (Phase 6 Refactoring)
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

# ============================================================================
# Exception Hierarchy
# ============================================================================


class YirifiDQError(Exception):
    """
    Base exception for all yirifi_dq errors.

    All custom exceptions inherit from this for easy catching of framework errors.

    Example:
        >>> try:
        ...     # Some operation
        ...     pass
        ... except YirifiDQError as e:
        ...     # Catch all framework errors
        ...     print(f"Framework error: {e}")
    """

    pass


class ValidationError(YirifiDQError):
    """
    Raised when validation fails.

    Example:
        >>> if duplicates_found:
        ...     raise ValidationError(f"Found {len(duplicates)} duplicates")
    """

    pass


class FixerError(YirifiDQError):
    """
    Raised when a fixer operation fails.

    Example:
        >>> if not backup_created:
        ...     raise FixerError("Failed to create backup before deletion")
    """

    pass


class BackupError(YirifiDQError):
    """
    Raised when backup operation fails.

    Example:
        >>> if not backup_file.exists():
        ...     raise BackupError(f"Backup file not found: {backup_file}")
    """

    pass


class StateError(YirifiDQError):
    """
    Raised when state management operation fails.

    Example:
        >>> if operation.status == OperationStatus.FAILED:
        ...     raise StateError("Cannot rollback failed operation")
    """

    pass


class ConfigurationError(YirifiDQError):
    """
    Raised when configuration is invalid or missing.

    Example:
        >>> if not config.PRD_MONGODB_URI:
        ...     raise ConfigurationError("PRD_MONGODB_URI not configured")
    """

    pass


class LockError(YirifiDQError):
    """
    Raised when collection lock cannot be acquired.

    Example:
        >>> if collection_locked:
        ...     raise LockError(f"Collection {name} is locked by another operation")
    """

    pass


class VerificationError(YirifiDQError):
    """
    Raised when post-operation verification fails.

    Example:
        >>> if remaining_duplicates > 0:
        ...     raise VerificationError(f"Verification failed: {remaining_duplicates} duplicates remain")
    """

    pass


# ============================================================================
# Error Handling Utilities
# ============================================================================


def handle_operation_error(
    operation_id: str,
    error: Exception,
    state_manager,
    logger: logging.Logger,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Centralized error handling for operations.

    Handles logging, state updates, and error tracking for operation failures.

    Args:
        operation_id: ID of the failed operation
        error: Exception that was raised
        state_manager: StateManager instance
        logger: Logger instance
        context: Optional context information

    Example:
        >>> try:
        ...     # Operation logic
        ...     result = execute_operation(...)
        ... except Exception as e:
        ...     handle_operation_error(
        ...         operation_id=op_id,
        ...         error=e,
        ...         state_manager=state_manager,
        ...         logger=logger,
        ...         context={"collection": "links", "field": "url"}
        ...     )
        ...     raise
    """
    error_message = str(error)
    error_trace = traceback.format_exc()

    # Log to logger
    logger.error(f"Operation {operation_id} failed: {error_message}", exc_info=True, extra=context or {})

    # Log to state.db
    log_details = {
        "error_type": type(error).__name__,
        "error_trace": error_trace,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if context:
        log_details.update(context)

    state_manager.add_log(operation_id=operation_id, level="ERROR", message=error_message, details=log_details)

    # Update operation status
    from yirifi_dq.models.operation import OperationStatus

    state_manager.update_operation(operation_id, status=OperationStatus.FAILED, error_message=error_message)


def format_error_message(error: Exception, operation_name: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format error message with context for user-friendly display.

    Args:
        error: Exception that was raised
        operation_name: Name of the operation that failed
        context: Optional context information

    Returns:
        Formatted error message

    Example:
        >>> try:
        ...     find_duplicates(collection, 'url')
        ... except Exception as e:
        ...     msg = format_error_message(
        ...         error=e,
        ...         operation_name="find_duplicates",
        ...         context={"collection": "links"}
        ...     )
        ...     print(msg)
        ...     # Output: "Operation 'find_duplicates' failed: Connection timeout (collection: links)"
    """
    error_msg = str(error)
    error_type = type(error).__name__

    parts = [f"Operation '{operation_name}' failed: {error_msg}", f"({error_type})"]

    if context:
        context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
        parts.append(f"[{context_str}]")

    return " ".join(parts)


def is_recoverable_error(error: Exception) -> bool:
    """
    Determine if an error is potentially recoverable.

    Args:
        error: Exception to check

    Returns:
        True if error might be recoverable with retry

    Example:
        >>> try:
        ...     collection.find_one()
        ... except Exception as e:
        ...     if is_recoverable_error(e):
        ...         # Retry the operation
        ...         pass
    """
    # Network/connection errors are potentially recoverable
    recoverable_types = (
        "ConnectionError",
        "TimeoutError",
        "ServerSelectionTimeoutError",
        "AutoReconnect",
    )

    error_type = type(error).__name__
    return error_type in recoverable_types


def log_error_summary(
    logger: logging.Logger,
    operation_name: str,
    errors: list[Exception],
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log summary of multiple errors.

    Useful for batch operations where multiple errors may occur.

    Args:
        logger: Logger instance
        operation_name: Name of the operation
        errors: List of exceptions
        context: Optional context information

    Example:
        >>> errors = []
        >>> for item in batch:
        ...     try:
        ...         process(item)
        ...     except Exception as e:
        ...         errors.append(e)
        >>>
        >>> if errors:
        ...     log_error_summary(
        ...         logger=logger,
        ...         operation_name="batch_process",
        ...         errors=errors,
        ...         context={"batch_size": len(batch)}
        ...     )
    """
    error_counts = {}
    for error in errors:
        error_type = type(error).__name__
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    summary_lines = [f"Operation '{operation_name}' encountered {len(errors)} errors:"]

    for error_type, count in sorted(error_counts.items()):
        summary_lines.append(f"  - {error_type}: {count}")

    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        summary_lines.append(f"Context: {context_str}")

    logger.error("\n".join(summary_lines))


# ============================================================================
# Example Usage
# ============================================================================


if __name__ == "__main__":
    """Demo of error handling utilities."""
    print("\n" + "=" * 60)
    print("Yirifi-DQ Error Handling Demo")
    print("=" * 60 + "\n")

    # Example 1: Custom exceptions
    print("1. Custom Exceptions:")
    try:
        raise ValidationError("Found 10 duplicate records")
    except YirifiDQError as e:
        print(f"   Caught framework error: {e}")

    # Example 2: Error message formatting
    print("\n2. Error Message Formatting:")
    try:
        raise ValueError("Connection timeout")
    except Exception as e:
        msg = format_error_message(
            error=e,
            operation_name="find_duplicates",
            context={"collection": "links", "field": "url"},
        )
        print(f"   {msg}")

    # Example 3: Recoverable error detection
    print("\n3. Recoverable Error Detection:")
    errors = [
        ConnectionError("Network timeout"),
        ValueError("Invalid field name"),
        TimeoutError("Query timeout"),
    ]

    for error in errors:
        recoverable = "Yes" if is_recoverable_error(error) else "No"
        print(f"   {type(error).__name__:30s} : Recoverable? {recoverable}")

    print("\n" + "=" * 60 + "\n")
