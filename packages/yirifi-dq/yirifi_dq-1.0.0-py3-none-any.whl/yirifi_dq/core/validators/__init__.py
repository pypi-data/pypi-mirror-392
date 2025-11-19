"""
Validators Package

Collection of validation utilities for MongoDB data quality operations.

Available validators:
- duplicates: Find and analyze duplicate records
- orphans: Detect orphaned records (broken foreign keys)
- consistency: Validate field values against rules
- verification: Post-execution verification checks (NEW)

Example:
    >>> from yirifi_dq.core.validators import find_duplicates, find_orphans
    >>> from yirifi_dq.core.validators import verify_data_integrity, verify_referential_integrity, verify_schema
    >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
    >>>
    >>> client = get_client(env='PRD')
    >>> db = get_database(client, 'regdb')
    >>> collection = get_collection(db, 'links')
    >>>
    >>> # Find duplicates
    >>> duplicates = find_duplicates(collection, 'url')
    >>>
    >>> # Find orphans
    >>> orphans = find_orphans(
    ...     source_collection=articles_collection,
    ...     target_collection=links_collection,
    ...     source_field='articleYid',
    ...     target_field='link_yid'
    ... )
    >>>
    >>> # Verify data integrity
    >>> result = verify_data_integrity(
    ...     collection,
    ...     field_constraints={'url': {'not_null': True, 'unique': True}}
    ... )
"""

# Import main functions from each validator module for convenient access
from .consistency import (
    validate_constraints,
    validate_field_format,
    validate_field_types,
    validate_required_fields,
)
from .duplicates import (
    analyze_duplicates,
    export_duplicates_report,
    find_composite_duplicates,
    find_duplicates,
    validate_duplicates,
)
from .orphans import check_orphan_status, find_orphans, generate_orphan_report, verify_no_orphans
from .verification import (
    verify_data_integrity,
    verify_referential_integrity,
    verify_schema,
)

__all__ = [
    "analyze_duplicates",
    "check_orphan_status",
    "export_duplicates_report",
    "find_composite_duplicates",
    "find_duplicates",
    "find_orphans",
    "generate_orphan_report",
    "validate_constraints",
    "validate_duplicates",
    "validate_field_format",
    "validate_field_types",
    "validate_required_fields",
    "verify_data_integrity",
    "verify_no_orphans",
    "verify_referential_integrity",
    "verify_schema",
]
