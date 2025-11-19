#!/usr/bin/env python3
"""
Backup and Restore Manager for MongoDB Operations

Provides comprehensive backup and restore functionality with safety features.
All deletion operations MUST use backup_documents() before executing.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from bson import ObjectId

from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


def convert_objectid_to_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all ObjectId fields to strings for JSON serialization.

    Args:
        doc: MongoDB document with potential ObjectId fields

    Returns:
        Document copy with ObjectIds converted to strings
    """
    doc_copy = doc.copy()

    for key, value in doc_copy.items():
        if isinstance(value, ObjectId):
            doc_copy[key] = str(value)
            logger.debug(f"Converted {key} from ObjectId to string")

    return doc_copy


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def backup_documents(
    collection,
    filter_query: Dict[str, Any],
    operation_name: str,
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Optional[str]:
    """
    Create comprehensive backup of documents matching filter.

    CRITICAL: Always call this BEFORE any deletion operation.

    Args:
        collection: MongoDB collection object
        filter_query: MongoDB filter dict to select documents
        operation_name: Descriptive name (e.g., "duplicate_cleanup")
        output_dir: Directory for backup file (defaults to ./output)
        metadata: Optional dict with additional context
        test_mode: If True, adds test mode indicator to backup
        limit: Optional limit on number of documents to backup

    Returns:
        str: Path to backup file, or None if backup failed

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> backup_file = backup_documents(
        ...     collection=collection,
        ...     filter_query={"url": {"$in": duplicate_urls}},
        ...     operation_name="duplicate_cleanup",
        ...     metadata={"reason": "Removing duplicate URLs"}
        ... )
        >>>
        >>> if backup_file:
        ...     # Safe to proceed with deletion
        ...     result = collection.delete_many(filter_query)
    """
    logger.info(f"Starting backup for operation: {operation_name}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Fetch documents BEFORE deletion
        logger.info(f"Fetching documents with filter: {filter_query}")

        if limit:
            documents = list(collection.find(filter_query).limit(limit))
            logger.info(f"Applied limit of {limit} documents")
        else:
            documents = list(collection.find(filter_query))

        if len(documents) == 0:
            logger.warning("No documents match filter. Check your query!")
            print("⚠️  Warning: No documents match filter. Check your query!")
            return None

        logger.info(f"Found {len(documents)} documents to backup")

        # Convert ObjectIds to strings for JSON serialization
        backup_docs = [convert_objectid_to_str(doc) for doc in documents]
        logger.debug(f"Converted {len(backup_docs)} documents to JSON-safe format")

        # Create comprehensive backup structure
        backup_data = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "collection": collection.name,
            "database": collection.database.name,
            "filter": str(filter_query),
            "total_records": len(backup_docs),
            "test_mode": test_mode,
            "limit_applied": limit,
            "documents": backup_docs,
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using output directory: {output_dir}")

        # Save backup file
        backup_filename = f"backup_{timestamp}.json"
        backup_file = output_dir / backup_filename

        with open(backup_file, "w") as f:
            json.dump(backup_data, f, indent=2, default=str)

        file_size = backup_file.stat().st_size / 1024  # KB

        logger.info(f"Backup created successfully: {backup_file}")
        logger.info(f"Backup size: {file_size:.1f} KB")

        print(f"✓ Backup created: {backup_filename}")
        print(f"  - {len(backup_docs)} records backed up")
        print(f"  - File size: {file_size:.1f} KB")
        print(f"  - Location: {backup_file}")

        if test_mode:
            print("  - ⚠️  TEST MODE backup")

        return str(backup_file)

    except Exception as e:
        logger.error(f"Backup failed: {e!s}", exc_info=True)
        print(f"❌ Backup failed: {e!s}")
        return None


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def restore_documents(backup_file: str, collection, confirm: bool = True) -> int:
    """
    Restore documents from backup file.

    Args:
        backup_file: Path to backup JSON file
        collection: Target MongoDB collection
        confirm: If True, ask for confirmation before overwriting

    Returns:
        int: Number of documents restored

    Raises:
        Exception: If backup file invalid or restoration fails

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> try:
        ...     restored = restore_documents(
        ...         backup_file='output/backup_20251115_143022.json',
        ...         collection=collection
        ...     )
        ...     print(f"✅ Restored {restored} documents")
        ... except Exception as e:
        ...     print(f"❌ Restoration failed: {e}")
    """
    logger.info(f"Starting restore from: {backup_file}")
    print(f"Starting restore from: {backup_file}")

    try:
        # Load backup file
        with open(backup_file) as f:
            backup_data = json.load(f)

        logger.info("Backup file loaded successfully")

        # Verify backup structure
        if "documents" not in backup_data:
            raise Exception("Invalid backup file: missing 'documents' field")

        documents = backup_data["documents"]
        logger.info(f"Backup contains {len(documents)} documents")
        print(f"Backup contains {len(documents)} documents")

        # Display backup metadata
        print(f"  - Backup timestamp: {backup_data.get('timestamp')}")
        print(f"  - Original operation: {backup_data.get('operation_name')}")
        print(f"  - Collection: {backup_data.get('collection')}")
        print(f"  - Database: {backup_data.get('database')}")

        if backup_data.get("test_mode"):
            print("  - ⚠️  This was a TEST MODE backup")

        # Convert string IDs back to ObjectId
        for doc in documents:
            try:
                doc["_id"] = ObjectId(doc["_id"])
                logger.debug(f"Converted _id to ObjectId: {doc['_id']}")
            except Exception:
                logger.error(f"Failed to convert _id: {doc.get('_id')}")
                raise Exception(f"Invalid _id in backup: {doc.get('_id')}")

            # Convert other ObjectId fields back
            # Heuristic: fields ending in _id or Yid are likely ObjectIds
            for key, value in doc.items():
                if isinstance(value, str) and (key.endswith("_id") or key.endswith("Yid")):
                    try:
                        doc[key] = ObjectId(value)
                        logger.debug(f"Converted {key} to ObjectId")
                    except Exception:
                        # Keep as string if conversion fails
                        logger.debug(f"Could not convert {key} to ObjectId, keeping as string")
                        pass

        # Check if documents already exist
        existing_ids = [doc["_id"] for doc in documents]
        existing_count = collection.count_documents({"_id": {"$in": existing_ids}})

        logger.info(f"Found {existing_count} existing documents in collection")

        if existing_count > 0:
            logger.warning(f"{existing_count} documents already exist in collection")
            print(f"\n⚠️  {existing_count} documents already exist in collection")

            if confirm:
                response = input("Overwrite existing documents? (yes/no): ")
                if response.lower() != "yes":
                    logger.info("Restore cancelled by user")
                    print("Restore cancelled")
                    return 0

            # Delete existing first
            delete_result = collection.delete_many({"_id": {"$in": existing_ids}})
            logger.info(f"Removed {delete_result.deleted_count} existing documents")
            print(f"Removed {delete_result.deleted_count} existing documents")

        # Insert documents
        if documents:
            result = collection.insert_many(documents, ordered=False)
            restored_count = len(result.inserted_ids)

            logger.info(f"Successfully restored {restored_count} documents")
            print(f"\n✓ Restored {restored_count} documents")
            print(f"  - Backup timestamp: {backup_data.get('timestamp')}")
            print(f"  - Original operation: {backup_data.get('operation_name')}")

            return restored_count

        return 0

    except Exception as e:
        logger.error(f"Restoration failed: {e!s}", exc_info=True)
        raise Exception(f"Restoration failed: {e!s}")


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def create_cross_collection_backup(
    primary_collection,
    related_collection,
    primary_filter: Dict[str, Any],
    related_filter: Dict[str, Any],
    operation_name: str,
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
) -> Optional[str]:
    """
    Backup documents from two related collections.

    Used for cross-collection operations like deleting from both
    links and articlesdocuments together.

    Args:
        primary_collection: Primary MongoDB collection
        related_collection: Related MongoDB collection
        primary_filter: Filter for primary collection
        related_filter: Filter for related collection
        operation_name: Descriptive name
        output_dir: Directory for backup file
        metadata: Optional additional context
        test_mode: If True, marks as test mode backup

    Returns:
        str: Path to backup file, or None if failed

    Example:
        >>> backup_file = create_cross_collection_backup(
        ...     primary_collection=links_collection,
        ...     related_collection=articles_collection,
        ...     primary_filter={"url": {"$in": urls_to_delete}},
        ...     related_filter={"link": {"$in": urls_to_delete}},
        ...     operation_name="cross_collection_cleanup"
        ... )
    """
    logger.info(f"Starting cross-collection backup for: {operation_name}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Fetch from both collections
        logger.info(f"Fetching from primary collection: {primary_collection.name}")
        primary_docs = list(primary_collection.find(primary_filter))
        logger.info(f"Found {len(primary_docs)} documents in primary collection")

        logger.info(f"Fetching from related collection: {related_collection.name}")
        related_docs = list(related_collection.find(related_filter))
        logger.info(f"Found {len(related_docs)} documents in related collection")

        if len(primary_docs) == 0 and len(related_docs) == 0:
            logger.warning("No documents found in either collection")
            print("⚠️  Warning: No documents found in either collection")
            return None

        # Convert ObjectIds
        primary_backup = [convert_objectid_to_str(doc) for doc in primary_docs]
        related_backup = [convert_objectid_to_str(doc) for doc in related_docs]

        # Create backup structure
        backup_data = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "test_mode": test_mode,
            "primary_collection": {
                "name": primary_collection.name,
                "database": primary_collection.database.name,
                "filter": str(primary_filter),
                "count": len(primary_backup),
                "documents": primary_backup,
            },
            "related_collection": {
                "name": related_collection.name,
                "database": related_collection.database.name,
                "filter": str(related_filter),
                "count": len(related_backup),
                "documents": related_backup,
            },
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save backup
        backup_filename = f"cross_collection_backup_{timestamp}.json"
        backup_file = output_dir / backup_filename

        with open(backup_file, "w") as f:
            json.dump(backup_data, f, indent=2, default=str)

        file_size = backup_file.stat().st_size / 1024  # KB

        logger.info(f"Cross-collection backup created: {backup_file}")

        print(f"✓ Cross-collection backup created: {backup_filename}")
        print(f"  - Primary ({primary_collection.name}): {len(primary_backup)} documents")
        print(f"  - Related ({related_collection.name}): {len(related_backup)} documents")
        print(f"  - File size: {file_size:.1f} KB")
        print(f"  - Location: {backup_file}")

        if test_mode:
            print("  - ⚠️  TEST MODE backup")

        return str(backup_file)

    except Exception as e:
        logger.error(f"Cross-collection backup failed: {e!s}", exc_info=True)
        print(f"❌ Cross-collection backup failed: {e!s}")
        return None


def verify_backup(backup_file: str) -> bool:
    """
    Verify backup file integrity and structure.

    Args:
        backup_file: Path to backup JSON file

    Returns:
        bool: True if backup is valid
    """
    logger.info(f"Verifying backup file: {backup_file}")

    try:
        with open(backup_file) as f:
            backup_data = json.load(f)

        # Check required fields
        required_fields = ["timestamp", "operation_name", "collection", "database", "documents"]

        for field in required_fields:
            if field not in backup_data:
                logger.error(f"Missing required field: {field}")
                print(f"❌ Invalid backup: missing '{field}' field")
                return False

        doc_count = len(backup_data["documents"])
        logger.info(f"Backup verified: {doc_count} documents")
        print(f"✓ Backup verified: {doc_count} documents")

        return True

    except Exception as e:
        logger.error(f"Backup verification failed: {e!s}")
        print(f"❌ Backup verification failed: {e!s}")
        return False


if __name__ == "__main__":
    print("Backup Manager Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - backup_documents() - Create backup before deletion")
    print("  - restore_documents() - Restore from backup")
    print("  - create_cross_collection_backup() - Backup multiple collections")
    print("  - convert_objectid_to_str() - Helper for JSON serialization")
    print("  - verify_backup() - Check backup file integrity")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.backup import backup_documents, restore_documents")
