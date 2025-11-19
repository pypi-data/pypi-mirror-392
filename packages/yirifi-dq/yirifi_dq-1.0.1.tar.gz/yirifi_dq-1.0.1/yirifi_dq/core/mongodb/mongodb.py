"""
MongoDB Client Management Utility
Handles connections to DEV, UAT, and PRD environments
"""

import os
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


def get_config_dir() -> Path:
    """Get the config directory path (~/.config/yirifi-dq)"""
    return Path.home() / ".config" / "yirifi-dq"


def load_env_config():
    """
    Load environment variables from .env files.

    Priority order (first found wins for each variable):
    1. Environment variables already set
    2. .env in current working directory
    3. ~/.config/yirifi-dq/.env (global config)
    """
    # Load from global config first (lower priority)
    global_env = get_config_dir() / ".env"
    if global_env.exists():
        load_dotenv(global_env)

    # Load from current directory (higher priority, overrides global)
    local_env = Path.cwd() / ".env"
    if local_env.exists():
        load_dotenv(local_env, override=True)


class MongoDBClientManager:
    """Manages MongoDB connections across environments"""

    _clients: ClassVar[dict] = {}
    _env_loaded: ClassVar[bool] = False

    @classmethod
    def get_client(cls, env: str = "PRD") -> MongoClient:
        """
        Get MongoDB client for specified environment

        Args:
            env: Environment name ('DEV', 'UAT', 'PRD')

        Returns:
            MongoClient instance

        Raises:
            ValueError: If environment not configured
        """
        if env not in cls._clients:
            # Load env config only once
            if not cls._env_loaded:
                load_env_config()
                cls._env_loaded = True

            uri_key = f"{env}_MONGODB_URI"
            uri = os.getenv(uri_key)

            if not uri:
                config_dir = get_config_dir()
                raise ValueError(
                    f"{uri_key} not found. Please configure MongoDB connection:\n\n"
                    f"Option 1: Global config (recommended)\n"
                    f"  mkdir -p {config_dir}\n"
                    f"  echo '{uri_key}=mongodb://...' >> {config_dir}/.env\n\n"
                    f"Option 2: Project .env file\n"
                    f"  echo '{uri_key}=mongodb://...' >> .env\n\n"
                    f"Option 3: Environment variable\n"
                    f"  export {uri_key}=mongodb://..."
                )

            # Create client with timeout settings to prevent indefinite hangs
            cls._clients[env] = MongoClient(
                uri,
                serverSelectionTimeoutMS=10000,  # 10 seconds to select server
                connectTimeoutMS=10000,  # 10 seconds to establish connection
                socketTimeoutMS=30000,  # 30 seconds for socket operations
                maxPoolSize=50,  # Maximum connection pool size
                minPoolSize=1,  # Minimum connection pool size
            )
            print(f"✓ Connected to {env} MongoDB")

        return cls._clients[env]

    @classmethod
    def get_database(cls, client: MongoClient, db_name: str) -> Database:
        """Get database from client"""
        return client[db_name]

    @classmethod
    def get_collection(cls, db: Database, collection_name: str) -> Collection:
        """Get collection from database"""
        return db[collection_name]

    @classmethod
    def close_all(cls):
        """Close all active connections"""
        for env, client in cls._clients.items():
            client.close()
            print(f"✓ Closed {env} connection")
        cls._clients = {}


# Convenience functions
def get_client(env: str = "PRD") -> MongoClient:
    """Get MongoDB client"""
    return MongoDBClientManager.get_client(env)


def get_database(client: MongoClient, db_name: str) -> Database:
    """Get database"""
    return MongoDBClientManager.get_database(client, db_name)


def get_collection(db: Database, collection_name: str) -> Collection:
    """Get collection"""
    return MongoDBClientManager.get_collection(db, collection_name)


# Example usage
if __name__ == "__main__":
    # Get PRD client
    client = get_client("PRD")

    # Get database
    db = get_database(client, "regdb")

    # Get collection
    collection = get_collection(db, "links")

    print(f"Collection: {collection.name}")
    print(f"Document count: {collection.count_documents({})}")
