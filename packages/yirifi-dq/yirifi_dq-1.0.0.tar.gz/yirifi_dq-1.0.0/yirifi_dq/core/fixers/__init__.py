"""
Fixers Package

Collection of utilities to fix data quality issues in MongoDB collections.

Available fixers:
- duplicates: Intelligently remove duplicate records
- orphans: Clean orphaned records (broken foreign keys)
- normalizer: Normalize field values (URLs, text, etc.)
- pipeline: Reset pipeline processing states for Airflow DAG

Example:
    >>> from yirifi_dq.core.fixers import remove_duplicates, clean_orphans, reset_pipeline_fields
    >>> from yirifi_dq.core.mongodb import get_client, get_database, get_collection
    >>>
    >>> client = get_client(env='PRD')
    >>> db = get_database(client, 'regdb')
    >>> collection = get_collection(db, 'links')
    >>>
    >>> # Remove duplicates, keeping oldest
    >>> result = remove_duplicates(
    ...     collection=collection,
    ...     field='url',
    ...     keep_strategy='oldest'
    ... )
    >>>
    >>> # Clean orphans
    >>> result = clean_orphans(
    ...     source_collection=articles_collection,
    ...     target_collection=links_collection,
    ...     source_field='articleYid',
    ...     target_field='link_yid'
    ... )
    >>>
    >>> # Reset pipeline fields
    >>> result = reset_pipeline_fields(
    ...     collection=collection,
    ...     operation_config={'field_updates': {'processing_done': False}},
    ...     input_method='csv',
    ...     input_data={'csv_path': 'stuck_links.csv'}
    ... )
"""

# Import main functions from each fixer module for convenient access
from .duplicates import remove_duplicates, select_keeper
from .normalizer import normalize_case, normalize_field, normalize_urls, normalize_whitespace
from .orphans import clean_orphans, reassign_orphans
from .pipeline import (
    find_documents_by_query,
    load_ids_from_csv,
    parse_manual_ids,
    reset_cross_collection_pipeline,
    reset_pipeline_fields,
)

__all__ = [
    # Orphan cleaner
    "clean_orphans",
    "find_documents_by_query",
    "load_ids_from_csv",
    "normalize_case",
    "normalize_field",
    # Data normalizer
    "normalize_urls",
    "normalize_whitespace",
    "parse_manual_ids",
    "reassign_orphans",
    # Duplicate remover
    "remove_duplicates",
    "reset_cross_collection_pipeline",
    # Pipeline reset
    "reset_pipeline_fields",
    "select_keeper",
]
