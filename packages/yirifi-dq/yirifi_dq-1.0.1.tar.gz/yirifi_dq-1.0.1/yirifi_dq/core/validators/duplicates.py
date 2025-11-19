#!/usr/bin/env python3
"""
Duplicate Detector for MongoDB Collections

Provides utilities to find and analyze duplicate records across collection fields.
Uses MongoDB aggregation pipelines for efficient duplicate detection.

Author: Data Quality Framework
Last Updated: 2025-11-17 (Refactored to use functional patterns)
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from yirifi_dq.models.results import ValidationResult
from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.mongodb_helpers import mongodb_operation
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


# ============================================================================
# NEW: Functional Pattern with Pydantic Models (2025-11-17 Refactoring)
# ============================================================================


@mongodb_operation("validate_duplicates")
@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def validate_duplicates(collection, field_name: str, test_mode: bool = False, limit: Optional[int] = None) -> ValidationResult:
    """
    Validate collection for duplicate values (NEW: Returns Pydantic model).

    This is the NEW functional approach using @mongodb_operation decorator
    and ValidationResult Pydantic model. Provides same functionality as
    find_duplicates() but with type safety and standardized results.

    Benefits over old approach:
    - Automatic logging, timing, error handling (@mongodb_operation)
    - Type-safe results (ValidationResult Pydantic model)
    - Standardized format for orchestrator integration
    - Better testability

    Args:
        collection: MongoDB collection
        field_name: Field to check for duplicates
        test_mode: If True, limits results for testing
        limit: Optional limit on number of duplicates to return

    Returns:
        ValidationResult: Pydantic model with:
            - validator_name: "validate_duplicates"
            - collection_name: Collection name
            - database_name: Database name
            - issues_found: Number of duplicate values
            - issue_details: List of {value, count, docs} dicts
            - execution_time_seconds: Time taken
            - summary: Statistics about duplicates
            - timestamp: When validation was performed

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> from yirifi_dq.core.validators.duplicates import validate_duplicates
        >>>
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> # New approach - returns Pydantic model
        >>> result = validate_duplicates(collection, 'url')
        >>> print(f"Found {result.issues_found} duplicate URLs")
        >>> print(f"Took {result.execution_time_seconds:.2f}s")
        >>> print(f"Summary: {result.summary}")
        >>>
        >>> # Access details
        >>> for issue in result.issue_details:
        ...     print(f"{issue['value']}: {issue['count']} duplicates")
    """
    start_time = time.time()

    # Build aggregation pipeline
    pipeline = [
        {"$group": {"_id": f"${field_name}", "count": {"$sum": 1}, "docs": {"$push": "$$ROOT"}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}},
    ]

    # Execute aggregation
    results = list(collection.aggregate(pipeline))

    # Apply limit if specified
    if limit and len(results) > limit:
        results = results[:limit]

    # Transform to issue_details format
    issue_details = []
    total_duplicate_docs = 0

    for item in results:
        issue_details.append(
            {
                "value": item["_id"],
                "count": item["count"],
                "docs": item["docs"] if not test_mode else item["docs"][:2],  # Limit docs in test mode
            }
        )
        total_duplicate_docs += item["count"]

    # Calculate execution time
    execution_time = time.time() - start_time

    # Create summary
    summary = {
        "total_duplicate_values": len(results),
        "total_duplicate_documents": total_duplicate_docs,
        "field_validated": field_name,
        "test_mode": test_mode,
        "limit_applied": limit is not None,
    }

    # Return standardized ValidationResult
    return ValidationResult(
        validator_name="validate_duplicates",
        collection_name=collection.name,
        database_name=collection.database.name,
        issues_found=len(results),
        issue_details=issue_details,
        execution_time_seconds=execution_time,
        summary=summary,
    )


# ============================================================================
# LEGACY: Original Functions (Maintained for Backward Compatibility)
# ============================================================================


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def find_duplicates(
    collection,
    field_name: str,
    return_details: bool = False,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Union[List[Any], Dict[Any, List[Dict]]]:
    """
    Find duplicate values in a collection field.

    Args:
        collection: MongoDB collection
        field_name: Field to check for duplicates
        return_details: If True, return full documents; if False, just values
        test_mode: If True, limits results for testing
        limit: Optional limit on number of duplicates to return

    Returns:
        If return_details=False: List of duplicate values
        If return_details=True: Dict of {value: [documents]}

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> # Simple list of duplicate values
        >>> duplicate_urls = find_duplicates(collection, 'url')
        >>> print(f"Found {len(duplicate_urls)} duplicate URLs")
        >>>
        >>> # With full document details
        >>> duplicates_with_docs = find_duplicates(collection, 'url', return_details=True)
        >>> for url, docs in duplicates_with_docs.items():
        ...     print(f"{url}: {len(docs)} duplicates")
    """
    logger.info(f"Finding duplicates in field: {field_name}")

    try:
        pipeline = [
            {
                "$group": {
                    "_id": f"${field_name}",
                    "count": {"$sum": 1},
                    "docs": {"$push": "$$ROOT"},
                }
            },
            {"$match": {"count": {"$gt": 1}}},
            {"$sort": {"count": -1}},
        ]

        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} duplicate {field_name} values")

        # Apply limit if specified
        if limit and len(results) > limit:
            logger.info(f"Applying limit: {limit}")
            results = results[:limit]

        if test_mode:
            print(f"⚠️  TEST MODE: Found {len(results)} duplicate {field_name} values")

        if not return_details:
            # Just return the duplicate values
            duplicate_values = [item["_id"] for item in results]
            logger.info(f"Returning {len(duplicate_values)} duplicate values")
            return duplicate_values
        else:
            # Return dict with full details
            duplicates = {}
            for item in results:
                duplicates[item["_id"]] = item["docs"]

            total_docs = sum(len(docs) for docs in duplicates.values())
            logger.info(f"Returning {len(duplicates)} duplicate values with {total_docs} total documents")

            return duplicates

    except Exception as e:
        logger.error(f"Failed to find duplicates: {e!s}", exc_info=True)
        print(f"❌ Failed to find duplicates: {e!s}")
        raise


@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def find_composite_duplicates(
    collection,
    fields: List[str],
    return_details: bool = False,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Union[List[Dict], Dict[str, List[Dict]]]:
    """
    Find duplicates based on combination of multiple fields.

    Args:
        collection: MongoDB collection
        fields: List of field names (e.g., ['first_name', 'last_name'])
        return_details: If True, return full documents
        test_mode: If True, limits results for testing
        limit: Optional limit on number of duplicates to return

    Returns:
        List or dict of duplicates

    Example:
        >>> # Find users with same first and last name
        >>> duplicates = find_composite_duplicates(
        ...     collection=users_collection,
        ...     fields=['first_name', 'last_name'],
        ...     return_details=True
        ... )
        >>> for key, docs in duplicates.items():
        ...     print(f"{key}: {len(docs)} duplicates")
    """
    logger.info(f"Finding composite duplicates on fields: {', '.join(fields)}")

    try:
        # Build composite key
        group_id = {field: f"${field}" for field in fields}

        pipeline = [
            {"$group": {"_id": group_id, "count": {"$sum": 1}, "docs": {"$push": "$$ROOT"}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$sort": {"count": -1}},
        ]

        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} composite duplicates")

        # Apply limit if specified
        if limit and len(results) > limit:
            logger.info(f"Applying limit: {limit}")
            results = results[:limit]

        if test_mode:
            print(f"⚠️  TEST MODE: Found {len(results)} composite duplicates")

        if not return_details:
            return [item["_id"] for item in results]
        else:
            duplicates = {}
            for item in results:
                # Create readable key
                key = " + ".join([str(v) for v in item["_id"].values()])
                duplicates[key] = item["docs"]

            logger.info(f"Returning {len(duplicates)} composite duplicate groups")
            return duplicates

    except Exception as e:
        logger.error(f"Failed to find composite duplicates: {e!s}", exc_info=True)
        print(f"❌ Failed to find composite duplicates: {e!s}")
        raise


def analyze_duplicates(collection, field_name: str) -> Dict[str, Any]:
    """
    Generate summary statistics about duplicates.

    Args:
        collection: MongoDB collection
        field_name: Field to analyze for duplicates

    Returns:
        Dict with duplicate statistics

    Example:
        >>> stats = analyze_duplicates(collection, 'url')
        >>> print(f"Duplicate values: {stats['duplicate_values']}")
        >>> print(f"Total duplicate records: {stats['duplicate_records']}")
        >>> print(f"Most duplicated: {stats['most_duplicated']['value']} ({stats['most_duplicated']['count']} times)")
    """
    logger.info(f"Analyzing duplicates for field: {field_name}")

    try:
        duplicates = find_duplicates(collection, field_name, return_details=True)

        if not duplicates:
            logger.info("No duplicates found")
            return {
                "field": field_name,
                "duplicate_values": 0,
                "duplicate_records": 0,
                "max_duplicates_per_value": 0,
                "most_duplicated": None,
            }

        total_duplicate_values = len(duplicates)
        total_duplicate_records = sum(len(docs) for docs in duplicates.values())
        max_duplicates = max(len(docs) for docs in duplicates.values())

        # Find most duplicated value
        most_duplicated = max(duplicates.items(), key=lambda x: len(x[1]))

        summary = {
            "field": field_name,
            "duplicate_values": total_duplicate_values,
            "duplicate_records": total_duplicate_records,
            "max_duplicates_per_value": max_duplicates,
            "most_duplicated": {"value": most_duplicated[0], "count": len(most_duplicated[1])},
        }

        logger.info(f"Analysis complete: {total_duplicate_values} duplicate values, {total_duplicate_records} total records")

        print(f"\nDuplicate Analysis for '{field_name}':")
        print(f"  - Duplicate values: {total_duplicate_values}")
        print(f"  - Total duplicate records: {total_duplicate_records}")
        print(f"  - Max duplicates per value: {max_duplicates}")
        print(f"  - Most duplicated: {summary['most_duplicated']['value'][:60]}... ({summary['most_duplicated']['count']} occurrences)")

        return summary

    except Exception as e:
        logger.error(f"Failed to analyze duplicates: {e!s}", exc_info=True)
        print(f"❌ Failed to analyze duplicates: {e!s}")
        raise


def export_duplicates_report(collection, field_name: str, output_dir: Optional[Path] = None) -> str:
    """
    Export detailed duplicates report to JSON file.

    Args:
        collection: MongoDB collection
        field_name: Field to check for duplicates
        output_dir: Directory for output file (defaults to ./output)

    Returns:
        str: Path to report file

    Example:
        >>> report_file = export_duplicates_report(collection, 'url')
        >>> print(f"Report saved: {report_file}")
    """
    logger.info(f"Exporting duplicates report for field: {field_name}")

    try:
        from datetime import datetime

        # Get duplicates with full details
        duplicates = find_duplicates(collection, field_name, return_details=True)

        # Get summary statistics
        stats = analyze_duplicates(collection, field_name)

        # Prepare report data
        detailed_duplicates = []
        for value, docs in duplicates.items():
            # Convert ObjectId to string for JSON serialization
            from yirifi_dq.core.backup import convert_objectid_to_str

            detailed_duplicates.append(
                {
                    "value": value,
                    "count": len(docs),
                    "documents": [convert_objectid_to_str(doc) for doc in docs],
                }
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "collection": collection.name,
            "database": collection.database.name,
            "field": field_name,
            "summary": stats,
            "duplicates": detailed_duplicates,
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"duplicates_{field_name}_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        file_size = report_file.stat().st_size / 1024  # KB

        logger.info(f"Report exported: {report_file}")
        print(f"✓ Duplicates report exported: {report_filename}")
        print(f"  - File size: {file_size:.1f} KB")
        print(f"  - Location: {report_file}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Failed to export duplicates report: {e!s}", exc_info=True)
        print(f"❌ Failed to export duplicates report: {e!s}")
        raise


if __name__ == "__main__":
    print("Duplicate Detector Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - find_duplicates() - Find duplicate values in a field")
    print("  - find_composite_duplicates() - Find duplicates across multiple fields")
    print("  - analyze_duplicates() - Generate duplicate statistics")
    print("  - export_duplicates_report() - Export detailed report to JSON")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.validators.duplicates import find_duplicates, analyze_duplicates")
    print("  # OR")
    print("  from yirifi_dq.core.validators import find_duplicates, analyze_duplicates")
