#!/usr/bin/env python3
"""
Relationship Analyzer for MongoDB Collections

Analyzes cross-collection relationships and referential integrity.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def analyze_foreign_keys(source_collection, target_collection, source_field: str, target_field: str) -> Dict[str, Any]:
    """
    Analyze foreign key relationship between two collections.

    Args:
        source_collection: Source collection with foreign key
        target_collection: Target collection
        source_field: Foreign key field in source
        target_field: Primary key field in target

    Returns:
        Dict with relationship analysis

    Example:
        >>> stats = analyze_foreign_keys(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid'
        ... )
        >>> print(f"Orphans: {stats['orphan_count']}")
    """
    logger.info(f"Analyzing foreign key: {source_collection.name}.{source_field} → {target_collection.name}.{target_field}")

    try:
        from yirifi_dq.core.validators.orphans import find_orphans

        # Find orphans
        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
        )

        total_source = source_collection.count_documents({})
        orphan_count = len(orphans)
        valid_count = total_source - orphan_count

        results = {
            "source_collection": source_collection.name,
            "target_collection": target_collection.name,
            "source_field": source_field,
            "target_field": target_field,
            "total_records": total_source,
            "valid_references": valid_count,
            "orphan_count": orphan_count,
            "integrity_percentage": round((valid_count / total_source * 100), 2) if total_source > 0 else 0,
        }

        logger.info(f"Foreign key analysis complete: {orphan_count} orphans out of {total_source} records")
        print("✓ Foreign key analysis:")
        print(f"  - Total records: {total_source}")
        print(f"  - Valid references: {valid_count}")
        print(f"  - Orphans: {orphan_count}")
        print(f"  - Integrity: {results['integrity_percentage']}%")

        return results

    except Exception as e:
        logger.error(f"Foreign key analysis failed: {e!s}", exc_info=True)
        print(f"❌ Foreign key analysis failed: {e!s}")
        raise


def analyze_collection_relationships(collections: List[tuple]) -> Dict[str, Any]:
    """
    Analyze relationships between multiple collections.

    Args:
        collections: List of tuples (source_coll, target_coll, source_field, target_field)

    Returns:
        Dict with relationship analysis

    Example:
        >>> relationships = [
        ...     (articles_collection, links_collection, 'articleYid', 'link_yid'),
        ...     (comments_collection, articles_collection, 'articleId', '_id')
        ... ]
        >>> stats = analyze_collection_relationships(relationships)
    """
    logger.info(f"Analyzing {len(collections)} collection relationships")

    try:
        results = []

        for source_coll, target_coll, source_field, target_field in collections:
            relationship_stats = analyze_foreign_keys(
                source_collection=source_coll,
                target_collection=target_coll,
                source_field=source_field,
                target_field=target_field,
            )
            results.append(relationship_stats)

        return {"total_relationships": len(collections), "relationships": results}

    except Exception as e:
        logger.error(f"Collection relationship analysis failed: {e!s}", exc_info=True)
        print(f"❌ Collection relationship analysis failed: {e!s}")
        raise


def detect_broken_relationships(source_collection, target_collection, source_field: str, target_field: str) -> List[Dict[str, Any]]:
    """
    Detect all broken relationships (orphans).

    Args:
        source_collection: Source collection
        target_collection: Target collection
        source_field: Foreign key field
        target_field: Primary key field

    Returns:
        List of orphaned documents

    Example:
        >>> broken = detect_broken_relationships(
        ...     source_collection=articles_collection,
        ...     target_collection=links_collection,
        ...     source_field='articleYid',
        ...     target_field='link_yid'
        ... )
        >>> print(f"Found {len(broken)} broken relationships")
    """
    logger.info("Detecting broken relationships")

    try:
        from yirifi_dq.core.validators.orphans import find_orphans

        orphans = find_orphans(
            source_collection=source_collection,
            target_collection=target_collection,
            source_field=source_field,
            target_field=target_field,
        )

        logger.info(f"Found {len(orphans)} broken relationships")
        return orphans

    except Exception as e:
        logger.error(f"Broken relationship detection failed: {e!s}", exc_info=True)
        print(f"❌ Broken relationship detection failed: {e!s}")
        raise


def generate_relationship_map(relationships: List[tuple], output_dir: Optional[Path] = None) -> str:
    """
    Generate relationship map report.

    Args:
        relationships: List of relationship tuples
        output_dir: Directory for report file

    Returns:
        str: Path to report file

    Example:
        >>> relationships = [
        ...     (articles_collection, links_collection, 'articleYid', 'link_yid')
        ... ]
        >>> report_file = generate_relationship_map(relationships)
    """
    logger.info("Generating relationship map")

    try:
        stats = analyze_collection_relationships(relationships)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {"timestamp": timestamp, "operation": "relationship_map", "statistics": stats}

        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        report_filename = f"relationship_map_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Relationship map generated: {report_file}")
        print(f"✓ Relationship map generated: {report_filename}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Relationship map generation failed: {e!s}", exc_info=True)
        print(f"❌ Relationship map generation failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Relationship Analyzer Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - analyze_foreign_keys() - Analyze single foreign key relationship")
    print("  - analyze_collection_relationships() - Analyze multiple relationships")
    print("  - detect_broken_relationships() - Find all orphans")
    print("  - generate_relationship_map() - Generate relationship report")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.analyzers import analyze_foreign_keys")
