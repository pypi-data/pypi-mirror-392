"""
MongoDB Client Management Utility
Handles connections to DEV, UAT, and PRD environments
"""

import os
from typing import ClassVar

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoDBClientManager:
    """Manages MongoDB connections across environments"""

    _clients: ClassVar[dict] = {}

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
            load_dotenv()
            uri_key = f"{env}_MONGODB_URI"
            uri = os.getenv(uri_key)

            if not uri:
                raise ValueError(f"{uri_key} not found in .env file")

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
