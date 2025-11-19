"""
Centralized logging configuration for yirifi_dq framework.

Provides both file and console logging with automatic log rotation.
Optimized for solo operator use - simple, effective, no over-engineering.
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# Default log directory
DEFAULT_LOG_DIR = Path(__file__).parent.parent.parent / "logs"

# Log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_level: Optional[str] = None,
):
    """
    Configure centralized logging for the framework.

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Logging level for file (DEBUG, INFO, WARNING, ERROR)
        max_bytes: Max size of each log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        console_level: Logging level for console (default: same as log_level)

    Example:
        >>> # At start of your operation script
        >>> from yirifi_dq.utils.logging_config import setup_logging
        >>> setup_logging(log_level="DEBUG")
        >>>
        >>> # Then use logging as normal
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Operation started")
    """
    # Create log directory if it doesn't exist
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)

    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Console level defaults to same as file level
    console_numeric_level = numeric_level if console_level is None else getattr(logging, console_level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything, handlers will filter

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # Create formatters
    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT)

    # 1. File handler - Rotating by size
    log_file = log_dir / "yirifi_dq.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 2. Daily file handler - One file per day
    daily_log_file = log_dir / "yirifi_dq_daily.log"
    daily_handler = TimedRotatingFileHandler(
        daily_log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days
    )
    daily_handler.setLevel(numeric_level)
    daily_handler.setFormatter(formatter)
    daily_handler.suffix = "%Y%m%d"
    root_logger.addHandler(daily_handler)

    # 3. Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_numeric_level)

    # Simpler format for console
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 4. Error file handler - Separate file for errors only
    error_log_file = log_dir / "yirifi_dq_errors.log"
    error_handler = RotatingFileHandler(error_log_file, maxBytes=max_bytes, backupCount=backup_count)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"Logging initialized at {datetime.now().isoformat()}")
    logger.info(f"Log directory: {log_dir}")
    logger.info(f"File log level: {log_level}")
    logger.info(f"Console log level: {console_level or log_level}")
    logger.info(f"Main log: {log_file}")
    logger.info(f"Daily log: {daily_log_file}")
    logger.info(f"Error log: {error_log_file}")
    logger.info("=" * 80)

    return root_logger


def setup_operation_logging(operation_name: str, log_dir: Optional[Path] = None, log_level: str = "INFO"):
    """
    Set up logging for a specific operation with a dedicated log file.

    Args:
        operation_name: Name of the operation (used for log filename)
        log_dir: Directory for log files (default: ./logs/operations)
        log_level: Logging level

    Returns:
        Logger instance for this operation

    Example:
        >>> logger = setup_operation_logging("duplicate_cleanup")
        >>> logger.info("Starting duplicate cleanup")
        >>> # Logs go to both console and logs/operations/duplicate_cleanup_YYYYMMDD.log
    """
    # Set up base logging first
    setup_logging(log_level=log_level)

    # Create operation-specific log directory
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR / "operations"

    log_dir.mkdir(parents=True, exist_ok=True)

    # Create operation-specific logger
    logger = logging.getLogger(f"operation.{operation_name}")

    # Create operation-specific file handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    operation_log_file = log_dir / f"{operation_name}_{timestamp}.log"

    operation_handler = logging.FileHandler(operation_log_file)
    operation_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT)
    operation_handler.setFormatter(formatter)

    logger.addHandler(operation_handler)

    logger.info("=" * 80)
    logger.info(f"Operation logging initialized: {operation_name}")
    logger.info(f"Operation log file: {operation_log_file}")
    logger.info("=" * 80)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    This is a convenience function that ensures logging is set up
    before returning the logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Example:
        >>> from yirifi_dq.utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a test")
    """
    # Ensure logging is set up (idempotent)
    if not logging.getLogger().handlers:
        setup_logging()

    return logging.getLogger(name)


def cleanup_old_logs(log_dir: Optional[Path] = None, days_to_keep: int = 30):
    """
    Clean up log files older than specified days.

    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days to keep (default: 30)

    Example:
        >>> from yirifi_dq.utils.logging_config import cleanup_old_logs
        >>> cleanup_old_logs(days_to_keep=7)  # Keep last 7 days
    """
    import time

    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    if not log_dir.exists():
        return

    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    deleted_count = 0

    for log_file in log_dir.rglob("*.log*"):
        # Skip current main log files
        if log_file.name in ["yirifi_dq.log", "yirifi_dq_errors.log", "yirifi_dq_daily.log"]:
            continue

        # Check file age
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to delete old log file {log_file}: {e}")

    if deleted_count > 0:
        logger = logging.getLogger(__name__)
        logger.info(f"Cleaned up {deleted_count} log files older than {days_to_keep} days")


if __name__ == "__main__":
    """Demo of logging configuration."""
    print("\nLogging Configuration Demo\n")

    # Set up logging
    setup_logging(log_level="DEBUG", console_level="INFO")

    # Test different log levels
    logger = get_logger(__name__)

    logger.debug("This is a debug message (file only)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test operation-specific logging
    op_logger = setup_operation_logging("test_operation", log_level="DEBUG")
    op_logger.info("This goes to both main log and operation-specific log")

    print("\n✓ Logs created in:", DEFAULT_LOG_DIR)
    print("  - yirifi_dq.log (main log, rotating by size)")
    print("  - yirifi_dq_daily.log (daily rotating log)")
    print("  - yirifi_dq_errors.log (errors only)")
    print("  - operations/test_operation_*.log (operation-specific)")
    print("\n✓ Check the logs directory to see the output!\n")
