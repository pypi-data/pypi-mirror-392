"""
Centralized Application Configuration

Consolidates scattered configuration from multiple locations (.env, setup.py, etc.)
into a single source of truth with validation and type safety.

Created: 2025-11-17 (Phase 6 Refactoring)
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """
    Centralized application configuration.

    Consolidates configuration from:
    - Environment variables (.env)
    - Default paths
    - Application constants

    Usage:
        >>> from yirifi_dq.config import config
        >>> print(config.PROJECT_ROOT)
        >>> uri = config.get_mongodb_uri('DEV')
    """

    # ==========================================
    # Path Configuration
    # ==========================================

    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    """Root directory of the project (yirifi-data-fixes/)"""

    CONFIG_DIR: Path = PROJECT_ROOT / "config"
    """Configuration files directory"""

    OUTPUT_DIR: Path = PROJECT_ROOT / "output"
    """Output directory for backups, reports, etc."""

    DATABASE_DIR: Path = PROJECT_ROOT / "databases"
    """Operation databases directory"""

    STATE_DB_PATH: Path = PROJECT_ROOT / "yirifi_dq" / "db" / "state.db"
    """SQLite state database path"""

    LOG_DIR: Path = PROJECT_ROOT / "logs"
    """Logging directory"""

    # ==========================================
    # MongoDB Configuration
    # ==========================================

    PRD_MONGODB_URI: Optional[str] = os.getenv("PRD_MONGODB_URI")
    """Production MongoDB connection string"""

    DEV_MONGODB_URI: Optional[str] = os.getenv("DEV_MONGODB_URI")
    """Development MongoDB connection string"""

    UAT_MONGODB_URI: Optional[str] = os.getenv("UAT_MONGODB_URI")
    """UAT MongoDB connection string"""

    # ==========================================
    # Application Defaults
    # ==========================================

    DEFAULT_TEST_LIMIT: int = 10
    """Default limit for test mode operations"""

    DEFAULT_BACKUP_DIR: Path = OUTPUT_DIR
    """Default directory for backups"""

    DEFAULT_ENVIRONMENT: str = "DEV"
    """Default environment if not specified"""

    DEFAULT_BATCH_SIZE: int = 100
    """Default batch size for bulk operations"""

    # ==========================================
    # Logging Configuration
    # ==========================================

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    """Logging level (DEBUG, INFO, WARNING, ERROR)"""

    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    """Maximum size of log files before rotation"""

    LOG_BACKUP_COUNT: int = 5
    """Number of backup log files to keep"""

    # ==========================================
    # Operation Configuration
    # ==========================================

    MAX_OPERATION_LOCKS: int = 10
    """Maximum number of concurrent operation locks"""

    LOCK_TIMEOUT_MINUTES: int = 60
    """Default lock timeout in minutes"""

    # ==========================================
    # Methods
    # ==========================================

    @classmethod
    def get_mongodb_uri(cls, environment: str) -> Optional[str]:
        """
        Get MongoDB URI for specified environment.

        Args:
            environment: Environment name ('PRD', 'DEV', 'UAT')

        Returns:
            MongoDB connection string or None if not configured

        Example:
            >>> uri = config.get_mongodb_uri('DEV')
            >>> if uri:
            ...     client = MongoClient(uri)
        """
        env_upper = environment.upper()
        attr_name = f"{env_upper}_MONGODB_URI"

        if not hasattr(cls, attr_name):
            raise ValueError(f"Unknown environment: {environment}")

        return getattr(cls, attr_name)

    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration is present.

        Raises:
            ValueError: If required configuration is missing

        Returns:
            True if validation passes

        Example:
            >>> try:
            ...     config.validate()
            ... except ValueError as e:
            ...     print(f"Configuration error: {e}")
        """
        required_vars = ["PRD_MONGODB_URI"]
        missing = []

        for var in required_vars:
            value = getattr(cls, var, None)
            if not value:
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}. Please set these in your .env file.")

        return True

    @classmethod
    def ensure_directories(cls) -> None:
        """
        Ensure all required directories exist.

        Creates directories if they don't exist:
        - OUTPUT_DIR
        - LOG_DIR
        - DATABASE_DIR

        Example:
            >>> config.ensure_directories()
            >>> assert config.OUTPUT_DIR.exists()
        """
        directories = [
            cls.OUTPUT_DIR,
            cls.LOG_DIR,
            cls.DATABASE_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_summary(cls) -> dict:
        """
        Get configuration summary for debugging.

        Returns:
            Dictionary with non-sensitive configuration values

        Example:
            >>> summary = config.get_summary()
            >>> print(f"Project root: {summary['PROJECT_ROOT']}")
        """
        return {
            "PROJECT_ROOT": str(cls.PROJECT_ROOT),
            "CONFIG_DIR": str(cls.CONFIG_DIR),
            "OUTPUT_DIR": str(cls.OUTPUT_DIR),
            "STATE_DB_PATH": str(cls.STATE_DB_PATH),
            "LOG_DIR": str(cls.LOG_DIR),
            "DEFAULT_ENVIRONMENT": cls.DEFAULT_ENVIRONMENT,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "PRD_MONGODB_URI_configured": bool(cls.PRD_MONGODB_URI),
            "DEV_MONGODB_URI_configured": bool(cls.DEV_MONGODB_URI),
            "UAT_MONGODB_URI_configured": bool(cls.UAT_MONGODB_URI),
        }


# Singleton instance - import this
config = Config()

# Validate configuration on import (can be disabled for testing)
if os.getenv("SKIP_CONFIG_VALIDATION") != "1":
    try:
        config.validate()
    except ValueError as e:
        # Log warning but don't fail - allow app to start
        import logging

        logging.warning(f"Configuration validation failed: {e}")

# Ensure directories exist
config.ensure_directories()


# Example usage
if __name__ == "__main__":
    """Demo of configuration usage."""
    print("\n" + "=" * 60)
    print("Yirifi-DQ Configuration Summary")
    print("=" * 60 + "\n")

    summary = config.get_summary()
    for key, value in summary.items():
        print(f"{key:30s} : {value}")

    print("\n" + "=" * 60)
    print("MongoDB Environments")
    print("=" * 60 + "\n")

    for env in ["PRD", "DEV", "UAT"]:
        uri = config.get_mongodb_uri(env)
        status = "✓ Configured" if uri else "✗ Not configured"
        print(f"{env:10s} : {status}")

    print("\n" + "=" * 60)
    print("Paths")
    print("=" * 60 + "\n")

    paths = {
        "Project Root": config.PROJECT_ROOT,
        "State DB": config.STATE_DB_PATH,
        "Output Dir": config.OUTPUT_DIR,
        "Log Dir": config.LOG_DIR,
    }

    for name, path in paths.items():
        exists = "✓" if path.exists() else "✗"
        print(f"{exists} {name:20s} : {path}")

    print()
