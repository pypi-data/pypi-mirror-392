"""
MongoDB Package

MongoDB connection and utility functions for data quality operations.

Available functions:
- get_client: Get MongoDB client connection
- get_database: Get database handle from client
- get_collection: Get collection handle from database

Example:
    >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
    >>>
    >>> # Connect to MongoDB
    >>> client = get_client(env='PRD')
    >>> db = get_database(client, 'regdb')
    >>> collection = get_collection(db, 'links')
    >>>
    >>> # Perform operations
    >>> count = collection.count_documents({})
"""

# Import all functions from mongodb module
from .mongodb import get_client, get_database, get_collection

__all__ = [
    "get_client",
    "get_database",
    "get_collection",
]
