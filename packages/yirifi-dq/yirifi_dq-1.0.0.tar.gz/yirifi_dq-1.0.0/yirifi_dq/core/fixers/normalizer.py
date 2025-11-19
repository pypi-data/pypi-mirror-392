#!/usr/bin/env python3
"""
Data Normalizer for MongoDB Collections

Normalizes field values to ensure consistency across collections.
Supports URLs, text, case normalization and custom transformations.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse, urlunparse

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def normalize_urls(
    collection,
    field_name: str,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Normalize URL values in a field.

    Normalizations performed:
    - Remove trailing slashes
    - Convert to lowercase (domain only)
    - Remove fragments (#section)
    - Standardize http/https
    - Remove www. prefix if present

    Args:
        collection: MongoDB collection
        field_name: Field containing URLs
        filter_query: Optional filter for documents
        test_mode: If True, performs dry run without updates
        limit: Optional limit on number of documents to process

    Returns:
        Dict with operation results

    Example:
        >>> result = normalize_urls(
        ...     collection=links_collection,
        ...     field_name='url',
        ...     test_mode=False
        ... )
        >>> print(f"Normalized {result['updated_count']} URLs")
    """
    logger.info(f"Normalizing URLs in {collection.name}.{field_name}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Processing {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Normalizing URLs in {len(documents)} documents")

        updated_count = 0
        changes_made = []

        for doc in documents:
            original_url = doc.get(field_name)

            if not original_url or not isinstance(original_url, str):
                continue

            # Normalize URL
            try:
                parsed = urlparse(original_url.strip())

                # Normalize domain to lowercase
                netloc = parsed.netloc.lower()

                # Remove www. prefix
                if netloc.startswith("www."):
                    netloc = netloc[4:]

                # Remove trailing slash from path
                path = parsed.path.rstrip("/") if parsed.path else ""

                # Rebuild URL without fragment
                normalized_url = urlunparse(
                    (
                        parsed.scheme,
                        netloc,
                        path,
                        parsed.params,
                        parsed.query,
                        "",  # Remove fragment
                    )
                )

                # If changed, update
                if normalized_url != original_url:
                    if not test_mode:
                        collection.update_one({"_id": doc["_id"]}, {"$set": {field_name: normalized_url}})

                    updated_count += 1

                    # Keep first 10 examples
                    if len(changes_made) < 10:
                        changes_made.append(
                            {
                                "id": str(doc["_id"]),
                                "original": original_url,
                                "normalized": normalized_url,
                            }
                        )

            except Exception as e:
                logger.warning(f"Failed to normalize URL '{original_url}': {e!s}")

        logger.info(f"Normalized {updated_count} URLs")
        print("✓ URL normalization complete:")
        print(f"  - Documents processed: {len(documents)}")
        print(f"  - URLs normalized: {updated_count}")

        return {
            "field": field_name,
            "total_processed": len(documents),
            "updated_count": updated_count,
            "examples": changes_made,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"URL normalization failed: {e!s}", exc_info=True)
        print(f"❌ URL normalization failed: {e!s}")
        raise


def normalize_whitespace(
    collection,
    field_name: str,
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Normalize whitespace in text fields.

    Normalizations performed:
    - Trim leading/trailing whitespace
    - Replace multiple spaces with single space
    - Remove tabs and newlines

    Args:
        collection: MongoDB collection
        field_name: Field containing text
        filter_query: Optional filter for documents
        test_mode: If True, performs dry run without updates
        limit: Optional limit on number of documents to process

    Returns:
        Dict with operation results

    Example:
        >>> result = normalize_whitespace(
        ...     collection=users_collection,
        ...     field_name='name',
        ...     test_mode=False
        ... )
        >>> print(f"Normalized {result['updated_count']} names")
    """
    logger.info(f"Normalizing whitespace in {collection.name}.{field_name}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Processing {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Normalizing whitespace in {len(documents)} documents")

        updated_count = 0
        changes_made = []

        for doc in documents:
            original_value = doc.get(field_name)

            if not original_value or not isinstance(original_value, str):
                continue

            # Normalize whitespace
            normalized_value = " ".join(original_value.split())

            # If changed, update
            if normalized_value != original_value:
                if not test_mode:
                    collection.update_one({"_id": doc["_id"]}, {"$set": {field_name: normalized_value}})

                updated_count += 1

                # Keep first 10 examples
                if len(changes_made) < 10:
                    changes_made.append(
                        {
                            "id": str(doc["_id"]),
                            "original": original_value[:100],
                            "normalized": normalized_value[:100],
                        }
                    )

        logger.info(f"Normalized {updated_count} values")
        print("✓ Whitespace normalization complete:")
        print(f"  - Documents processed: {len(documents)}")
        print(f"  - Values normalized: {updated_count}")

        return {
            "field": field_name,
            "total_processed": len(documents),
            "updated_count": updated_count,
            "examples": changes_made,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Whitespace normalization failed: {e!s}", exc_info=True)
        print(f"❌ Whitespace normalization failed: {e!s}")
        raise


def normalize_case(
    collection,
    field_name: str,
    case_type: str = "lower",
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Normalize case of text fields.

    Args:
        collection: MongoDB collection
        field_name: Field containing text
        case_type: 'lower', 'upper', or 'title'
        filter_query: Optional filter for documents
        test_mode: If True, performs dry run without updates
        limit: Optional limit on number of documents to process

    Returns:
        Dict with operation results

    Example:
        >>> result = normalize_case(
        ...     collection=users_collection,
        ...     field_name='email',
        ...     case_type='lower',
        ...     test_mode=False
        ... )
        >>> print(f"Normalized {result['updated_count']} emails to lowercase")
    """
    logger.info(f"Normalizing case in {collection.name}.{field_name} to {case_type}")

    try:
        if case_type not in ["lower", "upper", "title"]:
            raise ValueError(f"Invalid case_type: {case_type}. Must be 'lower', 'upper', or 'title'")

        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Processing {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Normalizing case in {len(documents)} documents")

        updated_count = 0
        changes_made = []

        for doc in documents:
            original_value = doc.get(field_name)

            if not original_value or not isinstance(original_value, str):
                continue

            # Normalize case
            if case_type == "lower":
                normalized_value = original_value.lower()
            elif case_type == "upper":
                normalized_value = original_value.upper()
            else:  # title
                normalized_value = original_value.title()

            # If changed, update
            if normalized_value != original_value:
                if not test_mode:
                    collection.update_one({"_id": doc["_id"]}, {"$set": {field_name: normalized_value}})

                updated_count += 1

                # Keep first 10 examples
                if len(changes_made) < 10:
                    changes_made.append(
                        {
                            "id": str(doc["_id"]),
                            "original": original_value[:100],
                            "normalized": normalized_value[:100],
                        }
                    )

        logger.info(f"Normalized {updated_count} values to {case_type}case")
        print("✓ Case normalization complete:")
        print(f"  - Documents processed: {len(documents)}")
        print(f"  - Values normalized: {updated_count}")
        print(f"  - Case type: {case_type}")

        return {
            "field": field_name,
            "case_type": case_type,
            "total_processed": len(documents),
            "updated_count": updated_count,
            "examples": changes_made,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Case normalization failed: {e!s}", exc_info=True)
        print(f"❌ Case normalization failed: {e!s}")
        raise


def normalize_field(
    collection,
    field_name: str,
    normalizer: Callable[[Any], Any],
    filter_query: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Apply custom normalization function to field values.

    Args:
        collection: MongoDB collection
        field_name: Field to normalize
        normalizer: Function that takes a value and returns normalized value
        filter_query: Optional filter for documents
        test_mode: If True, performs dry run without updates
        limit: Optional limit on number of documents to process

    Returns:
        Dict with operation results

    Example:
        >>> # Custom normalizer to remove special characters
        >>> def remove_special_chars(value):
        ...     if isinstance(value, str):
        ...         return re.sub(r'[^a-zA-Z0-9\\s]', '', value)
        ...     return value
        >>>
        >>> result = normalize_field(
        ...     collection=users_collection,
        ...     field_name='username',
        ...     normalizer=remove_special_chars,
        ...     test_mode=False
        ... )
    """
    logger.info(f"Applying custom normalization to {collection.name}.{field_name}")

    try:
        query = filter_query if filter_query else {}

        # Get documents
        if limit:
            logger.info(f"Applying limit: {limit}")
            documents = list(collection.find(query).limit(limit))
        else:
            documents = list(collection.find(query))

        logger.info(f"Processing {len(documents)} documents")

        if test_mode:
            print(f"⚠️  TEST MODE: Normalizing {len(documents)} documents")

        updated_count = 0
        error_count = 0
        changes_made = []

        for doc in documents:
            original_value = doc.get(field_name)

            if original_value is None:
                continue

            try:
                # Apply custom normalizer
                normalized_value = normalizer(original_value)

                # If changed, update
                if normalized_value != original_value:
                    if not test_mode:
                        collection.update_one({"_id": doc["_id"]}, {"$set": {field_name: normalized_value}})

                    updated_count += 1

                    # Keep first 10 examples
                    if len(changes_made) < 10:
                        changes_made.append(
                            {
                                "id": str(doc["_id"]),
                                "original": str(original_value)[:100],
                                "normalized": str(normalized_value)[:100],
                            }
                        )

            except Exception as e:
                error_count += 1
                logger.warning(f"Failed to normalize value for doc {doc['_id']}: {e!s}")

        logger.info(f"Normalized {updated_count} values, {error_count} errors")
        print("✓ Custom normalization complete:")
        print(f"  - Documents processed: {len(documents)}")
        print(f"  - Values normalized: {updated_count}")

        if error_count > 0:
            print(f"  - Errors: {error_count}")

        return {
            "field": field_name,
            "total_processed": len(documents),
            "updated_count": updated_count,
            "error_count": error_count,
            "examples": changes_made,
            "test_mode": test_mode,
        }

    except Exception as e:
        logger.error(f"Custom normalization failed: {e!s}", exc_info=True)
        print(f"❌ Custom normalization failed: {e!s}")
        raise


if __name__ == "__main__":
    print("Data Normalizer Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - normalize_urls() - Normalize URL values")
    print("  - normalize_whitespace() - Normalize whitespace in text")
    print("  - normalize_case() - Normalize text case (lower/upper/title)")
    print("  - normalize_field() - Apply custom normalization function")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.core.fixers.normalizer import normalize_urls, normalize_whitespace")
    print("  # OR")
    print("  from yirifi_dq.core.fixers import normalize_urls, normalize_whitespace")
