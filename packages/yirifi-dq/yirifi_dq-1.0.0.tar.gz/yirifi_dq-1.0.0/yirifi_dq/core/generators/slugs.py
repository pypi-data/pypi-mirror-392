"""
AI-Enhanced Slug Generator

Generates and manages URL-friendly slugs using OpenAI gpt-5-nano.

Features:
- Automatic slug generation for missing/empty slugs
- Duplicate slug detection and regeneration
- AI-powered collision handling
- Dynamic field selection (excludes metadata)
- Test mode support
- Automatic backup before changes

Usage:
    from yirifi_dq.core.generators import SlugGenerator

    generator = SlugGenerator(env='DEV')
    results = generator.fix_missing_slugs(
        database='regdb',
        collection='organizations',
        test_mode=True,
        limit=10
    )
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar, Dict, List, Optional, Set

import yaml
from openai import OpenAI
from pymongo.collection import Collection

from yirifi_dq.core.backup import backup_documents
from yirifi_dq.core.mongodb import get_client, get_collection, get_database


class SlugGenerator:
    """
    AI-enhanced slug generator using OpenAI gpt-5-nano.

    Handles slug generation, duplicate detection, and collision resolution.
    """

    # Fields to exclude from slug generation context
    METADATA_FIELDS: ClassVar[set] = {
        "_id",
        "id",
        "created",
        "createdAt",
        "updated",
        "updatedAt",
        "created_at",
        "updated_at",
        "modified",
        "modifiedAt",
        "__v",
        "version",
        "slug",  # Don't include existing slug in generation
    }

    def __init__(self, env: str = "DEV", config_path: Optional[str] = None):
        """
        Initialize slug generator.

        Args:
            env: Environment to connect to (PRD/DEV/UAT)
            config_path: Optional path to YAML config file (defaults to yirifi_dq/config/slug_fields.yaml)
        """
        self.env = env
        self.client = get_client(env=env)

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in environment variables")

        self.openai_client = OpenAI(
            api_key=api_key,
            timeout=900.0,  # 15 minutes for flex processing
        )

        # Load field configuration from YAML
        self.field_config = self._load_field_config(config_path)

        # Load AI optimization settings
        if self.field_config and "ai_settings" in self.field_config:
            self.ai_settings = self.field_config["ai_settings"]
        else:
            # Default settings (backward compatible)
            self.ai_settings = {
                "send_existing_slugs_on_retry": True,
                "max_similar_slugs": 10,
                "max_field_value_length": 500,
            }

        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "slugs_generated": 0,
            "duplicates_fixed": 0,
            "collisions_resolved": 0,
            "api_calls": 0,
            "errors": 0,
            "rate_limit_errors": 0,
        }

        # Thread-safety infrastructure
        self.slug_lock = Lock()  # Protects existing_slugs set
        self.stats_lock = Lock()  # Protects stats dictionary
        self.rate_limiter_enabled = False  # Adaptive rate limiting
        self.rate_limit_lock = Lock()  # Protects rate limiter state

    def _load_field_config(self, config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load field configuration from YAML file.

        Args:
            config_path: Path to YAML config file (optional)

        Returns:
            Parsed YAML config dict, or None if file not found/invalid (fallback to hardcoded)
        """
        # Default config path
        config_path = Path(__file__).parent.parent / "config" / "slug_fields.yaml" if config_path is None else Path(config_path)

        try:
            if not config_path.exists():
                print(f"⚠️  YAML config not found: {config_path}")
                print("⚠️  Falling back to hardcoded METADATA_FIELDS")
                return None

            with open(config_path) as f:
                config = yaml.safe_load(f)

            print(f"✓ Loaded field configuration from: {config_path}")
            return config

        except yaml.YAMLError as e:
            print(f"⚠️  Error parsing YAML config: {e}")
            print("⚠️  Falling back to hardcoded METADATA_FIELDS")
            return None

        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            print("⚠️  Falling back to hardcoded METADATA_FIELDS")
            return None

    def _filter_metadata_fields(self, record: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """
        Filter record fields based on YAML configuration (include-only approach).

        Uses YAML config to determine which fields to send to AI:
        - If collection is configured in YAML: use include_fields allowlist
        - If collection not configured: exclude only global_exclusions (permissive)
        - If YAML not loaded: fallback to hardcoded METADATA_FIELDS

        Args:
            record: MongoDB document
            collection_name: Collection name (e.g., 'organizations')

        Returns:
            Filtered record with only allowed fields (JSON serializable)
        """
        from bson import ObjectId

        # Get global exclusions
        global_exclusions = set(self.field_config.get("global_exclusions", [])) if self.field_config else self.METADATA_FIELDS

        filtered = {}

        # Check if collection has specific configuration
        if self.field_config and "collections" in self.field_config:
            collections = self.field_config["collections"]

            if collection_name in collections:
                # INCLUDE-ONLY MODE: Use allowlist from YAML
                collection_config = collections[collection_name]
                include_fields = set(collection_config.get("include_fields", []))

                for k, v in record.items():
                    # Include only if in allowlist AND not in global exclusions AND not empty
                    if k in include_fields and k not in global_exclusions and v is not None and v != "":
                        if isinstance(v, ObjectId):
                            filtered[k] = str(v)
                        else:
                            filtered[k] = v

            else:
                # DEFAULT BEHAVIOR: Collection not configured, exclude only global exclusions
                for k, v in record.items():
                    if k not in global_exclusions and v is not None and v != "":
                        if isinstance(v, ObjectId):
                            filtered[k] = str(v)
                        else:
                            filtered[k] = v
        else:
            # YAML not loaded or no collections defined: use global exclusions only
            for k, v in record.items():
                if k not in global_exclusions and v is not None and v != "":
                    if isinstance(v, ObjectId):
                        filtered[k] = str(v)
                    else:
                        filtered[k] = v

        return filtered

    def _generate_slug_with_ai(
        self,
        record: Dict[str, Any],
        collection_name: str,
        existing_slugs: Optional[Set[str]] = None,
        previous_attempt: Optional[str] = None,
    ) -> str:
        """
        Generate slug using OpenAI gpt-5-nano.

        Args:
            record: Full record data
            collection_name: Collection name for YAML config lookup
            existing_slugs: Set of existing slugs to avoid
            previous_attempt: Previous slug that caused collision

        Returns:
            Generated slug string

        Raises:
            Exception: If API call fails
        """
        # Filter metadata fields using YAML config
        filtered_record = self._filter_metadata_fields(record, collection_name)

        # Build system instructions
        system_instructions = """You are a URL slug generator. Generate clean, SEO-friendly slugs.

Rules:
1. Use only lowercase letters, numbers, and hyphens
2. Replace spaces with hyphens
3. Remove special characters
4. Keep slugs SHORT and concise (target: 40-60 characters, max 70)
5. Focus on KEY words only - remove filler words (the, of, and, for, etc.)
6. Make slugs readable but BRIEF
7. For non-English text, transliterate to English
8. Include country/region context when relevant but keep it short

Examples of good slugs:
- "china-blockchain-smart-contract-standard" (41 chars)
- "hk-sfc-virtual-asset-regulatory-framework" (42 chars)
- "japan-fsa-crypto-exchange-guidelines" (37 chars)

Return ONLY the slug, no explanation or quotes."""

        # Build user message
        user_message = f"Generate a unique slug for this record:\n\n{json.dumps(filtered_record, indent=2)}"

        # Hybrid approach: Only send similar slugs on retry (not on first attempt)
        if previous_attempt:
            user_message += f"\n\nPrevious attempt '{previous_attempt}' caused collision. Generate alternative."

            # Send similar slugs for context (if enabled in config)
            if existing_slugs and self.ai_settings.get("send_existing_slugs_on_retry", True):
                max_similar = self.ai_settings.get("max_similar_slugs", 10)

                # Find slugs similar to the collision (share prefix/suffix with previous attempt)
                prefix_len = min(15, len(previous_attempt))
                similar_slugs = [s for s in existing_slugs if previous_attempt[:prefix_len] in s or s[:prefix_len] in previous_attempt][:max_similar]

                if similar_slugs:
                    user_message += f"\n\nSimilar existing slugs to avoid:\n{', '.join(similar_slugs)}"

        try:
            # Call OpenAI Responses API (gpt-5-nano on flex tier)
            response = self.openai_client.responses.create(
                model="gpt-5-nano",
                service_tier="flex",
                input=[
                    {"role": "developer", "content": system_instructions},
                    {"role": "user", "content": user_message},
                ],
            )

            self.stats["api_calls"] += 1

            # Extract slug from response
            slug = response.output_text.strip()

            # Clean up any quotes or extra characters
            slug = slug.strip('"').strip("'").strip()

            # Validate slug format
            if not slug or not self._is_valid_slug(slug):
                raise ValueError(f"Generated invalid slug: {slug}")

            return slug

        except Exception as e:
            self.stats["errors"] += 1
            raise Exception(f"Failed to generate slug with AI: {e!s}")

    def _is_valid_slug(self, slug: str) -> bool:
        """
        Validate slug format.

        Args:
            slug: Slug to validate

        Returns:
            True if valid, False otherwise
        """
        if not slug:
            return False

        # Check length (strict max: 70 characters)
        if len(slug) > 70:
            return False

        # Check characters (lowercase alphanumeric + hyphens)
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if not all(c in allowed_chars for c in slug):
            return False

        # Check for consecutive hyphens
        if "--" in slug:
            return False

        # Check start/end
        return not (slug.startswith("-") or slug.endswith("-"))

    def _increment_stat(self, stat_name: str, increment: int = 1):
        """
        Thread-safe increment of statistics counter.

        Args:
            stat_name: Name of the stat to increment
            increment: Amount to increment (default: 1)
        """
        with self.stats_lock:
            self.stats[stat_name] += increment

    def _check_and_enable_rate_limiter(self, error: Exception):
        """
        Adaptively enable rate limiter if 429 errors detected.

        Args:
            error: Exception from OpenAI API call
        """
        error_str = str(error).lower()
        if "429" in error_str or "rate limit" in error_str:
            with self.rate_limit_lock:
                if not self.rate_limiter_enabled:
                    self.rate_limiter_enabled = True
                    print("\n⚠️  Rate limit detected! Enabling adaptive rate limiter (10 req/sec)")
                self._increment_stat("rate_limit_errors")

    def _rate_limit_wait(self, min_interval: float = 0.1):
        """
        Wait if rate limiter is enabled.

        Args:
            min_interval: Minimum seconds between requests (default: 0.1 = 10 req/sec)
        """
        if self.rate_limiter_enabled:
            time.sleep(min_interval)

    def _thread_safe_generate_and_add_slug(
        self,
        record: Dict[str, Any],
        collection_name: str,
        existing_slugs: Set[str],
        max_retries: int = 5,
    ) -> Optional[str]:
        """
        Thread-safe slug generation with collision detection.

        This method generates a slug and atomically checks/adds it to existing_slugs
        to prevent race conditions between threads.

        Args:
            record: MongoDB document
            collection_name: Collection name for YAML config
            existing_slugs: Set of existing slugs (shared across threads)
            max_retries: Maximum collision retry attempts

        Returns:
            Generated slug if successful, None if failed after retries
        """
        # First attempt: generate slug outside lock
        self._rate_limit_wait()
        try:
            slug = self._generate_slug_with_ai(record, collection_name, existing_slugs)
        except Exception as e:
            self._check_and_enable_rate_limiter(e)
            self._increment_stat("errors")
            return None

        # Critical section: check collision and regenerate if needed
        with self.slug_lock:
            retry_count = 0
            while slug in existing_slugs and retry_count < max_retries:
                # Regenerate inside lock to ensure atomicity
                self._rate_limit_wait()
                try:
                    previous_slug = slug
                    slug = self._generate_slug_with_ai(record, collection_name, existing_slugs, previous_slug)
                    retry_count += 1
                    self._increment_stat("collisions_resolved")
                except Exception as e:
                    self._check_and_enable_rate_limiter(e)
                    self._increment_stat("errors")
                    return None

            # If still collision after retries, fail
            if slug in existing_slugs:
                return None

            # Success: add to set atomically
            existing_slugs.add(slug)
            return slug

    def _process_single_record(
        self,
        record: Dict[str, Any],
        collection_name: str,
        existing_slugs: Set[str],
        record_index: int,
        total_records: int,
        collection: Collection,
        test_mode: bool,
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single record (worker function for ThreadPoolExecutor).

        Args:
            record: MongoDB document
            collection_name: Collection name
            existing_slugs: Shared set of existing slugs
            record_index: Index of this record (for logging)
            total_records: Total number of records being processed
            collection: MongoDB collection for immediate writes
            test_mode: If True, skip database writes

        Returns:
            Dict with processing result, or None if failed
        """
        try:
            record_id = record.get("_id", "unknown")
            print(f"\n[{record_index}/{total_records}] Processing record {record_id}...")

            # Generate and add slug (thread-safe)
            slug = self._thread_safe_generate_and_add_slug(record, collection_name, existing_slugs)

            if not slug:
                print("  ❌ Failed to generate unique slug after retries")
                self._increment_stat("errors")
                return None

            # Write immediately to database (no queuing)
            if not test_mode:
                collection.update_one({"_id": record["_id"]}, {"$set": {"slug": slug}})

            # Update stats
            self._increment_stat("slugs_generated")
            self._increment_stat("total_processed")

            print(f"  ✅ Generated slug: '{slug}' (length: {len(slug)}) {'- Written to DB' if not test_mode else '- Test mode'}")

            # Return result for examples
            return {
                "id": str(record["_id"]),
                "slug": slug,
                "sample_data": self._filter_metadata_fields(record, collection_name),
            }

        except Exception as e:
            print(f"  ❌ Error processing record: {e!s}")
            self._increment_stat("errors")
            return None

    def _process_duplicate_record(
        self,
        record_id: Any,
        old_slug: str,
        collection: Collection,
        collection_name: str,
        existing_slugs: Set[str],
        record_index: int,
        total_duplicates: int,
        test_mode: bool,
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single duplicate record (worker function for ThreadPoolExecutor).

        Args:
            record_id: MongoDB document _id
            old_slug: The duplicate slug to replace
            collection: MongoDB collection
            collection_name: Collection name
            existing_slugs: Shared set of existing slugs
            record_index: Index of this duplicate (for logging)
            total_duplicates: Total number of duplicates being processed
            test_mode: If True, skip database writes

        Returns:
            Dict with processing result, or None if failed
        """
        try:
            print(f"\n[{record_index}/{total_duplicates}] Processing duplicate {record_id}...")

            # Fetch full record
            record = collection.find_one({"_id": record_id})
            if not record:
                print("  ❌ Record not found")
                self._increment_stat("errors")
                return None

            # Generate and add new slug (thread-safe)
            new_slug = self._thread_safe_generate_and_add_slug(record, collection_name, existing_slugs)

            if not new_slug:
                print("  ❌ Failed to generate unique slug after retries")
                self._increment_stat("errors")
                return None

            # Write immediately to database (no queuing)
            if not test_mode:
                collection.update_one({"_id": record_id}, {"$set": {"slug": new_slug}})

            # Update stats
            self._increment_stat("duplicates_fixed")
            self._increment_stat("total_processed")

            print(f"  ✅ Regenerated: '{old_slug}' → '{new_slug}' {'- Written to DB' if not test_mode else '- Test mode'}")

            # Return result for examples
            return {"id": str(record_id), "old_slug": old_slug, "new_slug": new_slug}

        except Exception as e:
            print(f"  ❌ Error processing duplicate: {e!s}")
            self._increment_stat("errors")
            return None

    def _get_existing_slugs(self, collection: Collection) -> Set[str]:
        """
        Get all existing slugs from collection.

        Args:
            collection: MongoDB collection

        Returns:
            Set of existing slug values
        """
        slugs = set()
        for doc in collection.find({"slug": {"$exists": True, "$nin": [None, ""]}}, {"slug": 1}):
            if doc.get("slug"):
                slugs.add(doc["slug"])
        return slugs

    def _find_missing_slug_records(self, collection: Collection, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find records with missing or empty slug field.

        Args:
            collection: MongoDB collection
            limit: Maximum number of records to return

        Returns:
            List of records missing slugs
        """
        query = {"$or": [{"slug": {"$exists": False}}, {"slug": None}, {"slug": ""}]}

        cursor = collection.find(query)
        if limit:
            cursor = cursor.limit(limit)

        return list(cursor)

    def _find_duplicate_slugs(self, collection: Collection) -> List[Dict[str, Any]]:
        """
        Find duplicate slug values using aggregation.

        Args:
            collection: MongoDB collection

        Returns:
            List of dicts with duplicate slug info
        """
        pipeline = [
            {"$match": {"slug": {"$exists": True, "$nin": [None, ""]}}},
            {"$group": {"_id": "$slug", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$sort": {"count": -1}},
        ]

        return list(collection.aggregate(pipeline))

    def fix_missing_slugs(
        self,
        database: str,
        collection_name: str,
        test_mode: bool = False,
        limit: Optional[int] = None,
        max_workers: int = 10,
    ) -> Dict[str, Any]:
        """
        Generate slugs for records missing slug field (multi-threaded).

        Args:
            database: Database name
            collection_name: Collection name
            test_mode: If True, don't actually update records
            limit: Maximum number of records to process
            max_workers: Number of concurrent worker threads (default: 10)

        Returns:
            Dict with operation results
        """
        print(f"\n{'=' * 60}")
        print("🔧 Fixing Missing Slugs (Multi-Threaded)")
        print(f"{'=' * 60}")
        print(f"Environment: {self.env}")
        print(f"Database: {database}")
        print(f"Collection: {collection_name}")
        print(f"Test Mode: {test_mode}")
        print(f"Limit: {limit or 'None'}")
        print(f"Workers: {max_workers}")
        print(f"{'=' * 60}\n")

        # Get collection
        db = get_database(self.client, database)
        collection = get_collection(db, collection_name)

        # Find records missing slugs
        print("🔍 Finding records with missing slugs...")
        missing_records = self._find_missing_slug_records(collection, limit)

        if not missing_records:
            print("✅ No records found with missing slugs")
            return {
                "operation": "fix_missing_slugs",
                "database": database,
                "collection": collection_name,
                "total_processed": 0,
                "slugs_generated": 0,
                "test_mode": test_mode,
            }

        print(f"📊 Found {len(missing_records)} records with missing slugs")

        # Get existing slugs for collision detection
        print("🔍 Loading existing slugs for collision detection...")
        existing_slugs = self._get_existing_slugs(collection)
        print(f"📊 Found {len(existing_slugs)} existing slugs")

        # Backup before changes
        if not test_mode:
            print("\n💾 Creating backup...")
            backup_file = backup_documents(
                collection=collection,
                filter_query={"_id": {"$in": [r["_id"] for r in missing_records]}},
                operation_name=f"slug_generation_{collection_name}",
                test_mode=False,
            )

            if not backup_file:
                print("❌ Backup failed - aborting operation")
                return {
                    "operation": "fix_missing_slugs",
                    "error": "Backup failed",
                    "test_mode": test_mode,
                }
            print(f"✅ Backup created: {backup_file}")

        # Generate slugs with multi-threading
        print(f"\n🤖 Generating slugs with AI (using {max_workers} workers)...")
        examples = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {}
            for idx, record in enumerate(missing_records, 1):
                future = executor.submit(
                    self._process_single_record,
                    record,
                    collection_name,
                    existing_slugs,
                    idx,
                    len(missing_records),
                    collection,  # Pass collection for immediate writes
                    test_mode,  # Pass test_mode
                )
                futures[future] = record

            # Collect results as they complete
            for future in as_completed(futures, timeout=930):  # 15.5 min timeout
                try:
                    result = future.result(timeout=60)  # 1 min per record timeout

                    if result and len(examples) < 10:
                        # Track examples (first 10)
                        examples.append(
                            {
                                "id": result["id"],
                                "generated_slug": result["slug"],
                                "sample_data": result["sample_data"],
                            }
                        )

                except Exception as e:
                    print(f"  ❌ Thread error: {e!s}")
                    self._increment_stat("errors")

        # Generate report
        result = {
            "operation": "fix_missing_slugs",
            "database": database,
            "collection": collection_name,
            "total_processed": self.stats["total_processed"],
            "slugs_generated": self.stats["slugs_generated"],
            "collisions_resolved": self.stats["collisions_resolved"],
            "api_calls": self.stats["api_calls"],
            "errors": self.stats["errors"],
            "test_mode": test_mode,
            "examples": examples,
        }

        print(f"\n{'=' * 60}")
        print("✅ Operation Complete")
        print(f"{'=' * 60}")
        print(f"Total Processed: {result['total_processed']}")
        print(f"Slugs Generated: {result['slugs_generated']}")
        print(f"Collisions Resolved: {result['collisions_resolved']}")
        print(f"API Calls: {result['api_calls']}")
        print(f"Errors: {result['errors']}")
        print(f"{'=' * 60}\n")

        return result

    def fix_duplicate_slugs(self, database: str, collection_name: str, test_mode: bool = False, max_workers: int = 10) -> Dict[str, Any]:
        """
        Find and regenerate duplicate slugs (multi-threaded).

        Keeps the first/oldest record with original slug,
        regenerates slugs for all duplicates.

        Args:
            database: Database name
            collection_name: Collection name
            test_mode: If True, don't actually update records
            max_workers: Number of concurrent worker threads (default: 10)

        Returns:
            Dict with operation results
        """
        print(f"\n{'=' * 60}")
        print("🔧 Fixing Duplicate Slugs (Multi-Threaded)")
        print(f"{'=' * 60}")
        print(f"Environment: {self.env}")
        print(f"Database: {database}")
        print(f"Collection: {collection_name}")
        print(f"Test Mode: {test_mode}")
        print(f"Workers: {max_workers}")
        print(f"{'=' * 60}\n")

        # Get collection
        db = get_database(self.client, database)
        collection = get_collection(db, collection_name)

        # Find duplicates
        print("🔍 Finding duplicate slugs...")
        duplicates = self._find_duplicate_slugs(collection)

        if not duplicates:
            print("✅ No duplicate slugs found")
            return {
                "operation": "fix_duplicate_slugs",
                "database": database,
                "collection": collection_name,
                "duplicates_found": 0,
                "duplicates_fixed": 0,
                "test_mode": test_mode,
            }

        total_duplicate_records = sum(d["count"] - 1 for d in duplicates)
        print(f"📊 Found {len(duplicates)} duplicate slugs affecting {total_duplicate_records} records")

        # Get existing slugs
        existing_slugs = self._get_existing_slugs(collection)

        # Collect all duplicates to process and create backup
        all_duplicates_to_fix = []
        backup_ids = []

        for dup_info in duplicates:
            slug = dup_info["_id"]
            ids = dup_info["ids"]

            # Keep first record, regenerate others
            ids_to_regenerate = ids[1:]  # Skip first ID

            for dup_id in ids_to_regenerate:
                all_duplicates_to_fix.append((dup_id, slug))
                backup_ids.append(dup_id)

        # Create single backup for all duplicates
        if not test_mode and backup_ids:
            print("\n💾 Creating backup for all duplicate records...")
            backup_file = backup_documents(
                collection=collection,
                filter_query={"_id": {"$in": backup_ids}},
                operation_name=f"duplicate_slug_fix_{collection_name}",
                test_mode=False,
            )

            if not backup_file:
                print("❌ Backup failed - aborting operation")
                return {
                    "operation": "fix_duplicate_slugs",
                    "error": "Backup failed",
                    "test_mode": test_mode,
                }
            print(f"✅ Backup created: {backup_file}")

        # Process duplicates with multi-threading
        print(f"\n🤖 Regenerating duplicate slugs with AI (using {max_workers} workers)...")
        examples = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {}
            for idx, (dup_id, old_slug) in enumerate(all_duplicates_to_fix, 1):
                future = executor.submit(
                    self._process_duplicate_record,
                    dup_id,
                    old_slug,
                    collection,
                    collection_name,
                    existing_slugs,
                    idx,
                    len(all_duplicates_to_fix),
                    test_mode,  # Pass test_mode for immediate writes
                )
                futures[future] = (dup_id, old_slug)

            # Collect results as they complete
            for future in as_completed(futures, timeout=930):  # 15.5 min timeout
                try:
                    result = future.result(timeout=60)  # 1 min per record timeout

                    if result and len(examples) < 10:
                        # Track examples (first 10)
                        examples.append(
                            {
                                "id": result["id"],
                                "old_slug": result["old_slug"],
                                "new_slug": result["new_slug"],
                            }
                        )

                except Exception as e:
                    print(f"  ❌ Thread error: {e!s}")
                    self._increment_stat("errors")

        # Generate report
        result = {
            "operation": "fix_duplicate_slugs",
            "database": database,
            "collection": collection_name,
            "duplicates_found": len(duplicates),
            "duplicates_fixed": self.stats["duplicates_fixed"],
            "collisions_resolved": self.stats["collisions_resolved"],
            "api_calls": self.stats["api_calls"],
            "errors": self.stats["errors"],
            "test_mode": test_mode,
            "examples": examples,
        }

        print(f"\n{'=' * 60}")
        print("✅ Operation Complete")
        print(f"{'=' * 60}")
        print(f"Duplicates Found: {result['duplicates_found']}")
        print(f"Duplicates Fixed: {result['duplicates_fixed']}")
        print(f"Collisions Resolved: {result['collisions_resolved']}")
        print(f"API Calls: {result['api_calls']}")
        print(f"Errors: {result['errors']}")
        print(f"{'=' * 60}\n")

        return result


def generate_slug_for_collection(
    env: str,
    database: str,
    collection: str,
    fix_missing: bool = True,
    fix_duplicates: bool = True,
    test_mode: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Convenience function to generate slugs for a collection.

    Args:
        env: Environment (PRD/DEV/UAT)
        database: Database name
        collection: Collection name
        fix_missing: Fix missing slugs
        fix_duplicates: Fix duplicate slugs
        test_mode: Dry run mode
        limit: Limit for missing slug fixes

    Returns:
        Dict with combined results
    """
    generator = SlugGenerator(env=env)
    results = {}

    if fix_missing:
        results["missing"] = generator.fix_missing_slugs(database=database, collection_name=collection, test_mode=test_mode, limit=limit)

    if fix_duplicates:
        results["duplicates"] = generator.fix_duplicate_slugs(database=database, collection_name=collection, test_mode=test_mode)

    return results
