#!/usr/bin/env python3
"""
Field Analyzer for MongoDB Collections

Analyzes field value distributions, patterns, and quality metrics.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def analyze_field_distribution(collection, field_name: str, top_n: int = 20, filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze value distribution for a field.

    Args:
        collection: MongoDB collection
        field_name: Field to analyze
        top_n: Number of top values to return
        filter_query: Optional filter for documents

    Returns:
        Dict with distribution analysis

    Example:
        >>> stats = analyze_field_distribution(collection, 'status', top_n=10)
        >>> print(f"Top value: {stats['top_values'][0]['value']} ({stats['top_values'][0]['count']} occurrences)")
    """
    logger.info(f"Analyzing field distribution: {collection.name}.{field_name}")

    try:
        query = filter_query if filter_query else {}
        documents = list(collection.find(query))

        values = [doc.get(field_name) for doc in documents]
        value_counts = Counter(values)

        total_docs = len(documents)
        unique_values = len(value_counts)
        null_count = value_counts.get(None, 0)

        top_values = [
            {
                "value": str(value)[:100] if value is not None else "NULL",
                "count": count,
                "percentage": round((count / total_docs * 100), 2),
            }
            for value, count in value_counts.most_common(top_n)
        ]

        results = {
            "field": field_name,
            "total_documents": total_docs,
            "unique_values": unique_values,
            "null_count": null_count,
            "top_values": top_values,
        }

        logger.info(f"Field analysis complete: {unique_values} unique values in {total_docs} documents")
        print("✓ Field distribution analysis:")
        print(f"  - Field: {field_name}")
        print(f"  - Total documents: {total_docs}")
        print(f"  - Unique values: {unique_values}")
        print(f"  - Null/Missing: {null_count}")

        return results

    except Exception as e:
        logger.error(f"Field distribution analysis failed: {e!s}", exc_info=True)
        print(f"❌ Field distribution analysis failed: {e!s}")
        raise


def analyze_field_nulls(collection, fields: List[str], filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze null/missing values across multiple fields.

    Args:
        collection: MongoDB collection
        fields: List of fields to analyze
        filter_query: Optional filter for documents

    Returns:
        Dict with null analysis

    Example:
        >>> stats = analyze_field_nulls(collection, ['email', 'phone', 'address'])
        >>> for field, info in stats['by_field'].items():
        ...     print(f"{field}: {info['null_count']} nulls ({info['null_percentage']}%)")
    """
    logger.info(f"Analyzing null values for fields: {', '.join(fields)}")

    try:
        query = filter_query if filter_query else {}
        documents = list(collection.find(query))
        total_docs = len(documents)

        null_stats = {}
        for field in fields:
            null_count = sum(1 for doc in documents if doc.get(field) is None or doc.get(field) == "")
            null_stats[field] = {
                "null_count": null_count,
                "non_null_count": total_docs - null_count,
                "null_percentage": round((null_count / total_docs * 100), 2) if total_docs > 0 else 0,
            }

        results = {"total_documents": total_docs, "fields_analyzed": fields, "by_field": null_stats}

        logger.info(f"Null analysis complete for {len(fields)} fields")
        print("✓ Null value analysis:")
        print(f"  - Total documents: {total_docs}")
        print(f"  - Fields analyzed: {len(fields)}")

        return results

    except Exception as e:
        logger.error(f"Null analysis failed: {e!s}", exc_info=True)
        print(f"❌ Null analysis failed: {e!s}")
        raise


def analyze_field_types(collection, field_name: str, filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze data type distribution for a field.

    Args:
        collection: MongoDB collection
        field_name: Field to analyze
        filter_query: Optional filter for documents

    Returns:
        Dict with type distribution

    Example:
        >>> stats = analyze_field_types(collection, 'age')
        >>> print(f"Type distribution: {stats['type_distribution']}")
    """
    logger.info(f"Analyzing field types: {collection.name}.{field_name}")

    try:
        query = filter_query if filter_query else {}
        documents = list(collection.find(query))

        type_counts = Counter()
        for doc in documents:
            value = doc.get(field_name)
            type_counts[type(value).__name__] += 1

        total_docs = len(documents)

        type_distribution = [{"type": type_name, "count": count, "percentage": round((count / total_docs * 100), 2)} for type_name, count in type_counts.most_common()]

        results = {
            "field": field_name,
            "total_documents": total_docs,
            "type_distribution": type_distribution,
        }

        logger.info(f"Type analysis complete: {len(type_counts)} different types found")
        print("✓ Field type analysis:")
        print(f"  - Field: {field_name}")
        print(f"  - Different types: {len(type_counts)}")

        return results

    except Exception as e:
        logger.error(f"Type analysis failed: {e!s}", exc_info=True)
        print(f"❌ Type analysis failed: {e!s}")
        raise


def generate_field_report(collection, field_name: str, output_dir: Optional[Path] = None) -> str:
    """
    Generate comprehensive field analysis report.

    Args:
        collection: MongoDB collection
        field_name: Field to analyze
        output_dir: Directory for report file

    Returns:
        str: Path to report file

    Example:
        >>> report_file = generate_field_report(collection, 'status')
        >>> print(f"Report saved: {report_file}")
    """
    logger.info(f"Generating field report: {collection.name}.{field_name}")

    try:
        # Run all analyses
        distribution = analyze_field_distribution(collection, field_name)
        types = analyze_field_types(collection, field_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "collection": collection.name,
            "database": collection.database.name,
            "field": field_name,
            "distribution": distribution,
            "types": types,
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"field_analysis_{field_name}_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Field report generated: {report_file}")
        print(f"✓ Field report generated: {report_filename}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Field report generation failed: {e!s}", exc_info=True)
        print(f"❌ Field report generation failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Field Analyzer Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - analyze_field_distribution() - Analyze value distribution")
    print("  - analyze_field_nulls() - Analyze null/missing values")
    print("  - analyze_field_types() - Analyze data type distribution")
    print("  - generate_field_report() - Generate comprehensive report")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.analyzers import analyze_field_distribution")
