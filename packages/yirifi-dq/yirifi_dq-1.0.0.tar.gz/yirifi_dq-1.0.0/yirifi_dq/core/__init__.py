"""
Core Package

Collection of core utilities for MongoDB data quality operations.

This package contains:
- validators: Data validation utilities (duplicates, orphans, consistency)
- fixers: Data modification utilities (remove duplicates, clean orphans, normalize)
- analyzers: Data analysis utilities (statistics, relationships, field analysis)
- generators: Data generation utilities (slugs, IDs)
- backup: Backup and restore utilities
- mongodb: MongoDB connection utilities
- base_operation: Base classes for complex operations

All utilities are re-exported at the package level for convenient access.

Example:
    >>> from yirifi_dq.core.validators import find_duplicates
    >>> from yirifi_dq.core.fixers import remove_duplicates
    >>> from yirifi_dq.core.mongodb import get_client
    >>> from yirifi_dq.core.backup import backup_documents
    >>> from yirifi_dq.core.analyzers import analyze_field_distribution
"""

# Base classes
from yirifi_dq.core.base_operation import BaseOperation

# Validators - Import all validation utilities
from yirifi_dq.core.validators import (
    analyze_duplicates,
    check_orphan_status,
    export_duplicates_report,
    find_composite_duplicates,
    find_duplicates,
    find_orphans,
    generate_orphan_report,
    validate_constraints,
    validate_duplicates,
    validate_field_format,
    validate_field_types,
    validate_required_fields,
    verify_no_orphans,
)

# Fixers - Import all data fixing utilities
from yirifi_dq.core.fixers import (
    clean_orphans,
    find_documents_by_query,
    load_ids_from_csv,
    normalize_case,
    normalize_field,
    normalize_urls,
    normalize_whitespace,
    parse_manual_ids,
    reassign_orphans,
    remove_duplicates,
    reset_cross_collection_pipeline,
    reset_pipeline_fields,
    select_keeper,
)

# Analyzers - Import all analysis utilities
from yirifi_dq.core.analyzers import (
    analyze_collection_relationships,
    analyze_field_distribution,
    analyze_field_nulls,
    analyze_field_types,
    analyze_foreign_keys,
    compare_collections,
    detect_broken_relationships,
    generate_collection_stats,
    generate_database_stats,
    generate_field_report,
    generate_relationship_map,
    track_operation_metrics,
)

# Generators - Import all generation utilities
from yirifi_dq.core.generators import SlugGenerator, generate_slug_for_collection

# Backup - Import all backup utilities
from yirifi_dq.core.backup import (
    backup_documents,
    convert_objectid_to_str,
    create_cross_collection_backup,
    restore_documents,
    verify_backup,
)

# MongoDB - Import all MongoDB utilities
from yirifi_dq.core.mongodb import get_client, get_collection, get_database

__all__ = [
    # Base classes
    "BaseOperation",
    # Validators
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
    "verify_no_orphans",
    # Fixers
    "clean_orphans",
    "find_documents_by_query",
    "load_ids_from_csv",
    "normalize_case",
    "normalize_field",
    "normalize_urls",
    "normalize_whitespace",
    "parse_manual_ids",
    "reassign_orphans",
    "remove_duplicates",
    "reset_cross_collection_pipeline",
    "reset_pipeline_fields",
    "select_keeper",
    # Analyzers
    "analyze_collection_relationships",
    "analyze_field_distribution",
    "analyze_field_nulls",
    "analyze_field_types",
    "analyze_foreign_keys",
    "compare_collections",
    "detect_broken_relationships",
    "generate_collection_stats",
    "generate_database_stats",
    "generate_field_report",
    "generate_relationship_map",
    "track_operation_metrics",
    # Generators
    "SlugGenerator",
    "generate_slug_for_collection",
    # Backup
    "backup_documents",
    "convert_objectid_to_str",
    "create_cross_collection_backup",
    "restore_documents",
    "verify_backup",
    # MongoDB
    "get_client",
    "get_collection",
    "get_database",
]
