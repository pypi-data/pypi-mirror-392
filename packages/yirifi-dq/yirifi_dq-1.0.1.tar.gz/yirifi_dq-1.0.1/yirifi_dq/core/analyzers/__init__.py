"""
Analyzers Package

Collection of analysis utilities for MongoDB data quality operations.

Available analyzers:
- fields: Analyze field value distributions and patterns
- relationships: Analyze cross-collection relationships
- statistics: Generate collection and database statistics

Example:
    >>> from yirifi_dq.core.analyzers import analyze_field_distribution, analyze_foreign_keys
    >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
    >>>
    >>> client = get_client(env='PRD')
    >>> db = get_database(client, 'regdb')
    >>> collection = get_collection(db, 'links')
    >>>
    >>> # Analyze field distribution
    >>> stats = analyze_field_distribution(collection, 'status')
    >>>
    >>> # Analyze relationships
    >>> relationship_stats = analyze_foreign_keys(
    ...     source_collection=articles_collection,
    ...     target_collection=links_collection,
    ...     source_field='articleYid',
    ...     target_field='link_yid'
    ... )
"""

# Import main functions from each analyzer module for convenient access
from .fields import (
    analyze_field_distribution,
    analyze_field_nulls,
    analyze_field_types,
    generate_field_report,
)
from .relationships import (
    analyze_collection_relationships,
    analyze_foreign_keys,
    detect_broken_relationships,
    generate_relationship_map,
)
from .statistics import (
    compare_collections,
    generate_collection_stats,
    generate_database_stats,
    track_operation_metrics,
)

__all__ = [
    "analyze_collection_relationships",
    # Field analyzer
    "analyze_field_distribution",
    "analyze_field_nulls",
    "analyze_field_types",
    # Relationship analyzer
    "analyze_foreign_keys",
    "compare_collections",
    "detect_broken_relationships",
    # Statistics generator
    "generate_collection_stats",
    "generate_database_stats",
    "generate_field_report",
    "generate_relationship_map",
    "track_operation_metrics",
]
