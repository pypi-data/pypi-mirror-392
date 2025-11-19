"""
MongoDB Operation Helpers

Provides decorators and utilities for MongoDB operations with standardized
logging, timing, and error handling. These decorators replace the functionality
of deleted base classes (BaseValidator, BaseFixer) with a simpler functional approach.

Author: Data Quality Framework
Last Updated: 2025-11-17
"""

import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

from yirifi_dq.utils.logging_config import get_logger

# Type variable for generic function signatures
F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)


def mongodb_operation(operation_name: str, log_params: bool = True):
    """
    Decorator for MongoDB operations with standard logging, timing, and error handling.

    This decorator provides the same benefits as the deleted BaseValidator/BaseFixer
    classes but without the OOP overhead:
    - Automatic logging (start, completion, errors)
    - Automatic timing
    - Structured error handling
    - Parameter logging (optional)

    Args:
        operation_name: Human-readable name of the operation (e.g., "find_duplicates")
        log_params: Whether to log function parameters (default: True)

    Returns:
        Decorated function with enhanced logging and error handling

    Example:
        >>> from yirifi_dq.utils.mongodb_helpers import mongodb_operation
        >>> from yirifi_dq.models.results import ValidationResult
        >>>
        >>> @mongodb_operation("find_duplicates")
        >>> def find_duplicates(collection, field_name) -> ValidationResult:
        ...     # Your validation logic here
        ...     duplicates = list(collection.aggregate(...))
        ...     return ValidationResult(...)
        ...
        >>> # Decorator automatically logs:
        >>> # INFO - [find_duplicates] Starting operation
        >>> # INFO - [find_duplicates] Parameters: collection=links, field_name=url
        >>> # INFO - [find_duplicates] Completed in 2.34s

    Benefits over base classes:
        - 50% less code (no class boilerplate)
        - Works with existing functions (no refactor needed)
        - Composable (stack multiple decorators)
        - Easier to test (no class instantiation)
        - More Pythonic (functional approach)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get logger from function's module
            func_logger = logging.getLogger(func.__module__)

            # Log operation start
            func_logger.info(f"[{operation_name}] Starting operation")

            # Log parameters if requested
            if log_params and (args or kwargs):
                # Extract collection name if first arg is a MongoDB collection
                param_info = []
                if args:
                    first_arg = args[0]
                    if hasattr(first_arg, "name") and hasattr(first_arg, "database"):
                        # Looks like a MongoDB collection
                        param_info.append(f"collection={first_arg.name}")
                        param_info.append(f"database={first_arg.database.name}")
                        # Log remaining args
                        if len(args) > 1:
                            for i, arg in enumerate(args[1:], 1):
                                param_info.append(f"arg{i}={arg}")
                    else:
                        for i, arg in enumerate(args):
                            param_info.append(f"arg{i}={arg}")

                # Log kwargs
                for key, value in kwargs.items():
                    param_info.append(f"{key}={value}")

                if param_info:
                    func_logger.info(f"[{operation_name}] Parameters: {', '.join(param_info)}")

            # Execute function with timing
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Log successful completion
                func_logger.info(f"[{operation_name}] Completed in {duration:.2f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log failure with details
                func_logger.error(f"[{operation_name}] Failed after {duration:.2f}s: {e!s}", exc_info=True)
                raise

        return cast(F, wrapper)

    return decorator


def timed_operation(func: F) -> F:
    """
    Lightweight decorator that only adds timing (no logging).

    Useful for internal helper functions where you want timing
    but not the full logging of @mongodb_operation.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that returns (result, duration_seconds)

    Example:
        >>> @timed_operation
        >>> def expensive_computation(data):
        ...     # Complex processing
        ...     return processed_data
        ...
        >>> result, duration = expensive_computation(my_data)
        >>> print(f"Took {duration:.2f}s")
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> tuple[Any, float]:
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration

    return cast(F, wrapper)


def log_collection_info(collection) -> dict[str, Any]:
    """
    Extract and log useful information about a MongoDB collection.

    Utility function for logging collection details without cluttering
    the main function code.

    Args:
        collection: MongoDB collection object

    Returns:
        Dictionary with collection metadata

    Example:
        >>> info = log_collection_info(collection)
        >>> # Returns: {"name": "links", "database": "regdb", "count": 1234}
    """
    info = {
        "name": collection.name,
        "database": collection.database.name,
    }

    # Try to get document count (may fail on large collections)
    try:
        info["count"] = collection.estimated_document_count()
    except Exception:
        info["count"] = "unknown"

    logger.info(f"Collection info: {info}")
    return info


def format_aggregation_pipeline(pipeline: list[dict]) -> str:
    """
    Format MongoDB aggregation pipeline for readable logging.

    Utility for logging complex pipelines in a readable format.

    Args:
        pipeline: MongoDB aggregation pipeline

    Returns:
        Formatted pipeline string

    Example:
        >>> pipeline = [
        ...     {"$match": {"status": "active"}},
        ...     {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ... ]
        >>> formatted = format_aggregation_pipeline(pipeline)
        >>> logger.info(f"Pipeline: {formatted}")
    """
    import json

    try:
        return json.dumps(pipeline, indent=2, default=str)
    except Exception:
        return str(pipeline)


def batch_operation(
    items: list[Any],
    operation_func: Callable,
    batch_size: int = 100,
    operation_name: str = "batch_operation",
) -> list[Any]:
    """
    Execute a function on items in batches with progress logging.

    Useful for processing large datasets without overwhelming MongoDB
    or consuming too much memory.

    Args:
        items: List of items to process
        operation_func: Function to apply to each batch
        batch_size: Number of items per batch (default: 100)
        operation_name: Name for logging (default: "batch_operation")

    Returns:
        List of results from each batch

    Example:
        >>> def process_batch(docs):
        ...     return collection.insert_many(docs)
        ...
        >>> results = batch_operation(
        ...     items=documents_to_insert,
        ...     operation_func=process_batch,
        ...     batch_size=100,
        ...     operation_name="insert_documents"
        ... )
    """
    results = []
    total_items = len(items)
    total_batches = (total_items + batch_size - 1) // batch_size

    logger.info(f"[{operation_name}] Processing {total_items} items in {total_batches} batches")

    for i in range(0, total_items, batch_size):
        batch_num = (i // batch_size) + 1
        batch = items[i : i + batch_size]

        logger.info(f"[{operation_name}] Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

        start_time = time.time()
        try:
            result = operation_func(batch)
            duration = time.time() - start_time
            results.append(result)

            logger.info(f"[{operation_name}] Batch {batch_num}/{total_batches} completed in {duration:.2f}s")

        except Exception as e:
            logger.error(f"[{operation_name}] Batch {batch_num}/{total_batches} failed: {e!s}", exc_info=True)
            raise

    logger.info(f"[{operation_name}] All {total_batches} batches completed")
    return results


# Example usage (for documentation purposes)
if __name__ == "__main__":
    """Demo of MongoDB helper functions."""

    # Example 1: Using @mongodb_operation decorator
    @mongodb_operation("example_validator")
    def validate_collection(collection, _field_name: str):
        """Example validator using decorator."""
        from yirifi_dq.models.results import ValidationResult

        # Simulate validation
        issues = []  # Your validation logic here

        return ValidationResult(
            validator_name="validate_collection",
            collection_name=collection.name,
            database_name=collection.database.name,
            issues_found=len(issues),
            issue_details=issues,
            execution_time_seconds=0.0,  # Decorator handles timing
        )

    # Example 2: Using batch_operation
    def insert_batch(documents):
        """Example batch operation."""
        # Simulate batch insert
        return {"inserted_count": len(documents)}

    # documents = [...]  # Your documents
    # results = batch_operation(
    #     items=documents,
    #     operation_func=insert_batch,
    #     batch_size=100,
    #     operation_name="bulk_insert"
    # )

    print("✓ MongoDB helpers loaded successfully")
    print("  - @mongodb_operation decorator: automatic logging, timing, error handling")
    print("  - @timed_operation decorator: lightweight timing only")
    print("  - batch_operation(): process large datasets in batches")
    print("  - log_collection_info(): extract collection metadata")
    print("  - format_aggregation_pipeline(): readable pipeline logging")
