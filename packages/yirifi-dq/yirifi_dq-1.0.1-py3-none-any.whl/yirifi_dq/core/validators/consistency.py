#!/usr/bin/env python3
"""
Consistency Checker for MongoDB Collections

Validates field values against business rules and data quality standards.
Ensures data consistency across collections.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import re
from typing import Any, Callable, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_field_format(
    collection,
    field_name: str,
    pattern: str,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Validate field values against a regex pattern.

    Args:
        collection: MongoDB collection
        field_name: Field to validate
        pattern: Regex pattern to match against
        filter_query: Optional filter for documents to check
        test_mode: If True, adds test mode warnings
        limit: Optional limit on number of documents to check

    Returns:
        Dict with validation results

    Example:
        >>> # Validate email format
        >>> results = validate_field_format(
        ...     collection=users_collection,
        ...     field_name='email',
        ...     pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        ... )
        >>> print(f"Valid: {results['valid_count']}, Invalid: {results['invalid_count']}")
    """
    logger.info(f"Validating field format: {field_name} against pattern: {pattern}")

    try:
        regex = re.compile(pattern)
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Checking {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Validating {len(documents)} documents")

        valid_count = 0
        invalid_count = 0
        null_count = 0
        invalid_examples = []

        for doc in documents:
            value = doc.get(field_name)

            if value is None:
                null_count += 1
                continue

            # Convert to string for pattern matching
            value_str = str(value)

            if regex.match(value_str):
                valid_count += 1
            else:
                invalid_count += 1
                # Keep first 10 invalid examples
                if len(invalid_examples) < 10:
                    invalid_examples.append(
                        {
                            "id": str(doc.get("_id")),
                            "value": value_str[:100],  # Truncate long values
                        }
                    )

        results = {
            "field": field_name,
            "pattern": pattern,
            "total_checked": len(documents),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "null_count": null_count,
            "invalid_examples": invalid_examples,
        }

        logger.info(f"Validation complete: {valid_count} valid, {invalid_count} invalid, {null_count} null")
        print("✓ Field format validation complete:")
        print(f"  - Field: {field_name}")
        print(f"  - Total checked: {len(documents)}")
        print(f"  - Valid: {valid_count}")
        print(f"  - Invalid: {invalid_count}")
        print(f"  - Null/Missing: {null_count}")

        return results

    except Exception as e:
        logger.error(f"Field format validation failed: {e!s}", exc_info=True)
        print(f"❌ Field format validation failed: {e!s}")
        raise


def validate_required_fields(
    collection,
    required_fields: List[str],
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Validate that required fields exist and are not null.

    Args:
        collection: MongoDB collection
        required_fields: List of field names that must exist
        filter_query: Optional filter for documents to check
        test_mode: If True, adds test mode warnings
        limit: Optional limit on number of documents to check

    Returns:
        Dict with validation results

    Example:
        >>> # Check required fields exist
        >>> results = validate_required_fields(
        ...     collection=users_collection,
        ...     required_fields=['email', 'username', 'created_at']
        ... )
        >>> if results['missing_fields_count'] > 0:
        ...     print(f"⚠️  {results['missing_fields_count']} records have missing fields")
    """
    logger.info(f"Validating required fields: {', '.join(required_fields)}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Checking {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Validating {len(documents)} documents")

        missing_by_field = dict.fromkeys(required_fields, 0)
        records_with_missing = []

        for doc in documents:
            missing_in_doc = []

            for field in required_fields:
                value = doc.get(field)
                if value is None or value == "":
                    missing_by_field[field] += 1
                    missing_in_doc.append(field)

            if missing_in_doc:
                records_with_missing.append({"id": str(doc.get("_id")), "missing_fields": missing_in_doc})

        results = {
            "required_fields": required_fields,
            "total_checked": len(documents),
            "missing_fields_count": len(records_with_missing),
            "missing_by_field": missing_by_field,
            "records_with_missing": records_with_missing[:10],  # First 10 examples
        }

        logger.info(f"Validation complete: {len(records_with_missing)} records with missing fields")
        print("✓ Required fields validation complete:")
        print(f"  - Total checked: {len(documents)}")
        print(f"  - Records with missing fields: {len(records_with_missing)}")

        for field, count in missing_by_field.items():
            if count > 0:
                print(f"  - Missing '{field}': {count} records")

        return results

    except Exception as e:
        logger.error(f"Required fields validation failed: {e!s}", exc_info=True)
        print(f"❌ Required fields validation failed: {e!s}")
        raise


def validate_field_types(
    collection,
    field_types: Dict[str, type],
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Validate that fields have expected data types.

    Args:
        collection: MongoDB collection
        field_types: Dict mapping field names to expected Python types
        filter_query: Optional filter for documents to check
        test_mode: If True, adds test mode warnings
        limit: Optional limit on number of documents to check

    Returns:
        Dict with validation results

    Example:
        >>> # Validate field types
        >>> results = validate_field_types(
        ...     collection=users_collection,
        ...     field_types={
        ...         'email': str,
        ...         'age': int,
        ...         'is_active': bool
        ...     }
        ... )
    """
    logger.info(f"Validating field types: {', '.join(field_types.keys())}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Checking {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Validating {len(documents)} documents")

        type_errors_by_field = dict.fromkeys(field_types.keys(), 0)
        records_with_errors = []

        for doc in documents:
            errors_in_doc = []

            for field, expected_type in field_types.items():
                value = doc.get(field)

                # Skip null values (use validate_required_fields for null checks)
                if value is None:
                    continue

                if not isinstance(value, expected_type):
                    type_errors_by_field[field] += 1
                    errors_in_doc.append(
                        {
                            "field": field,
                            "expected_type": expected_type.__name__,
                            "actual_type": type(value).__name__,
                            "value": str(value)[:100],
                        }
                    )

            if errors_in_doc:
                records_with_errors.append({"id": str(doc.get("_id")), "type_errors": errors_in_doc})

        results = {
            "field_types": {k: v.__name__ for k, v in field_types.items()},
            "total_checked": len(documents),
            "records_with_errors": len(records_with_errors),
            "type_errors_by_field": type_errors_by_field,
            "error_examples": records_with_errors[:10],  # First 10 examples
        }

        logger.info(f"Validation complete: {len(records_with_errors)} records with type errors")
        print("✓ Field type validation complete:")
        print(f"  - Total checked: {len(documents)}")
        print(f"  - Records with type errors: {len(records_with_errors)}")

        for field, count in type_errors_by_field.items():
            if count > 0:
                print(f"  - Type errors in '{field}': {count} records")

        return results

    except Exception as e:
        logger.error(f"Field type validation failed: {e!s}", exc_info=True)
        print(f"❌ Field type validation failed: {e!s}")
        raise


def validate_constraints(
    collection,
    constraints: Dict[str, Callable],
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Validate custom business rule constraints.

    Args:
        collection: MongoDB collection
        constraints: Dict mapping field names to validation functions
        filter_query: Optional filter for documents to check
        test_mode: If True, adds test mode warnings
        limit: Optional limit on number of documents to check

    Returns:
        Dict with validation results

    Example:
        >>> # Define custom constraints
        >>> def is_valid_age(value):
        ...     return value is not None and 0 <= value <= 150
        >>>
        >>> def is_valid_email(value):
        ...     return value and '@' in value and '.' in value
        >>>
        >>> results = validate_constraints(
        ...     collection=users_collection,
        ...     constraints={
        ...         'age': is_valid_age,
        ...         'email': is_valid_email
        ...     }
        ... )
    """
    logger.info(f"Validating custom constraints: {', '.join(constraints.keys())}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Checking {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Validating {len(documents)} documents")

        violations_by_field = dict.fromkeys(constraints.keys(), 0)
        records_with_violations = []

        for doc in documents:
            violations_in_doc = []

            for field, validator in constraints.items():
                value = doc.get(field)

                try:
                    is_valid = validator(value)
                    if not is_valid:
                        violations_by_field[field] += 1
                        violations_in_doc.append(
                            {
                                "field": field,
                                "value": str(value)[:100] if value is not None else "None",
                                "reason": "Constraint violation",
                            }
                        )
                except Exception as e:
                    violations_by_field[field] += 1
                    violations_in_doc.append(
                        {
                            "field": field,
                            "value": str(value)[:100] if value is not None else "None",
                            "reason": f"Validation error: {e!s}",
                        }
                    )

            if violations_in_doc:
                records_with_violations.append({"id": str(doc.get("_id")), "violations": violations_in_doc})

        results = {
            "constraints": list(constraints.keys()),
            "total_checked": len(documents),
            "records_with_violations": len(records_with_violations),
            "violations_by_field": violations_by_field,
            "violation_examples": records_with_violations[:10],  # First 10 examples
        }

        logger.info(f"Validation complete: {len(records_with_violations)} records with constraint violations")
        print("✓ Constraint validation complete:")
        print(f"  - Total checked: {len(documents)}")
        print(f"  - Records with violations: {len(records_with_violations)}")

        for field, count in violations_by_field.items():
            if count > 0:
                print(f"  - Violations in '{field}': {count} records")

        return results

    except Exception as e:
        logger.error(f"Constraint validation failed: {e!s}", exc_info=True)
        print(f"❌ Constraint validation failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Consistency Checker Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - validate_field_format() - Validate field against regex pattern")
    print("  - validate_required_fields() - Check required fields exist")
    print("  - validate_field_types() - Validate field data types")
    print("  - validate_constraints() - Validate custom business rules")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.validators.consistency import validate_field_format, validate_required_fields")
    print("  # OR")
    print("  from yirifi_dq.core.validators import validate_field_format, validate_required_fields")
