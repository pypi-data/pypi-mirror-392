#!/usr/bin/env python3
"""
Statistics Generator for MongoDB Collections

Generates collection and database-level statistics.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def generate_collection_stats(collection, sample_size: int = 1000) -> Dict[str, Any]:
    """
    Generate comprehensive collection statistics.

    Args:
        collection: MongoDB collection
        sample_size: Number of documents to sample for analysis

    Returns:
        Dict with collection statistics

    Example:
        >>> stats = generate_collection_stats(collection)
        >>> print(f"Total documents: {stats['total_documents']}")
        >>> print(f"Average document size: {stats['avg_document_size']} bytes")
    """
    logger.info(f"Generating statistics for collection: {collection.name}")

    try:
        # Get basic counts
        total_documents = collection.count_documents({})

        # Sample documents for analysis
        sample_docs = list(collection.find().limit(sample_size))

        # Calculate average document size
        if sample_docs:
            import bson

            total_size = sum(len(bson.BSON.encode(doc)) for doc in sample_docs)
            avg_size = total_size / len(sample_docs)
        else:
            avg_size = 0

        # Get field names from sample
        all_fields = set()
        for doc in sample_docs:
            all_fields.update(doc.keys())

        stats = {
            "collection": collection.name,
            "database": collection.database.name,
            "total_documents": total_documents,
            "sample_size": len(sample_docs),
            "avg_document_size": round(avg_size, 2),
            "total_fields": len(all_fields),
            "fields": list(all_fields),
        }

        logger.info(f"Collection stats generated: {total_documents} documents, {len(all_fields)} fields")
        print("✓ Collection statistics:")
        print(f"  - Collection: {collection.name}")
        print(f"  - Total documents: {total_documents:,}")
        print(f"  - Avg document size: {stats['avg_document_size']:.2f} bytes")
        print(f"  - Total fields: {len(all_fields)}")

        return stats

    except Exception as e:
        logger.error(f"Collection stats generation failed: {e!s}", exc_info=True)
        print(f"❌ Collection stats generation failed: {e!s}")
        raise


def generate_database_stats(database, include_collections: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate database-level statistics.

    Args:
        database: MongoDB database
        include_collections: Optional list of collections to include

    Returns:
        Dict with database statistics

    Example:
        >>> stats = generate_database_stats(db)
        >>> print(f"Total collections: {stats['total_collections']}")
    """
    logger.info(f"Generating statistics for database: {database.name}")

    try:
        collection_names = database.list_collection_names()

        if include_collections:
            collection_names = [name for name in collection_names if name in include_collections]

        collection_stats = []
        total_docs = 0

        for coll_name in collection_names:
            coll = database[coll_name]
            doc_count = coll.count_documents({})
            total_docs += doc_count

            collection_stats.append({"name": coll_name, "document_count": doc_count})

        stats = {
            "database": database.name,
            "total_collections": len(collection_names),
            "total_documents": total_docs,
            "collections": collection_stats,
        }

        logger.info(f"Database stats generated: {len(collection_names)} collections, {total_docs} total documents")
        print("✓ Database statistics:")
        print(f"  - Database: {database.name}")
        print(f"  - Total collections: {len(collection_names)}")
        print(f"  - Total documents: {total_docs:,}")

        return stats

    except Exception as e:
        logger.error(f"Database stats generation failed: {e!s}", exc_info=True)
        print(f"❌ Database stats generation failed: {e!s}")
        raise


def compare_collections(collection1, collection2) -> Dict[str, Any]:
    """
    Compare two collections.

    Args:
        collection1: First collection
        collection2: Second collection

    Returns:
        Dict with comparison results

    Example:
        >>> comparison = compare_collections(links_coll, links_backup_coll)
        >>> print(f"Document count difference: {comparison['count_difference']}")
    """
    logger.info(f"Comparing collections: {collection1.name} vs {collection2.name}")

    try:
        count1 = collection1.count_documents({})
        count2 = collection2.count_documents({})

        comparison = {
            "collection1": {"name": collection1.name, "count": count1},
            "collection2": {"name": collection2.name, "count": count2},
            "count_difference": count1 - count2,
            "count_ratio": round(count1 / count2, 2) if count2 > 0 else 0,
        }

        logger.info(f"Comparison complete: {count1} vs {count2} documents")
        print("✓ Collection comparison:")
        print(f"  - {collection1.name}: {count1:,} documents")
        print(f"  - {collection2.name}: {count2:,} documents")
        print(f"  - Difference: {comparison['count_difference']:,}")

        return comparison

    except Exception as e:
        logger.error(f"Collection comparison failed: {e!s}", exc_info=True)
        print(f"❌ Collection comparison failed: {e!s}")
        raise


def track_operation_metrics(
    operation_name: str,
    start_time: float,
    end_time: float,
    records_processed: int,
    output_dir: Optional[Path] = None,
) -> str:
    """
    Track and save operation performance metrics.

    Args:
        operation_name: Name of operation
        start_time: Start timestamp
        end_time: End timestamp
        records_processed: Number of records processed
        output_dir: Directory for metrics file

    Returns:
        str: Path to metrics file

    Example:
        >>> import time
        >>> start = time.time()
        >>> # ... perform operation ...
        >>> end = time.time()
        >>> metrics_file = track_operation_metrics(
        ...     operation_name="duplicate_cleanup",
        ...     start_time=start,
        ...     end_time=end,
        ...     records_processed=1000
        ... )
    """
    logger.info(f"Tracking metrics for operation: {operation_name}")

    try:
        from yirifi_dq.reporting import format_duration

        duration = end_time - start_time
        records_per_second = records_processed / duration if duration > 0 else 0

        metrics = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "operation_name": operation_name,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "duration_seconds": round(duration, 2),
            "duration_formatted": format_duration(duration),
            "records_processed": records_processed,
            "records_per_second": round(records_per_second, 2),
        }

        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        metrics_filename = f"metrics_{operation_name}_{metrics['timestamp']}.json"
        metrics_file = output_dir / metrics_filename

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2, default=str)

        logger.info(f"Operation metrics saved: {metrics_file}")
        print(f"✓ Operation metrics saved: {metrics_filename}")
        print(f"  - Duration: {metrics['duration_formatted']}")
        print(f"  - Records processed: {records_processed:,}")
        print(f"  - Processing rate: {records_per_second:.2f} records/sec")

        return str(metrics_file)

    except Exception as e:
        logger.error(f"Metrics tracking failed: {e!s}", exc_info=True)
        print(f"❌ Metrics tracking failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Statistics Generator Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - generate_collection_stats() - Collection-level statistics")
    print("  - generate_database_stats() - Database-level statistics")
    print("  - compare_collections() - Compare two collections")
    print("  - track_operation_metrics() - Track operation performance")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.analyzers import generate_collection_stats")
