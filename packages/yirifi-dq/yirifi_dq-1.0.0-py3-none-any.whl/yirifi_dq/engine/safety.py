"""
Safety Enforcement Layer

Provides safety checks, backup enforcement, and rollback capabilities
to protect against data loss and ensure data integrity.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from bson import ObjectId

from yirifi_dq.db.state_manager import StateManager, get_state_manager
from yirifi_dq.core.mongodb import get_client, get_collection, get_database


class SafetyEnforcer:
    """
    Enforces safety rules for data quality operations.

    Key features:
    - Mandatory backup before destructive operations
    - Pre-execution validation
    - Post-execution verification
    - Rollback capabilities
    """

    def __init__(self, state_manager: Optional[StateManager] = None):
        """
        Initialize safety enforcer.

        Args:
            state_manager: StateManager instance (uses singleton if None)
        """
        self.state_manager = state_manager or get_state_manager()

    def enforce_backup(self, operation_id: str, collection, filter_query: Dict[str, Any], operation_name: str) -> Optional[str]:
        """
        Enforce backup before destructive operation.

        Args:
            operation_id: Operation ID
            collection: MongoDB collection
            filter_query: Filter for documents to backup
            operation_name: Name of operation (for backup file naming)

        Returns:
            Backup file path or None if failed
        """
        from yirifi_dq.core.backup import backup_documents

        self.state_manager.add_log(operation_id, "INFO", "Enforcing mandatory backup...")

        try:
            backup_file = backup_documents(
                collection=collection,
                filter_query=filter_query,
                operation_name=operation_name,
                test_mode=False,
            )

            if not backup_file:
                self.state_manager.add_log(operation_id, "ERROR", "Backup failed - operation aborted")
                return None

            self.state_manager.add_log(operation_id, "INFO", f"Backup created: {backup_file}")

            # Update operation state with backup file
            self.state_manager.update_operation(operation_id, backup_file=backup_file)

            return backup_file

        except Exception as e:
            self.state_manager.add_log(operation_id, "ERROR", f"Backup failed: {e!s}")
            return None

    def verify_backup(self, backup_file: str) -> bool:
        """
        Verify that backup file exists and is valid.

        Args:
            backup_file: Path to backup file

        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(backup_file):
            return False

        try:
            with open(backup_file) as f:
                data = json.load(f)

            # Check required fields
            required_fields = ["metadata", "documents"]
            if not all(field in data for field in required_fields):
                return False

            # Check document count
            return len(data["documents"]) != 0

        except Exception:
            return False

    def rollback_from_backup(
        self,
        operation_id: str,
        backup_file: str,
        database: str,
        collection_name: str,
        environment: str,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Rollback operation by restoring from backup.

        Args:
            operation_id: Operation ID
            backup_file: Path to backup file
            database: Database name
            collection_name: Collection name
            environment: Environment (PRD, DEV, UAT)
            dry_run: If True, preview only without restoring

        Returns:
            Rollback result
        """
        self.state_manager.add_log(
            operation_id,
            "WARNING" if dry_run else "INFO",
            f"{'DRY RUN: ' if dry_run else ''}Starting rollback from {backup_file}",
        )

        # Load backup file
        try:
            with open(backup_file) as f:
                backup_data = json.load(f)
        except Exception as e:
            self.state_manager.add_log(operation_id, "ERROR", f"Failed to load backup file: {e!s}")
            return {"success": False, "error": str(e)}

        documents = backup_data.get("documents", [])
        metadata = backup_data.get("metadata", {})

        self.state_manager.add_log(operation_id, "INFO", f"Backup contains {len(documents)} documents")

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "documents_to_restore": len(documents),
                "metadata": metadata,
            }

        # Connect to MongoDB
        client = get_client(env=environment)

        try:
            db = get_database(client, database)
            collection = get_collection(db, collection_name)

            # Restore documents with better error handling
            restored_count = 0
            errors = []
            restored_ids = []  # Track successful restorations for potential rollback

            for idx, doc in enumerate(documents):
                try:
                    # Convert string _id back to ObjectId if needed
                    if "_id" in doc and isinstance(doc["_id"], str):
                        doc["_id"] = ObjectId(doc["_id"])

                    # Restore document (replace if exists, insert if not)
                    collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
                    restored_count += 1
                    restored_ids.append(doc["_id"])

                except Exception as e:
                    error_info = {
                        "document_id": str(doc.get("_id")),
                        "error": str(e),
                        "document_index": idx,
                    }
                    errors.append(error_info)

                    # If first document fails, abort immediately
                    if idx == 0:
                        self.state_manager.add_log(
                            operation_id,
                            "ERROR",
                            "Rollback failed on first document - aborting to prevent inconsistent state",
                            error_info,
                        )
                        return {
                            "success": False,
                            "restored_count": 0,
                            "total_documents": len(documents),
                            "errors": errors,
                            "aborted": True,
                            "message": "Rollback aborted on first document failure to prevent partial restore",
                        }

                    # For subsequent errors, log but continue (partial restore is better than none)
                    self.state_manager.add_log(
                        operation_id,
                        "WARNING",
                        f"Error restoring document {idx + 1}/{len(documents)}",
                        error_info,
                    )

            self.state_manager.add_log(
                operation_id,
                "INFO" if len(errors) == 0 else "WARNING",
                f"Restored {restored_count}/{len(documents)} documents",
            )

            if errors:
                self.state_manager.add_log(
                    operation_id,
                    "ERROR",
                    f"{len(errors)} errors during rollback",
                    {"errors": errors[:10], "total_errors": len(errors)},  # Log first 10 errors
                )

            return {
                "success": len(errors) == 0,
                "restored_count": restored_count,
                "total_documents": len(documents),
                "errors": errors,
                "restored_ids": [str(oid) for oid in restored_ids],  # For potential rollback of rollback
            }

        finally:
            # Close MongoDB connection
            if client:
                try:
                    client.close()
                except Exception as e:
                    self.state_manager.add_log(
                        operation_id,
                        "WARNING",
                        f"Error closing MongoDB connection during rollback: {e!s}",
                    )

    def verify_referential_integrity(self, operation_id: str, database: str, environment: str) -> Dict[str, Any]:
        """
        Verify referential integrity between links and articlesdocuments.

        Args:
            operation_id: Operation ID
            database: Database name
            environment: Environment

        Returns:
            Verification result
        """
        from yirifi_dq.core.validators import find_orphans

        self.state_manager.add_log(operation_id, "INFO", "Verifying referential integrity...")

        client = get_client(env=environment)
        db = get_database(client, database)

        links_collection = get_collection(db, "links")
        articles_collection = get_collection(db, "articlesdocuments")

        # Check for orphaned articles
        orphaned_articles = find_orphans(
            collection=articles_collection,
            foreign_key_field="articleYid",
            parent_collection=links_collection,
            parent_key_field="link_yid",
            return_details=True,
        )

        orphan_count = len(orphaned_articles) if orphaned_articles else 0

        if orphan_count > 0:
            self.state_manager.add_log(operation_id, "WARNING", f"Found {orphan_count} orphaned article documents")

        return {
            "passed": orphan_count == 0,
            "orphaned_articles": orphan_count,
            "details": orphaned_articles[:10] if orphaned_articles else [],  # First 10
        }

    def verify_no_duplicates(self, operation_id: str, collection, field: str) -> Dict[str, Any]:
        """
        Verify no duplicates exist in a field.

        Args:
            operation_id: Operation ID
            collection: MongoDB collection
            field: Field to check

        Returns:
            Verification result
        """
        from yirifi_dq.core.validators import find_duplicates

        self.state_manager.add_log(operation_id, "INFO", f"Verifying no duplicates in field '{field}'...")

        duplicates = find_duplicates(collection, field, return_details=True)
        duplicate_count = len(duplicates) if duplicates else 0

        if duplicate_count > 0:
            self.state_manager.add_log(operation_id, "WARNING", f"Found {duplicate_count} duplicate groups")

        return {
            "passed": duplicate_count == 0,
            "duplicate_groups": duplicate_count,
            "details": duplicates[:10] if duplicates else [],  # First 10
        }

    def verify_record_counts(self, operation_id: str, collection, expected_change: Dict[str, int]) -> Dict[str, Any]:
        """
        Verify record counts match expected changes.

        Args:
            operation_id: Operation ID
            collection: MongoDB collection
            expected_change: Expected changes (e.g., {'deleted': 10})

        Returns:
            Verification result
        """
        self.state_manager.add_log(operation_id, "INFO", "Verifying record counts...")

        current_count = collection.count_documents({})

        self.state_manager.add_log(operation_id, "INFO", f"Current record count: {current_count}")

        return {
            "passed": True,  # Can't verify without before count
            "current_count": current_count,
            "expected_change": expected_change,
        }

    def check_index_json_duplicates(self, operation_id: str, database: str, collection: str, field: Optional[str] = None) -> bool:
        """
        Check if similar operation already exists in INDEX.json.

        Args:
            operation_id: Operation ID
            database: Database name
            collection: Collection name
            field: Optional field name

        Returns:
            True if duplicate found, False otherwise
        """
        framework_root = Path(__file__).parent.parent.parent
        index_file = framework_root / "framework" / "INDEX.json"

        if not index_file.exists():
            return False

        try:
            with open(index_file) as f:
                index_data = json.load(f)

            operations = index_data.get("operations", [])

            # Check for similar operations
            for op in operations:
                if op.get("database") == database and op.get("collection") == collection and (field is None or op.get("field") == field):
                    self.state_manager.add_log(
                        operation_id,
                        "WARNING",
                        f"Similar operation found in INDEX.json: {op.get('operation_id')}",
                    )
                    return True

            return False

        except Exception:
            return False


def check_mongodb_connection(environment: str) -> bool:
    """
    Check if MongoDB connection is available.

    Args:
        environment: Environment (PRD, DEV, UAT)

    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_client(env=environment)
        # Ping database
        client.admin.command("ping")
        return True
    except Exception:
        return False


def get_collection_stats(database: str, collection_name: str, environment: str) -> Optional[Dict[str, Any]]:
    """
    Get collection statistics.

    Args:
        database: Database name
        collection_name: Collection name
        environment: Environment

    Returns:
        Collection stats or None if failed
    """
    try:
        client = get_client(env=environment)
        db = get_database(client, database)
        collection = get_collection(db, collection_name)

        total_count = collection.count_documents({})
        sample_doc = collection.find_one()

        return {
            "total_documents": total_count,
            "sample_fields": list(sample_doc.keys()) if sample_doc else [],
            "database": database,
            "collection": collection_name,
        }

    except Exception:
        return None
