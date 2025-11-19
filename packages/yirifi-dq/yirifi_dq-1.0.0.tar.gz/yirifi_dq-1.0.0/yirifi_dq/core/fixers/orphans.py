#!/usr/bin/env python3
"""
Orphan Cleaner for MongoDB Collections

Cleans orphaned records - records with broken foreign key references.
Supports both deletion and reassignment strategies.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

from typing import Any, Dict, Optional

from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def clean_orphans(
    source_collection,
    target_collection,
    source_field: str,
    target_field: str,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
    auto_backup: bool = True,
) -> Dict[str, Any]:
    """
    Clean orphaned records from source collection.

    Args:
        source_collection: Collection to clean orphans from
        target_collection: Collection with valid foreign keys
        source_field: Field in source with foreign key reference
        target_field: Field in target collection
        filter_query: Optional filter for source records
        test_mode: If True, performs dry run without deletion
        limit: Optional limit on number of orphans to process
        auto_backup: If True, creates backup before deletion

    Returns:
        Dict with operation results

    Example:
        >>> # Clean orphaned articlesdocuments
        >>> result = clean_orphans(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid',
        ...     test_mode=False
        ... )
        >>> print(f"Deleted {result['deleted_count']} orphaned records")
    """
    logger.info(f"Cleaning orphans from {source_collection.name}.{source_field}")

    try:
        from yirifi_dq.core.backup import backup_documents
        from yirifi_dq.core.validators.orphans import find_orphans

        # Step 1: Find orphans
        print(f"\n{'=' * 80}")
        print(f"ORPHAN CLEANUP: {source_collection.name}")
        print(f"Foreign Key: {source_field} → {target_collection.name}.{target_field}")
        print(f"{'=' * 80}\n")

        print("Step 1: Finding orphaned records...")
        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
            filter_query=filter_query,
            test_mode=test_mode,
            limit=limit,
        )

        if not orphans:
            logger.info("No orphans found")
            print("\n✓ No orphaned records found. Nothing to clean.")
            return {"orphans_found": 0, "deleted_count": 0, "backup_file": None}

        logger.info(f"Found {len(orphans)} orphaned records")
        print(f"  - Orphans found: {len(orphans)}")

        # Step 2: Create backup if auto_backup enabled
        backup_file = None
        if auto_backup:
            print("\nStep 2: Creating backup...")
            orphan_ids = [orphan["_id"] for orphan in orphans]

            backup_file = backup_documents(
                collection=source_collection,
                filter_query={"_id": {"$in": orphan_ids}},
                operation_name=f"orphan_cleanup_{source_collection.name}",
                test_mode=test_mode,
            )

            if not backup_file:
                logger.error("Backup failed, aborting operation")
                print("❌ Backup failed. Aborting operation.")
                return {
                    "orphans_found": len(orphans),
                    "deleted_count": 0,
                    "backup_file": None,
                    "error": "Backup failed",
                }

        # Step 3: Delete orphans
        print("\nStep 3: Deleting orphaned records...")

        if test_mode:
            logger.info("TEST MODE: Skipping actual deletion")
            print(f"  ⚠️  TEST MODE: Would delete {len(orphans)} orphaned records")
            deleted_count = 0
        else:
            orphan_ids = [orphan["_id"] for orphan in orphans]
            result = source_collection.delete_many({"_id": {"$in": orphan_ids}})
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} orphaned records")
            print(f"  ✓ Deleted {deleted_count} orphaned records")

        # Step 4: Verify
        print("\nStep 4: Verification...")
        if not test_mode:
            from yirifi_dq.core.validators.orphans import verify_no_orphans

            no_orphans = verify_no_orphans(
                source_collection=source_collection,
                target_collection=target_collection,
                source_field=source_field,
                target_field=target_field,
                filter_query=filter_query,
            )

            if not no_orphans:
                logger.warning("Verification warning: Orphans may still exist")
                print("  ⚠️  WARNING: Orphans may still exist")
        else:
            print("  ⚠️  TEST MODE: Skipping verification")

        # Final results
        print(f"\n{'=' * 80}")
        if test_mode:
            print("✓ TEST RUN COMPLETED")
        else:
            print("✓ ORPHAN CLEANUP COMPLETED")
        print(f"{'=' * 80}\n")

        return {
            "orphans_found": len(orphans),
            "deleted_count": deleted_count,
            "backup_file": backup_file,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Orphan cleanup failed: {e!s}", exc_info=True)
        print(f"❌ Orphan cleanup failed: {e!s}")
        raise


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def reassign_orphans(
    source_collection,
    target_collection,
    source_field: str,
    target_field: str,
    new_target_value: Any,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Reassign orphaned records to a valid target value.

    Instead of deleting orphans, update their foreign key to point
    to a valid target record.

    Args:
        source_collection: Collection with orphaned records
        target_collection: Collection with valid foreign keys
        source_field: Field in source with foreign key reference
        target_field: Field in target collection
        new_target_value: Valid target value to reassign orphans to
        filter_query: Optional filter for source records
        test_mode: If True, performs dry run without updates
        limit: Optional limit on number of orphans to process

    Returns:
        Dict with operation results

    Example:
        >>> # Reassign orphaned articles to a default link
        >>> result = reassign_orphans(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid',
        ...     new_target_value='default_link_yid_123',
        ...     test_mode=False
        ... )
        >>> print(f"Reassigned {result['updated_count']} orphaned records")
    """
    logger.info(f"Reassigning orphans from {source_collection.name}.{source_field}")

    try:
        from yirifi_dq.core.validators.orphans import check_orphan_status, find_orphans

        # Step 1: Verify new target value exists
        print(f"\n{'=' * 80}")
        print(f"ORPHAN REASSIGNMENT: {source_collection.name}")
        print(f"Foreign Key: {source_field} → {target_collection.name}.{target_field}")
        print(f"{'=' * 80}\n")

        print("Step 1: Verifying new target value...")
        target_exists = not check_orphan_status(
            record_id=new_target_value,
            target_collection=target_collection,
            target_field=target_field,
        )

        if not target_exists:
            logger.error(f"New target value does not exist: {new_target_value}")
            print(f"❌ Error: New target value '{new_target_value}' does not exist in {target_collection.name}")
            return {"orphans_found": 0, "updated_count": 0, "error": "Invalid target value"}

        print(f"  ✓ Target value exists: {new_target_value}")

        # Step 2: Find orphans
        print("\nStep 2: Finding orphaned records...")
        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
            filter_query=filter_query,
            test_mode=test_mode,
            limit=limit,
        )

        if not orphans:
            logger.info("No orphans found")
            print("\n✓ No orphaned records found. Nothing to reassign.")
            return {"orphans_found": 0, "updated_count": 0}

        logger.info(f"Found {len(orphans)} orphaned records")
        print(f"  - Orphans found: {len(orphans)}")

        # Step 3: Reassign orphans
        print("\nStep 3: Reassigning orphaned records...")

        if test_mode:
            logger.info("TEST MODE: Skipping actual updates")
            print(f"  ⚠️  TEST MODE: Would reassign {len(orphans)} orphaned records to: {new_target_value}")
            updated_count = 0
        else:
            orphan_ids = [orphan["_id"] for orphan in orphans]
            result = source_collection.update_many({"_id": {"$in": orphan_ids}}, {"$set": {source_field: new_target_value}})
            updated_count = result.modified_count
            logger.info(f"Reassigned {updated_count} orphaned records")
            print(f"  ✓ Reassigned {updated_count} orphaned records to: {new_target_value}")

        # Step 4: Verify
        print("\nStep 4: Verification...")
        if not test_mode:
            from yirifi_dq.core.validators.orphans import verify_no_orphans

            no_orphans = verify_no_orphans(
                source_collection=source_collection,
                target_collection=target_collection,
                source_field=source_field,
                target_field=target_field,
                filter_query=filter_query,
            )

            if not no_orphans:
                logger.warning("Verification warning: Orphans may still exist")
                print("  ⚠️  WARNING: Orphans may still exist")
        else:
            print("  ⚠️  TEST MODE: Skipping verification")

        # Final results
        print(f"\n{'=' * 80}")
        if test_mode:
            print("✓ TEST RUN COMPLETED")
        else:
            print("✓ ORPHAN REASSIGNMENT COMPLETED")
        print(f"{'=' * 80}\n")

        return {
            "orphans_found": len(orphans),
            "updated_count": updated_count,
            "new_target_value": new_target_value,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Orphan reassignment failed: {e!s}", exc_info=True)
        print(f"❌ Orphan reassignment failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Orphan Cleaner Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - clean_orphans() - Delete orphaned records")
    print("  - reassign_orphans() - Reassign orphans to valid target")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.fixers.orphans import clean_orphans, reassign_orphans")
    print("  # OR")
    print("  from yirifi_dq.core.fixers import clean_orphans, reassign_orphans")
    print("\nCritical relationship in this framework:")
    print("  links.link_yid (PRIMARY KEY) ↔ articlesdocuments.articleYid (FOREIGN KEY)")
