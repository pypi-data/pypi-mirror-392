#!/usr/bin/env python3
"""
Orphan Detector for MongoDB Collections

Detects orphaned records - records with foreign key references that don't exist
in the related collection. Critical for maintaining referential integrity.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.progress import operation_progress
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def check_orphan_status(record_id: Any, target_collection, target_field: str) -> bool:
    """
    Check if a single record ID exists in target collection.

    Args:
        record_id: The ID value to check (e.g., articleYid value)
        target_collection: MongoDB collection to check against
        target_field: Field name in target collection (e.g., 'link_yid')

    Returns:
        bool: True if orphaned (no match found), False otherwise

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> links_collection = get_collection(db, 'links')
        >>>
        >>> is_orphan = check_orphan_status(
        ...     record_id='some_article_yid',
        ...     target_collection=links_collection,
        ...     target_field='link_yid'
        ... )
        >>> if is_orphan:
        ...     print("This record is orphaned!")
    """
    try:
        matching_record = target_collection.find_one({target_field: record_id})
        is_orphan = matching_record is None

        logger.debug(f"Checked {record_id}: {'ORPHAN' if is_orphan else 'LINKED'}")

        return is_orphan

    except Exception as e:
        logger.error(f"Failed to check orphan status for {record_id}: {e!s}")
        raise


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def find_orphans(
    source_collection,
    target_collection,
    source_field: str,
    target_field: str,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Find all orphaned records in source collection.

    An orphaned record is one where source_field value doesn't exist
    in target_collection's target_field.

    Args:
        source_collection: Collection to check for orphans
        target_collection: Collection with valid foreign keys
        source_field: Field in source collection (e.g., 'articleYid')
        target_field: Field in target collection (e.g., 'link_yid')
        filter_query: Optional filter for source collection
        test_mode: If True, adds test mode warnings
        limit: Optional limit on number of records to check

    Returns:
        List of orphaned documents

    Example:
        >>> # Find articlesdocuments with invalid articleYid references
        >>> orphans = find_orphans(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid'
        ... )
        >>> print(f"Found {len(orphans)} orphaned records")
    """
    logger.info(f"Finding orphans: {source_collection.name}.{source_field} → {target_collection.name}.{target_field}")

    try:
        # Build query
        query = filter_query if filter_query else {}

        # Get source records
        if limit:
            logger.info(f"Applying limit: {limit}")
            source_records = list(source_collection.find(query).limit(limit))
        else:
            source_records = list(source_collection.find(query))

        logger.info(f"Checking {len(source_records)} source records for orphans")

        if test_mode:
            print(f"⚠️  TEST MODE: Checking {len(source_records)} records for orphans")

        # Check each record with progress indicator
        orphans = []
        orphan_count = 0

        with operation_progress("Checking for orphans", total=len(source_records)) as update:
            for i, record in enumerate(source_records):
                source_value = record.get(source_field)

                if source_value is None:
                    logger.warning(f"Record {record.get('_id')} has no value for {source_field}")
                    continue

                is_orphan = check_orphan_status(
                    record_id=source_value,
                    target_collection=target_collection,
                    target_field=target_field,
                )

                if is_orphan:
                    orphans.append(record)
                    orphan_count += 1

                # Update progress every 10 records or on last record
                if i % 10 == 0 or i == len(source_records) - 1:
                    update(i + 1)

        logger.info(f"Found {len(orphans)} orphaned records out of {len(source_records)} checked")
        print(f"✓ Orphan check complete: {len(orphans)} orphans found out of {len(source_records)} records")

        return orphans

    except Exception as e:
        logger.error(f"Failed to find orphans: {e!s}", exc_info=True)
        print(f"❌ Failed to find orphans: {e!s}")
        raise


def verify_no_orphans(
    source_collection,
    target_collection,
    source_field: str,
    target_field: str,
    filter_query: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Verify that no orphans exist in source collection.

    Useful for post-operation verification.

    Args:
        source_collection: Collection to check for orphans
        target_collection: Collection with valid foreign keys
        source_field: Field in source collection
        target_field: Field in target collection
        filter_query: Optional filter for source collection

    Returns:
        bool: True if no orphans found, False otherwise

    Example:
        >>> # After cleanup, verify no orphans remain
        >>> no_orphans = verify_no_orphans(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid'
        ... )
        >>> if no_orphans:
        ...     print("✓ Verification passed: No orphans found")
        ... else:
        ...     print("⚠️  Verification failed: Orphans still exist!")
    """
    logger.info("Verifying no orphans exist")

    try:
        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
            filter_query=filter_query,
        )

        if len(orphans) == 0:
            logger.info("✓ Verification passed: No orphans found")
            print("✓ Verification passed: No orphans found")
            return True
        else:
            logger.warning(f"⚠️  Verification failed: {len(orphans)} orphans found")
            print(f"⚠️  Verification failed: {len(orphans)} orphans found")
            return False

    except Exception as e:
        logger.error(f"Verification failed: {e!s}", exc_info=True)
        print(f"❌ Verification failed: {e!s}")
        raise


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def generate_orphan_report(
    source_collection,
    target_collection,
    source_field: str,
    target_field: str,
    output_dir: Optional[Path] = None,
    filter_query: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate detailed orphan detection report.

    Args:
        source_collection: Collection to check for orphans
        target_collection: Collection with valid foreign keys
        source_field: Field in source collection
        target_field: Field in target collection
        output_dir: Directory for report file
        filter_query: Optional filter for source collection

    Returns:
        str: Path to report file

    Example:
        >>> report_file = generate_orphan_report(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid'
        ... )
        >>> print(f"Report saved: {report_file}")
    """
    logger.info("Generating orphan detection report")

    try:
        # Find orphans
        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
            filter_query=filter_query,
        )

        # Convert ObjectIds for JSON serialization
        from yirifi_dq.core.backup import convert_objectid_to_str

        orphan_records = [convert_objectid_to_str(orphan) for orphan in orphans]

        # Build report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get total count for comparison
        query = filter_query if filter_query else {}
        total_records = source_collection.count_documents(query)

        report = {
            "timestamp": timestamp,
            "operation": "orphan_detection",
            "source_collection": {
                "name": source_collection.name,
                "database": source_collection.database.name,
                "field": source_field,
            },
            "target_collection": {
                "name": target_collection.name,
                "database": target_collection.database.name,
                "field": target_field,
            },
            "summary": {
                "total_records_checked": total_records,
                "orphans_found": len(orphans),
                "orphan_percentage": round((len(orphans) / total_records * 100), 2) if total_records > 0 else 0,
            },
            "orphan_records": orphan_records,
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"orphan_report_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        file_size = report_file.stat().st_size / 1024  # KB

        logger.info(f"Orphan report generated: {report_file}")
        print(f"✓ Orphan report generated: {report_filename}")
        print(f"  - Records checked: {total_records}")
        print(f"  - Orphans found: {len(orphans)}")
        print(f"  - Orphan percentage: {report['summary']['orphan_percentage']}%")
        print(f"  - File size: {file_size:.1f} KB")
        print(f"  - Location: {report_file}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Failed to generate orphan report: {e!s}", exc_info=True)
        print(f"❌ Failed to generate orphan report: {e!s}")
        raise


if __name__ == "__main__":
    print("Orphan Detector Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - check_orphan_status() - Check if single record is orphaned")
    print("  - find_orphans() - Find all orphaned records")
    print("  - verify_no_orphans() - Verify no orphans exist (for post-operation checks)")
    print("  - generate_orphan_report() - Generate detailed orphan detection report")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.validators.orphans import find_orphans, verify_no_orphans")
    print("  # OR")
    print("  from yirifi_dq.core.validators import find_orphans, verify_no_orphans")
    print("\nCritical relationship in this framework:")
    print("  links.link_yid (PRIMARY KEY) ↔ articlesdocuments.articleYid (FOREIGN KEY)")
