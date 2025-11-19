#!/usr/bin/env python3
"""
Duplicate Remover for MongoDB Collections

Intelligently removes duplicate records while preserving the most valuable record.
Supports multiple strategies for selecting which duplicate to keep.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.progress import multi_step_progress
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


def select_keeper(
    duplicates: List[Dict[str, Any]],
    strategy: str = "oldest",
    related_collection: Optional[Any] = None,
    related_field: Optional[str] = None,
    related_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Select which duplicate record to keep based on strategy.

    Args:
        duplicates: List of duplicate documents
        strategy: Strategy to use ('oldest', 'newest', 'most_complete', 'match_foreign_key')
        related_collection: For 'match_foreign_key' strategy
        related_field: Field in duplicate that references related collection
        related_key: Field in related collection to match

    Returns:
        The document to keep

    Strategies:
        - 'oldest': Keep record with earliest createdAt
        - 'newest': Keep record with latest createdAt
        - 'most_complete': Keep record with most non-null fields
        - 'match_foreign_key': Keep record that has matching foreign key

    Example:
        >>> keeper = select_keeper(
        ...     duplicates=[doc1, doc2, doc3],
        ...     strategy='oldest'
        ... )
        >>> print(f"Keeping record: {keeper['_id']}")
    """
    logger.info(f"Selecting keeper using strategy: {strategy}")

    if len(duplicates) == 0:
        raise ValueError("Cannot select keeper from empty list")

    if len(duplicates) == 1:
        return duplicates[0]

    try:
        if strategy == "oldest":
            # Keep record with earliest createdAt
            # Use _id as tiebreaker (ObjectId contains timestamp)
            keeper = min(duplicates, key=lambda x: (x.get("createdAt", datetime.max), x.get("_id", "")))
            logger.info(f"Selected oldest: {keeper.get('_id')}")

        elif strategy == "newest":
            # Keep record with latest createdAt
            keeper = max(duplicates, key=lambda x: (x.get("createdAt", datetime.min), x.get("_id", "")))
            logger.info(f"Selected newest: {keeper.get('_id')}")

        elif strategy == "most_complete":
            # Keep record with most non-null fields
            def count_non_null_fields(doc):
                return sum(1 for v in doc.values() if v is not None and v != "")

            keeper = max(duplicates, key=count_non_null_fields)
            logger.info(f"Selected most complete: {keeper.get('_id')}")

        elif strategy == "match_foreign_key":
            # Keep record that has matching foreign key in related collection
            if not related_collection or not related_field or not related_key:
                raise ValueError("match_foreign_key strategy requires related_collection, related_field, and related_key")

            from yirifi_dq.core.validators.orphans import check_orphan_status

            # Find first non-orphaned record
            for doc in duplicates:
                related_value = doc.get(related_field)
                if related_value:
                    is_orphan = check_orphan_status(
                        record_id=related_value,
                        target_collection=related_collection,
                        target_field=related_key,
                    )
                    if not is_orphan:
                        keeper = doc
                        logger.info(f"Selected with matching foreign key: {keeper.get('_id')}")
                        return keeper

            # If all are orphaned, fall back to oldest
            logger.warning("All duplicates are orphaned, falling back to 'oldest' strategy")
            keeper = min(duplicates, key=lambda x: (x.get("createdAt", datetime.max), x.get("_id", "")))

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return keeper

    except Exception as e:
        logger.error(f"Failed to select keeper: {e!s}", exc_info=True)
        print(f"❌ Failed to select keeper: {e!s}")
        raise


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def remove_duplicates(
    collection,
    field: str,
    keep_strategy: str = "oldest",
    related_collection: Optional[Any] = None,
    related_field: Optional[str] = None,
    related_key: Optional[str] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
    auto_backup: bool = True,
) -> Dict[str, Any]:
    """
    Remove duplicate records from collection, keeping one based on strategy.

    Args:
        collection: MongoDB collection
        field: Field to check for duplicates
        keep_strategy: Strategy for selecting keeper ('oldest', 'newest', 'most_complete', 'match_foreign_key')
        related_collection: For 'match_foreign_key' strategy
        related_field: Field referencing related collection
        related_key: Field in related collection
        test_mode: If True, performs dry run without deletion
        limit: Optional limit on number of duplicate groups to process
        auto_backup: If True, creates backup before deletion

    Returns:
        Dict with operation results

    Example:
        >>> # Remove URL duplicates, keeping oldest
        >>> result = remove_duplicates(
        ...     collection=links_collection,
        ...     field='url',
        ...     keep_strategy='oldest',
        ...     test_mode=False
        ... )
        >>> print(f"Deleted {result['deleted_count']} duplicates")
        >>>
        >>> # Remove duplicates, keeping records with valid foreign keys
        >>> result = remove_duplicates(
        ...     collection=articles_collection,
        ...     field='link',
        ...     keep_strategy='match_foreign_key',
        ...     related_collection=links_collection,
        ...     related_field='articleYid',
        ...     related_key='link_yid'
        ... )
    """
    logger.info(f"Removing duplicates from {collection.name}.{field} using strategy: {keep_strategy}")

    try:
        from yirifi_dq.core.backup import backup_documents
        from yirifi_dq.core.validators.duplicates import find_duplicates

        print(f"\n{'=' * 80}")
        print(f"DUPLICATE REMOVAL: {collection.name}.{field}")
        print(f"Strategy: {keep_strategy}")
        print(f"{'=' * 80}\n")

        # Define operation steps
        steps = [
            "Finding duplicates",
            "Analyzing and selecting keepers",
            "Creating backup",
            "Deleting duplicates",
            "Verifying results",
        ]

        with multi_step_progress(steps) as next_step:
            # Step 1: Find duplicates
            duplicates_dict = find_duplicates(
                collection=collection,
                field_name=field,
                return_details=True,
                test_mode=test_mode,
                limit=limit,
            )
            next_step()

            if not duplicates_dict:
                logger.info("No duplicates found")
                print("\n✓ No duplicates found. Nothing to remove.")
                return {
                    "duplicate_groups": 0,
                    "duplicates_found": 0,
                    "deleted_count": 0,
                    "kept_count": 0,
                    "backup_file": None,
                }

            duplicate_groups = len(duplicates_dict)
            total_duplicates = sum(len(docs) for docs in duplicates_dict.values())
            logger.info(f"Found {duplicate_groups} duplicate groups with {total_duplicates} total records")
            print(f"  - Duplicate groups: {duplicate_groups}")
            print(f"  - Total duplicate records: {total_duplicates}")

        to_delete = []
        to_keep = []
        analysis_details = []

        for value, docs in duplicates_dict.items():
            # Select keeper
            keeper = select_keeper(
                duplicates=docs,
                strategy=keep_strategy,
                related_collection=related_collection,
                related_field=related_field,
                related_key=related_key,
            )

            to_keep.append(keeper["_id"])

            # Mark others for deletion
            for doc in docs:
                if doc["_id"] != keeper["_id"]:
                    to_delete.append(doc["_id"])

            analysis_details.append(
                {
                    "value": str(value)[:100],
                    "duplicate_count": len(docs),
                    "keeper_id": str(keeper["_id"]),
                    "deleted_ids": [str(doc["_id"]) for doc in docs if doc["_id"] != keeper["_id"]],
                }
            )

        logger.info(f"Selected {len(to_keep)} keepers, marking {len(to_delete)} for deletion")
        print("\nStep 2: Selection complete")
        print(f"  - Records to keep: {len(to_keep)}")
        print(f"  - Records to delete: {len(to_delete)}")

        if len(to_delete) == 0:
            logger.info("No records to delete")
            print("\n✓ No records need to be deleted.")
            return {
                "duplicate_groups": duplicate_groups,
                "duplicates_found": total_duplicates,
                "deleted_count": 0,
                "kept_count": len(to_keep),
                "backup_file": None,
            }

        # Step 3: Create backup if auto_backup enabled
        backup_file = None
        if auto_backup:
            print("\nStep 3: Creating backup...")
            backup_file = backup_documents(
                collection=collection,
                filter_query={"_id": {"$in": to_delete}},
                operation_name=f"duplicate_removal_{field}",
                test_mode=test_mode,
            )

            if not backup_file:
                logger.error("Backup failed, aborting operation")
                print("❌ Backup failed. Aborting operation.")
                return {
                    "duplicate_groups": duplicate_groups,
                    "duplicates_found": total_duplicates,
                    "deleted_count": 0,
                    "kept_count": 0,
                    "backup_file": None,
                    "error": "Backup failed",
                }

        # Step 4: Delete duplicates
        print("\nStep 4: Deleting duplicates...")

        if test_mode:
            logger.info("TEST MODE: Skipping actual deletion")
            print(f"  ⚠️  TEST MODE: Would delete {len(to_delete)} records")
            deleted_count = 0
        else:
            result = collection.delete_many({"_id": {"$in": to_delete}})
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} duplicate records")
            print(f"  ✓ Deleted {deleted_count} duplicate records")

        # Step 5: Verify
        print("\nStep 5: Verification...")
        if not test_mode:
            # Check that keepers still exist
            keeper_count = collection.count_documents({"_id": {"$in": to_keep}})
            if keeper_count != len(to_keep):
                logger.error(f"Verification failed: Expected {len(to_keep)} keepers, found {keeper_count}")
                print(f"  ⚠️  WARNING: Expected {len(to_keep)} keepers, found {keeper_count}")
            else:
                logger.info(f"Verification passed: All {keeper_count} keepers preserved")
                print(f"  ✓ All {keeper_count} keepers preserved")

            # Check no duplicates remain
            remaining_duplicates = find_duplicates(collection=collection, field_name=field, return_details=False)
            if len(remaining_duplicates) > 0:
                logger.warning(f"Verification failed: {len(remaining_duplicates)} duplicate values still exist")
                print(f"  ⚠️  WARNING: {len(remaining_duplicates)} duplicate values still exist")
            else:
                logger.info("Verification passed: No duplicates remain")
                print("  ✓ No duplicates remain")
        else:
            print("  ⚠️  TEST MODE: Skipping verification")

        # Final results
        print(f"\n{'=' * 80}")
        if test_mode:
            print("✓ TEST RUN COMPLETED")
        else:
            print("✓ DUPLICATE REMOVAL COMPLETED")
        print(f"{'=' * 80}\n")

        return {
            "duplicate_groups": duplicate_groups,
            "duplicates_found": total_duplicates,
            "deleted_count": deleted_count,
            "kept_count": len(to_keep),
            "backup_file": backup_file,
            "analysis_details": analysis_details,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Duplicate removal failed: {e!s}", exc_info=True)
        print(f"❌ Duplicate removal failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Duplicate Remover Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - remove_duplicates() - Remove duplicates with intelligent keeper selection")
    print("  - select_keeper() - Select which duplicate to keep")
    print("\nKeep Strategies:")
    print("  - 'oldest': Keep record with earliest createdAt")
    print("  - 'newest': Keep record with latest createdAt")
    print("  - 'most_complete': Keep record with most non-null fields")
    print("  - 'match_foreign_key': Keep record with valid foreign key reference")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.fixers.duplicates import remove_duplicates")
    print("  # OR")
    print("  from yirifi_dq.core.fixers import remove_duplicates")
