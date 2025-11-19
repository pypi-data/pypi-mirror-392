#!/usr/bin/env python3
"""
Post-Execution Verification Checks for MongoDB Collections

Provides comprehensive verification functions to validate data integrity
after operations complete. These checks ensure operations succeeded and
data remains consistent.

Author: Data Quality Framework
Last Updated: 2025-11-17
"""

import re
import time
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger
from yirifi_dq.utils.mongodb_helpers import mongodb_operation
from yirifi_dq.utils.retry import retry_mongodb_operation

logger = get_logger(__name__)


# ============================================================================
# Data Integrity Verification
# ============================================================================


@mongodb_operation("verify_data_integrity")
@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def verify_data_integrity(
    collection,
    field_constraints: Dict[str, Dict[str, Any]],
    sample_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Verify data integrity constraints on collection fields.

    Validates field-level constraints such as:
    - not_null: Field must exist and not be null/empty
    - unique: Field values must be unique across collection
    - regex: Field values must match pattern
    - min_length: String fields must have minimum length
    - max_length: String fields must have maximum length
    - min_value: Numeric fields must be >= minimum
    - max_value: Numeric fields must be <= maximum
    - allowed_values: Field must be in enumerated list

    Args:
        collection: MongoDB collection to verify
        field_constraints: Dict of field -> constraint definitions
            Example:
                {
                    "url": {
                        "not_null": True,
                        "unique": True,
                        "regex": r"^https?://.*"
                    },
                    "title": {
                        "not_null": True,
                        "min_length": 5,
                        "max_length": 500
                    },
                    "status": {
                        "allowed_values": ["active", "inactive", "archived"]
                    },
                    "score": {
                        "min_value": 0,
                        "max_value": 100
                    }
                }
        sample_size: Optional limit for large collections (None = check all)

    Returns:
        Dict with verification results:
            {
                "passed": bool,  # True if all constraints passed
                "violations": [  # List of constraint violations found
                    {
                        "field": str,        # Field name
                        "constraint": str,   # Constraint type (not_null, unique, etc.)
                        "count": int,        # Number of violations
                        "examples": list     # Sample violating values (max 5)
                    }
                ],
                "summary": str,  # Human-readable summary
                "checks_performed": int,  # Number of constraint checks
                "documents_checked": int,  # Number of documents examined
                "execution_time_seconds": float
            }

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> from yirifi_dq.core.validators.verification import verify_data_integrity
        >>>
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> constraints = {
        ...     "url": {"not_null": True, "unique": True, "regex": r"^https?://.*"},
        ...     "title": {"not_null": True, "min_length": 5, "max_length": 500}
        ... }
        >>>
        >>> result = verify_data_integrity(collection, constraints)
        >>> if result['passed']:
        ...     print("All integrity checks passed!")
        ... else:
        ...     for violation in result['violations']:
        ...         print(f"{violation['field']}: {violation['constraint']} failed ({violation['count']} violations)")
    """
    start_time = time.time()
    violations = []
    checks_performed = 0
    documents_checked = 0

    try:
        # Get total document count
        total_docs = collection.count_documents({})
        if total_docs == 0:
            return {
                "passed": True,
                "violations": [],
                "summary": "Collection is empty, no integrity checks performed",
                "checks_performed": 0,
                "documents_checked": 0,
                "execution_time_seconds": time.time() - start_time,
            }

        documents_checked = total_docs if sample_size is None else min(sample_size, total_docs)

        logger.info(
            f"Verifying data integrity for {len(field_constraints)} fields across "
            f"{documents_checked} documents"
        )

        # Process each field and its constraints
        for field, constraints in field_constraints.items():
            for constraint_type, constraint_value in constraints.items():
                checks_performed += 1

                if constraint_type == "not_null":
                    # Check for missing or null values
                    if constraint_value:
                        pipeline = [
                            {
                                "$match": {
                                    "$or": [
                                        {field: {"$exists": False}},
                                        {field: None},
                                        {field: ""},
                                    ]
                                }
                            },
                            {"$limit": sample_size if sample_size else 999999999},
                            {"$project": {"_id": 1, field: 1}},
                        ]
                        violations_found = list(collection.aggregate(pipeline))

                        if violations_found:
                            violation_count = len(violations_found)
                            examples = [
                                str(doc.get("_id")) for doc in violations_found[:5]
                            ]
                            violations.append({
                                "field": field,
                                "constraint": "not_null",
                                "count": violation_count,
                                "examples": examples,
                            })
                            logger.warning(
                                f"Field '{field}': {violation_count} documents with null/missing values"
                            )

                elif constraint_type == "unique":
                    # Check for duplicate values
                    if constraint_value:
                        pipeline = [
                            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
                            {"$match": {"count": {"$gt": 1}}},
                            {"$sort": {"count": -1}},
                            {"$limit": 5},
                        ]
                        duplicates = list(collection.aggregate(pipeline))

                        if duplicates:
                            duplicate_count = sum(d["count"] - 1 for d in duplicates)
                            examples = [str(d["_id"]) for d in duplicates[:5]]
                            violations.append({
                                "field": field,
                                "constraint": "unique",
                                "count": duplicate_count,
                                "examples": examples,
                            })
                            logger.warning(
                                f"Field '{field}': {duplicate_count} duplicate values found"
                            )

                elif constraint_type == "regex":
                    # Check for values not matching regex pattern
                    try:
                        pattern = re.compile(constraint_value)
                        pipeline = [
                            {"$match": {field: {"$exists": True, "$ne": None}}},
                            {"$limit": sample_size if sample_size else 999999999},
                            {"$project": {"_id": 1, field: 1}},
                        ]
                        docs = list(collection.aggregate(pipeline))

                        invalid_docs = []
                        for doc in docs:
                            value = doc.get(field)
                            if value and not pattern.match(str(value)):
                                invalid_docs.append(doc)
                                if len(invalid_docs) >= 5:
                                    break

                        if invalid_docs:
                            violation_count = len(invalid_docs)
                            examples = [str(doc.get("_id")) for doc in invalid_docs[:5]]
                            violations.append({
                                "field": field,
                                "constraint": "regex",
                                "count": violation_count,
                                "examples": examples,
                            })
                            logger.warning(
                                f"Field '{field}': {violation_count} values don't match pattern {constraint_value}"
                            )
                    except re.error as e:
                        logger.error(f"Invalid regex pattern for field '{field}': {e}")

                elif constraint_type == "min_length":
                    # Check string length minimum
                    pipeline = [
                        {
                            "$match": {
                                field: {"$exists": True},
                                "$expr": {"$lt": [{"$strLenCP": f"${field}"}, constraint_value]},
                            }
                        },
                        {"$limit": 5},
                        {"$project": {"_id": 1, field: 1}},
                    ]
                    violations_found = list(collection.aggregate(pipeline))

                    if violations_found:
                        violation_count = len(violations_found)
                        examples = [str(doc.get("_id")) for doc in violations_found[:5]]
                        violations.append({
                            "field": field,
                            "constraint": "min_length",
                            "count": violation_count,
                            "examples": examples,
                        })
                        logger.warning(
                            f"Field '{field}': {violation_count} values shorter than {constraint_value}"
                        )

                elif constraint_type == "max_length":
                    # Check string length maximum
                    pipeline = [
                        {
                            "$match": {
                                field: {"$exists": True},
                                "$expr": {"$gt": [{"$strLenCP": f"${field}"}, constraint_value]},
                            }
                        },
                        {"$limit": 5},
                        {"$project": {"_id": 1, field: 1}},
                    ]
                    violations_found = list(collection.aggregate(pipeline))

                    if violations_found:
                        violation_count = len(violations_found)
                        examples = [str(doc.get("_id")) for doc in violations_found[:5]]
                        violations.append({
                            "field": field,
                            "constraint": "max_length",
                            "count": violation_count,
                            "examples": examples,
                        })
                        logger.warning(
                            f"Field '{field}': {violation_count} values longer than {constraint_value}"
                        )

                elif constraint_type == "min_value":
                    # Check numeric minimum
                    pipeline = [
                        {"$match": {field: {"$exists": True, "$lt": constraint_value}}},
                        {"$limit": 5},
                        {"$project": {"_id": 1, field: 1}},
                    ]
                    violations_found = list(collection.aggregate(pipeline))

                    if violations_found:
                        violation_count = len(violations_found)
                        examples = [str(doc.get("_id")) for doc in violations_found[:5]]
                        violations.append({
                            "field": field,
                            "constraint": "min_value",
                            "count": violation_count,
                            "examples": examples,
                        })
                        logger.warning(
                            f"Field '{field}': {violation_count} values below minimum {constraint_value}"
                        )

                elif constraint_type == "max_value":
                    # Check numeric maximum
                    pipeline = [
                        {"$match": {field: {"$exists": True, "$gt": constraint_value}}},
                        {"$limit": 5},
                        {"$project": {"_id": 1, field: 1}},
                    ]
                    violations_found = list(collection.aggregate(pipeline))

                    if violations_found:
                        violation_count = len(violations_found)
                        examples = [str(doc.get("_id")) for doc in violations_found[:5]]
                        violations.append({
                            "field": field,
                            "constraint": "max_value",
                            "count": violation_count,
                            "examples": examples,
                        })
                        logger.warning(
                            f"Field '{field}': {violation_count} values above maximum {constraint_value}"
                        )

                elif constraint_type == "allowed_values":
                    # Check enumerated values
                    pipeline = [
                        {"$match": {field: {"$exists": True, "$nin": constraint_value}}},
                        {"$limit": 5},
                        {"$project": {"_id": 1, field: 1}},
                    ]
                    violations_found = list(collection.aggregate(pipeline))

                    if violations_found:
                        violation_count = len(violations_found)
                        examples = [str(doc.get("_id")) for doc in violations_found[:5]]
                        violations.append({
                            "field": field,
                            "constraint": "allowed_values",
                            "count": violation_count,
                            "examples": examples,
                        })
                        logger.warning(
                            f"Field '{field}': {violation_count} values not in allowed list {constraint_value}"
                        )

        # Compile results
        passed = len(violations) == 0
        execution_time = time.time() - start_time

        if passed:
            summary = (
                f"All {checks_performed} integrity checks passed across "
                f"{documents_checked} documents"
            )
            logger.info(summary)
        else:
            summary = (
                f"Found {len(violations)} constraint violations in {checks_performed} checks "
                f"across {documents_checked} documents"
            )
            logger.warning(summary)

        return {
            "passed": passed,
            "violations": violations,
            "summary": summary,
            "checks_performed": checks_performed,
            "documents_checked": documents_checked,
            "execution_time_seconds": execution_time,
        }

    except Exception as e:
        logger.error(f"Data integrity verification failed: {e}", exc_info=True)
        return {
            "passed": False,
            "violations": [],
            "summary": f"Verification failed with error: {e}",
            "checks_performed": checks_performed,
            "documents_checked": documents_checked,
            "execution_time_seconds": time.time() - start_time,
            "error": str(e),
        }


# ============================================================================
# Referential Integrity Verification
# ============================================================================


@mongodb_operation("verify_referential_integrity")
@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def verify_referential_integrity(
    primary_collection,
    foreign_collection,
    primary_field: str,
    foreign_field: str,
    check_both_directions: bool = True,
) -> Dict[str, Any]:
    """
    Verify referential integrity between two collections (foreign key validation).

    Checks that:
    1. All primary_field values in primary_collection exist in foreign_collection.foreign_field
    2. (Optional) All foreign_field values in foreign_collection exist in primary_collection.primary_field

    This is critical for maintaining data consistency after operations that
    modify or delete records with foreign key relationships.

    Args:
        primary_collection: Collection with foreign key references
        foreign_collection: Collection with primary keys
        primary_field: Field in primary collection (e.g., 'articleYid')
        foreign_field: Field in foreign collection (e.g., 'link_yid')
        check_both_directions: Also check for orphans in foreign collection (default: True)

    Returns:
        Dict with verification results:
            {
                "passed": bool,  # True if no referential integrity violations
                "orphaned_in_primary": int,  # Records in primary without matching foreign
                "orphaned_in_foreign": int,  # Records in foreign without matching primary (if checked)
                "missing_references": [  # Sample of orphaned references (max 10)
                    {
                        "collection": str,     # Which collection has orphans
                        "field": str,          # Which field
                        "value": any,          # Orphaned value
                        "document_id": str     # Document _id
                    }
                ],
                "summary": str,  # Human-readable summary
                "execution_time_seconds": float
            }

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> from yirifi_dq.core.validators.verification import verify_referential_integrity
        >>>
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> articles = get_collection(db, 'articlesdocuments')
        >>> links = get_collection(db, 'links')
        >>>
        >>> # Verify articles.articleYid -> links.link_yid relationship
        >>> result = verify_referential_integrity(
        ...     primary_collection=articles,
        ...     foreign_collection=links,
        ...     primary_field='articleYid',
        ...     foreign_field='link_yid'
        ... )
        >>>
        >>> if not result['passed']:
        ...     print(f"Found {result['orphaned_in_primary']} orphaned articles!")
        ...     for ref in result['missing_references']:
        ...         print(f"Orphan: {ref['value']} in document {ref['document_id']}")
    """
    start_time = time.time()
    missing_references = []

    try:
        primary_name = primary_collection.name
        foreign_name = foreign_collection.name

        logger.info(
            f"Verifying referential integrity: {primary_name}.{primary_field} -> "
            f"{foreign_name}.{foreign_field}"
        )

        # Step 1: Find orphans in primary collection
        # (primary_field values that don't exist in foreign_field)

        # Get all unique foreign key values from foreign collection
        foreign_keys = set(
            doc[foreign_field]
            for doc in foreign_collection.find({foreign_field: {"$exists": True}}, {foreign_field: 1})
            if foreign_field in doc and doc[foreign_field] is not None
        )

        logger.debug(f"Found {len(foreign_keys)} unique values in {foreign_name}.{foreign_field}")

        # Find primary records with references not in foreign keys
        primary_orphans = list(
            primary_collection.find(
                {
                    primary_field: {"$exists": True, "$nin": list(foreign_keys)},
                },
                {primary_field: 1}
            ).limit(10)
        )

        orphaned_in_primary = len(primary_orphans)

        if primary_orphans:
            for doc in primary_orphans[:10]:
                missing_references.append({
                    "collection": primary_name,
                    "field": primary_field,
                    "value": doc.get(primary_field),
                    "document_id": str(doc.get("_id")),
                })
            logger.warning(
                f"Found {orphaned_in_primary} orphaned references in {primary_name}.{primary_field}"
            )

        # Step 2: Optionally check reverse direction (orphans in foreign collection)
        orphaned_in_foreign = 0
        if check_both_directions:
            # Get all unique primary key values from primary collection
            primary_keys = set(
                doc[primary_field]
                for doc in primary_collection.find(
                    {primary_field: {"$exists": True}}, {primary_field: 1}
                )
                if primary_field in doc and doc[primary_field] is not None
            )

            logger.debug(f"Found {len(primary_keys)} unique values in {primary_name}.{primary_field}")

            # Find foreign records not referenced by any primary record
            foreign_orphans = list(
                foreign_collection.find(
                    {
                        foreign_field: {"$exists": True, "$nin": list(primary_keys)},
                    },
                    {foreign_field: 1}
                ).limit(10)
            )

            orphaned_in_foreign = len(foreign_orphans)

            if foreign_orphans:
                for doc in foreign_orphans[:10]:
                    missing_references.append({
                        "collection": foreign_name,
                        "field": foreign_field,
                        "value": doc.get(foreign_field),
                        "document_id": str(doc.get("_id")),
                    })
                logger.warning(
                    f"Found {orphaned_in_foreign} unreferenced records in {foreign_name}.{foreign_field}"
                )

        # Compile results
        passed = orphaned_in_primary == 0 and orphaned_in_foreign == 0
        execution_time = time.time() - start_time

        if passed:
            summary = (
                f"Referential integrity verified: No orphaned references between "
                f"{primary_name}.{primary_field} and {foreign_name}.{foreign_field}"
            )
            logger.info(summary)
        else:
            summary = (
                f"Referential integrity violations found: "
                f"{orphaned_in_primary} orphans in {primary_name}, "
                f"{orphaned_in_foreign} orphans in {foreign_name}"
            )
            logger.warning(summary)

        return {
            "passed": passed,
            "orphaned_in_primary": orphaned_in_primary,
            "orphaned_in_foreign": orphaned_in_foreign,
            "missing_references": missing_references,
            "summary": summary,
            "execution_time_seconds": execution_time,
        }

    except Exception as e:
        logger.error(f"Referential integrity verification failed: {e}", exc_info=True)
        return {
            "passed": False,
            "orphaned_in_primary": 0,
            "orphaned_in_foreign": 0,
            "missing_references": [],
            "summary": f"Verification failed with error: {e}",
            "execution_time_seconds": time.time() - start_time,
            "error": str(e),
        }


# ============================================================================
# Schema Validation
# ============================================================================


@mongodb_operation("verify_schema")
@retry_mongodb_operation(max_attempts=3, min_wait=1, max_wait=10)
def verify_schema(
    collection,
    required_fields: List[str],
    optional_fields: Optional[List[str]] = None,
    strict_mode: bool = False,
    sample_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Verify document schema compliance in a collection.

    Validates that documents conform to expected structure:
    - All required_fields are present in every document
    - (Optional) Only required + optional fields exist (no unexpected fields)
    - Provides statistics on field presence

    Args:
        collection: MongoDB collection to verify
        required_fields: List of fields that MUST exist in all documents
        optional_fields: List of fields that MAY exist (default: allow any)
        strict_mode: If True, fail on any unexpected fields (default: False)
        sample_size: Optional limit for large collections (None = check all)

    Returns:
        Dict with verification results:
            {
                "passed": bool,  # True if all documents comply with schema
                "documents_checked": int,  # Number of documents examined
                "missing_required_fields": {  # Required fields missing from documents
                    "field_name": int  # Count of documents missing this field
                },
                "unexpected_fields": {  # Fields found that aren't in required/optional lists
                    "field_name": int  # Count of documents with this field
                },
                "field_statistics": {  # Presence statistics for all fields
                    "field_name": {
                        "present_count": int,
                        "present_percentage": float,
                        "is_required": bool
                    }
                },
                "summary": str,  # Human-readable summary
                "execution_time_seconds": float
            }

    Example:
        >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
        >>> from yirifi_dq.core.validators.verification import verify_schema
        >>>
        >>> client = get_client(env='PRD')
        >>> db = get_database(client, 'regdb')
        >>> collection = get_collection(db, 'links')
        >>>
        >>> # Verify schema compliance
        >>> result = verify_schema(
        ...     collection=collection,
        ...     required_fields=['url', 'title', 'link_yid', 'created_at'],
        ...     optional_fields=['description', 'tags', 'metadata', 'slug']
        ... )
        >>>
        >>> if result['passed']:
        ...     print("All documents comply with schema!")
        ... else:
        ...     if result['missing_required_fields']:
        ...         print("Missing required fields:")
        ...         for field, count in result['missing_required_fields'].items():
        ...             print(f"  {field}: {count} documents")
        ...     if result['unexpected_fields']:
        ...         print("Unexpected fields found:")
        ...         for field, count in result['unexpected_fields'].items():
        ...             print(f"  {field}: {count} documents")
    """
    start_time = time.time()
    missing_required_fields = {}
    unexpected_fields = {}
    field_statistics = {}

    try:
        # Get total document count
        total_docs = collection.count_documents({})
        if total_docs == 0:
            return {
                "passed": True,
                "documents_checked": 0,
                "missing_required_fields": {},
                "unexpected_fields": {},
                "field_statistics": {},
                "summary": "Collection is empty, no schema checks performed",
                "execution_time_seconds": time.time() - start_time,
            }

        documents_checked = total_docs if sample_size is None else min(sample_size, total_docs)

        logger.info(
            f"Verifying schema compliance for {documents_checked} documents "
            f"({len(required_fields)} required fields, "
            f"{len(optional_fields or [])} optional fields)"
        )

        # Build expected field set
        expected_fields = set(required_fields)
        if optional_fields:
            expected_fields.update(optional_fields)

        # Sample documents
        sample_query = {} if sample_size is None else {}
        documents = list(collection.find(sample_query).limit(sample_size or 999999999))

        # Check each document
        all_fields_seen = set()
        for doc in documents:
            doc_fields = set(doc.keys()) - {"_id"}  # Exclude _id
            all_fields_seen.update(doc_fields)

            # Check required fields
            for field in required_fields:
                if field not in doc or doc[field] is None:
                    missing_required_fields[field] = missing_required_fields.get(field, 0) + 1

            # Check for unexpected fields in strict mode
            if strict_mode:
                for field in doc_fields:
                    if field not in expected_fields and field != "_id":
                        unexpected_fields[field] = unexpected_fields.get(field, 0) + 1

        # Calculate field statistics
        for field in all_fields_seen:
            present_count = collection.count_documents({field: {"$exists": True, "$ne": None}})
            field_statistics[field] = {
                "present_count": present_count,
                "present_percentage": (present_count / documents_checked) * 100,
                "is_required": field in required_fields,
            }

        # Compile results
        passed = len(missing_required_fields) == 0 and (not strict_mode or len(unexpected_fields) == 0)
        execution_time = time.time() - start_time

        if passed:
            summary = (
                f"Schema compliance verified: All {documents_checked} documents conform to schema "
                f"({len(required_fields)} required fields)"
            )
            logger.info(summary)
        else:
            issues = []
            if missing_required_fields:
                issues.append(
                    f"{len(missing_required_fields)} required fields missing from some documents"
                )
            if unexpected_fields and strict_mode:
                issues.append(
                    f"{len(unexpected_fields)} unexpected fields found"
                )
            summary = (
                f"Schema compliance issues: {', '.join(issues)} in {documents_checked} documents"
            )
            logger.warning(summary)

        return {
            "passed": passed,
            "documents_checked": documents_checked,
            "missing_required_fields": missing_required_fields,
            "unexpected_fields": unexpected_fields,
            "field_statistics": field_statistics,
            "summary": summary,
            "execution_time_seconds": execution_time,
        }

    except Exception as e:
        logger.error(f"Schema verification failed: {e}", exc_info=True)
        return {
            "passed": False,
            "documents_checked": 0,
            "missing_required_fields": {},
            "unexpected_fields": {},
            "field_statistics": {},
            "summary": f"Verification failed with error: {e}",
            "execution_time_seconds": time.time() - start_time,
            "error": str(e),
        }


# ============================================================================
# Export All
# ============================================================================

__all__ = [
    "verify_data_integrity",
    "verify_referential_integrity",
    "verify_schema",
]
