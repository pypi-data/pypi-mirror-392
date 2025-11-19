"""
Retry utilities with exponential backoff for network operations.

Provides decorators for automatic retry of MongoDB operations and API calls
with configurable backoff strategies.
"""

import logging
from typing import Any, Callable

from pymongo.errors import (
    AutoReconnect,
    ConnectionFailure,
    NetworkTimeout,
    ServerSelectionTimeoutError,
)
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


# MongoDB transient errors that should be retried
MONGODB_RETRY_EXCEPTIONS = (
    AutoReconnect,
    NetworkTimeout,
    ServerSelectionTimeoutError,
    ConnectionFailure,
)


def retry_mongodb_operation(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 10) -> Callable:
    """
    Decorator for MongoDB operations with retry logic.

    Automatically retries MongoDB operations that fail due to transient network errors.
    Uses exponential backoff with jitter to avoid thundering herd.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time in seconds between retries (default: 1)
        max_wait: Maximum wait time in seconds between retries (default: 10)

    Returns:
        Decorated function with retry logic

    Example:
        ```python
        @retry_mongodb_operation(max_attempts=5)
        def find_duplicates(collection, field):
            return collection.aggregate([...])
        ```
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(MONGODB_RETRY_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG),
        reraise=True,
    )


def retry_api_call(max_attempts: int = 3, min_wait: int = 2, max_wait: int = 30) -> Callable:
    """
    Decorator for external API calls with retry logic.

    Automatically retries API calls that fail due to network errors or rate limits.
    Uses exponential backoff with longer waits than MongoDB (for rate limiting).

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time in seconds between retries (default: 2)
        max_wait: Maximum wait time in seconds between retries (default: 30)

    Returns:
        Decorated function with retry logic

    Example:
        ```python
        @retry_api_call(max_attempts=5, max_wait=60)
        def call_openai_api(prompt):
            return openai.Completion.create(...)
        ```
    """
    # Common API exceptions (can be extended)
    import requests

    API_RETRY_EXCEPTIONS = (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,  # Could filter by status code
    )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(API_RETRY_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG),
        reraise=True,
    )


def with_retry(func: Callable, max_attempts: int = 3) -> Any:
    """
    Execute a function with automatic retry (non-decorator version).

    Useful for one-off calls where you don't want to decorate the function.

    Args:
        func: Function to execute
        max_attempts: Maximum number of retry attempts

    Returns:
        Function result

    Example:
        ```python
        result = with_retry(
            lambda: collection.find_one({"_id": doc_id}),
            max_attempts=5
        )
        ```
    """

    @retry_mongodb_operation(max_attempts=max_attempts)
    def wrapper():
        return func()

    return wrapper()
