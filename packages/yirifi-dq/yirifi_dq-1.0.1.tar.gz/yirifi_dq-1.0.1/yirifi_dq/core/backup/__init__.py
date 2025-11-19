"""
Backup Package

Collection of backup and restore utilities for MongoDB data operations.

Available functions:
- backup_documents: Create backup of documents before modification
- restore_documents: Restore documents from backup file
- create_cross_collection_backup: Backup related documents across collections
- verify_backup: Verify backup file integrity

Example:
    >>> from yirifi_dq.core.backup import backup_documents, restore_documents
    >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
    >>>
    >>> client = get_client(env='PRD')
    >>> db = get_database(client, 'regdb')
    >>> collection = get_collection(db, 'links')
    >>>
    >>> # Create backup
    >>> backup_file = backup_documents(
    ...     collection=collection,
    ...     filter_query={"status": "inactive"},
    ...     operation_name="cleanup_inactive"
    ... )
    >>>
    >>> # Restore if needed
    >>> restore_documents(backup_file, collection)
"""

# Import all functions from backup module
from .backup import (
    backup_documents,
    convert_objectid_to_str,
    create_cross_collection_backup,
    restore_documents,
    verify_backup,
)

__all__ = [
    "backup_documents",
    "convert_objectid_to_str",
    "create_cross_collection_backup",
    "restore_documents",
    "verify_backup",
]
