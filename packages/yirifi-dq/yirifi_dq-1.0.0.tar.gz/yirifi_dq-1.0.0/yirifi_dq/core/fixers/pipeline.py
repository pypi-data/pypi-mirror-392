#!/usr/bin/env python3
"""
Pipeline State Reset Utilities

Reset pipeline processing states for documents stuck in Airflow DAG analysis.
Supports multiple input methods (CSV, manual, query) and cross-collection operations.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId

from yirifi_dq.core.backup import backup_documents


def load_ids_from_csv(csv_path: Union[str, Path], id_column: str = "link_yid") -> List[str]:
    """
    Load document IDs from CSV file.

    Args:
        csv_path: Path to CSV file
        id_column: Name of column containing IDs (default: 'link_yid')

    Returns:
        List of document IDs

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If ID column not found or no IDs loaded
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    ids = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if id_column not in reader.fieldnames:
            raise ValueError(f"Column '{id_column}' not found in CSV. Available columns: {', '.join(reader.fieldnames)}")

        for row in reader:
            id_value = row[id_column].strip()
            if id_value:
                ids.append(id_value)

    if not ids:
        raise ValueError(f"No IDs found in CSV file: {csv_path}")

    print(f"✓ Loaded {len(ids)} IDs from CSV: {csv_path}")
    return ids


def parse_manual_ids(ids_input: str) -> List[str]:
    """
    Parse manually entered IDs from comma or newline separated string.

    Args:
        ids_input: Comma or newline separated IDs

    Returns:
        List of document IDs

    Raises:
        ValueError: If no valid IDs found
    """
    # Split by comma or newline
    ids = []
    for line in ids_input.split("\n"):
        for part in line.split(","):
            id_value = part.strip()
            if id_value:
                ids.append(id_value)

    if not ids:
        raise ValueError("No valid IDs found in manual input")

    print(f"✓ Parsed {len(ids)} IDs from manual input")
    return ids


def find_documents_by_query(collection, query_filter: Dict[str, Any], limit: Optional[int] = None, id_field: str = "_id") -> List[Any]:
    """
    Find documents using MongoDB query and extract their IDs.

    Args:
        collection: MongoDB collection
        query_filter: MongoDB query filter
        limit: Optional limit on number of documents
        id_field: Field to extract as ID (default: '_id')

    Returns:
        List of document IDs

    Raises:
        ValueError: If no documents found matching query
    """
    cursor = collection.find(query_filter)

    if limit:
        cursor = cursor.limit(limit)

    ids = [doc[id_field] for doc in cursor]

    if not ids:
        raise ValueError(f"No documents found matching query: {query_filter}")

    print(f"✓ Found {len(ids)} documents matching query")
    return ids


def convert_to_object_ids(ids: List[str], id_field: str) -> List[Union[str, ObjectId]]:
    """
    Convert string IDs to appropriate type for querying.

    If id_field is '_id', convert to ObjectId.
    Otherwise, keep as string.

    Args:
        ids: List of string IDs
        id_field: Field name being used for matching

    Returns:
        List of IDs in appropriate format
    """
    if id_field == "_id":
        # Convert to ObjectId for _id queries
        converted = []
        for id_str in ids:
            try:
                converted.append(ObjectId(id_str))
            except Exception as e:
                print(f"Warning: Failed to convert '{id_str}' to ObjectId: {e}")
        return converted
    else:
        # Keep as strings for other fields
        return ids


def reset_pipeline_fields(
    collection,
    operation_config: Dict[str, Any],
    input_method: str,
    input_data: Dict[str, Any],
    env: str = "DEV",
    test_mode: bool = True,
    auto_backup: bool = True,
) -> Dict[str, Any]:
    """
    Reset pipeline fields for documents based on operation config.

    Args:
        collection: MongoDB collection to update
        operation_config: Operation YAML config (field_updates, etc.)
        input_method: 'csv', 'manual', or 'query'
        input_data: Dictionary containing input parameters:
            - For 'csv': {'csv_path': '...', 'id_column': '...'}
            - For 'manual': {'ids': [...]}
            - For 'query': {'query_filter': {...}}
        env: Environment (PRD/DEV/UAT)
        test_mode: If True, dry run without actual updates
        auto_backup: If True, create backup before updates

    Returns:
        Result dictionary with statistics:
        {
            'success': bool,
            'matched_count': int,
            'updated_count': int,
            'backup_file': str or None,
            'test_mode': bool,
            'field_updates': dict,
            'error': str or None
        }

    Raises:
        ValueError: If invalid input_method or missing required data
    """
    result = {
        "success": False,
        "matched_count": 0,
        "updated_count": 0,
        "backup_file": None,
        "test_mode": test_mode,
        "field_updates": operation_config.get("field_updates", {}),
        "error": None,
    }

    try:
        # Step 1: Load document IDs based on input method
        id_field = operation_config.get("id_field", "link_yid")
        ids = []

        if input_method == "csv":
            csv_path = input_data.get("csv_path")
            id_column = input_data.get("id_column", id_field)
            if not csv_path:
                raise ValueError("csv_path required for CSV input method")
            ids = load_ids_from_csv(csv_path, id_column=id_column)

        elif input_method == "manual":
            ids_list = input_data.get("ids")
            if not ids_list:
                raise ValueError("ids list required for manual input method")
            ids = parse_manual_ids(ids_list) if isinstance(ids_list, str) else ids_list

        elif input_method == "query":
            query_filter = input_data.get("query_filter")
            limit = input_data.get("limit")
            if not query_filter:
                raise ValueError("query_filter required for query input method")
            ids = find_documents_by_query(collection, query_filter, limit, id_field)

        else:
            raise ValueError(f"Invalid input_method: {input_method}")

        if not ids:
            raise ValueError("No IDs loaded from input")

        print("\n📊 Pipeline Reset Summary:")
        print(f"   Environment: {env}")
        print(f"   Input Method: {input_method}")
        print(f"   Documents to Update: {len(ids)}")
        print(f"   Test Mode: {test_mode}")
        print(f"   Field Updates: {json.dumps(result['field_updates'], indent=2)}")

        # Convert IDs to appropriate type
        converted_ids = convert_to_object_ids(ids, id_field)

        # Build query filter
        query = {id_field: {"$in": converted_ids}}

        # Step 2: Create backup if auto_backup=True
        if auto_backup and not test_mode:
            print("\n💾 Creating backup...")
            backup_file = backup_documents(
                collection=collection,
                filter_query=query,
                operation_name="pipeline_reset",
                test_mode=False,
            )
            result["backup_file"] = backup_file
            print(f"   ✓ Backup created: {backup_file}")

        # Step 3: Apply field updates
        if test_mode:
            print("\n🧪 TEST MODE - Preview only (no actual updates)")
            # Count how many documents would be affected
            matched_count = collection.count_documents(query)
            result["matched_count"] = matched_count
            result["updated_count"] = 0  # No updates in test mode
            print(f"   Would update {matched_count} documents")

            # Show sample documents that would be updated
            sample_docs = list(collection.find(query).limit(3))
            if sample_docs:
                print("\n   Sample documents that would be updated:")
                for i, doc in enumerate(sample_docs, 1):
                    print(f"   {i}. {id_field}: {doc.get(id_field)}")
                    # Show current values of fields to be updated
                    for field_path in result["field_updates"]:
                        current_val = _get_nested_field(doc, field_path)
                        print(f"      {field_path}: {current_val} → {result['field_updates'][field_path]}")

        else:
            print("\n✏️  Applying field updates...")
            # Build $set update document
            update_doc = {"$set": result["field_updates"]}

            # Execute update
            update_result = collection.update_many(query, update_doc)

            result["matched_count"] = update_result.matched_count
            result["updated_count"] = update_result.modified_count

            print(f"   ✓ Matched: {result['matched_count']} documents")
            print(f"   ✓ Updated: {result['updated_count']} documents")

        # Step 4: Verify updates (if not test mode)
        if not test_mode and result["updated_count"] > 0:
            print("\n✅ Verifying updates...")
            verification_passed = _verify_field_updates(collection, query, result["field_updates"])
            if verification_passed:
                print("   ✓ Verification passed")
            else:
                print("   ⚠️  Verification failed - some fields may not have been updated correctly")
                result["error"] = "Verification failed"

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        print(f"\n❌ Error: {e}")

    return result


def reset_cross_collection_pipeline(
    source_collection,
    target_collection,
    source_query: Dict[str, Any],
    match_field: str,
    target_field: str,
    field_updates: Dict[str, Any],
    env: str = "DEV",
    test_mode: bool = True,
    auto_backup: bool = True,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Reset pipeline fields across two collections.

    Used for operations like redownload_va_no where we query one collection
    (articledocuments_oreg) and update another (links).

    Args:
        source_collection: MongoDB collection to query (e.g., articledocuments_oreg)
        target_collection: MongoDB collection to update (e.g., links)
        source_query: Query to find documents in source collection
        match_field: Field in source collection to extract values from (e.g., articleYid)
        target_field: Field in target collection to match against (e.g., link_yid)
        field_updates: Dictionary of field updates to apply
        env: Environment (PRD/DEV/UAT)
        test_mode: If True, dry run without actual updates
        auto_backup: If True, create backup before updates
        limit: Optional limit on number of documents to process

    Returns:
        Result dictionary with statistics
    """
    result = {
        "success": False,
        "source_matched": 0,
        "target_matched": 0,
        "updated_count": 0,
        "backup_file": None,
        "test_mode": test_mode,
        "error": None,
    }

    try:
        print("\n📊 Cross-Collection Pipeline Reset:")
        print(f"   Source Collection: {source_collection.name}")
        print(f"   Target Collection: {target_collection.name}")
        print(f"   Source Query: {source_query}")
        print(f"   Match Field: {match_field} → {target_field}")
        print(f"   Environment: {env}")
        print(f"   Test Mode: {test_mode}")

        # Step 1: Query source collection
        print("\n🔍 Finding documents in source collection...")
        cursor = source_collection.find(source_query, {match_field: 1})

        if limit:
            cursor = cursor.limit(limit)

        match_values = [doc[match_field] for doc in cursor if match_field in doc]

        if not match_values:
            raise ValueError(f"No documents found in source collection with query: {source_query}")

        result["source_matched"] = len(match_values)
        print(f"   ✓ Found {len(match_values)} documents in source collection")

        # Step 2: Use values to create operation config for target collection
        operation_config = {"field_updates": field_updates, "id_field": target_field}

        input_data = {"ids": match_values}

        # Step 3: Call standard reset function on target collection
        target_result = reset_pipeline_fields(
            collection=target_collection,
            operation_config=operation_config,
            input_method="manual",
            input_data=input_data,
            env=env,
            test_mode=test_mode,
            auto_backup=auto_backup,
        )

        # Merge results
        result["target_matched"] = target_result["matched_count"]
        result["updated_count"] = target_result["updated_count"]
        result["backup_file"] = target_result["backup_file"]
        result["success"] = target_result["success"]
        result["error"] = target_result.get("error")

        print("\n✅ Cross-collection reset completed:")
        print(f"   Source documents: {result['source_matched']}")
        print(f"   Target matched: {result['target_matched']}")
        print(f"   Updated: {result['updated_count']}")

    except Exception as e:
        result["error"] = str(e)
        print(f"\n❌ Error: {e}")

    return result


def _get_nested_field(doc: Dict[str, Any], field_path: str) -> Any:
    """
    Get nested field value from document using dot notation.

    Args:
        doc: Document dictionary
        field_path: Field path (e.g., 'download_analysis.website-scraping.retry_count')

    Returns:
        Field value or None if not found
    """
    parts = field_path.split(".")
    value = doc

    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None

    return value


def _verify_field_updates(collection, query: Dict[str, Any], field_updates: Dict[str, Any], sample_size: int = 10) -> bool:
    """
    Verify that field updates were applied correctly.

    Args:
        collection: MongoDB collection
        query: Query used to select documents
        field_updates: Dictionary of field updates that were applied
        sample_size: Number of documents to check

    Returns:
        True if verification passed, False otherwise
    """
    sample_docs = list(collection.find(query).limit(sample_size))

    if not sample_docs:
        print("   ⚠️  No documents found for verification")
        return False

    all_correct = True

    for doc in sample_docs:
        for field_path, expected_value in field_updates.items():
            actual_value = _get_nested_field(doc, field_path)
            if actual_value != expected_value:
                print(f"   ⚠️  Mismatch: {field_path} = {actual_value}, expected {expected_value}")
                all_correct = False

    return all_correct
