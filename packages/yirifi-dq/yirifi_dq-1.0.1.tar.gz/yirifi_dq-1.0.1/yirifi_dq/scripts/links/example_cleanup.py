"""
Example custom script - Clean old duplicate links.

This script demonstrates how to write custom business logic that
composes core framework utilities.

Business Logic:
1. Find duplicate links based on URL
2. Filter duplicates older than age threshold
3. Remove old duplicates, keeping the oldest record
4. Find orphaned articles (no matching link)
5. Optionally archive orphaned articles

This shows how custom scripts can:
- Access framework utilities via context (no imports needed)
- Implement complex multi-step business logic
- Use parameters from YAML config
- Return detailed results
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from yirifi_dq.plugins import BaseScript, ScriptContext, ScriptResult, ScriptExecutionError, DryRunPreview


class ExampleCleanupScript(BaseScript):
    """
    Example script demonstrating custom business logic.

    This script removes duplicate links older than a threshold
    and optionally archives orphaned articles.
    """

    def execute(self, context: ScriptContext) -> ScriptResult:
        """
        Execute cleanup logic.

        Args:
            context: Pre-initialized context with database, parameters, utilities

        Returns:
            ScriptResult with metrics and details
        """
        # Extract parameters from YAML config
        age_threshold_days = context.parameters.get("age_threshold_days", 90)
        field = context.parameters.get("field", "url")
        keep_strategy = context.parameters.get("keep_strategy", "oldest")
        archive_orphans = context.parameters.get("archive_orphans", False)

        context.logger.info(
            f"Starting cleanup: field={field}, age_threshold={age_threshold_days} days"
        )

        # Step 1: Find duplicates using framework validator
        context.logger.info("Step 1: Finding duplicates...")
        duplicates = context.validators.find_duplicates(
            context.collection, field, return_details=True
        )

        context.logger.info(f"Found {len(duplicates)} duplicate groups")

        if not duplicates:
            return ScriptResult(
                success=True,
                message="No duplicates found",
                records_processed=0,
                records_deleted=0,
            )

        # Step 2: Filter old duplicates (custom business logic)
        context.logger.info("Step 2: Filtering old duplicates...")
        cutoff_date = datetime.utcnow() - timedelta(days=age_threshold_days)
        old_duplicate_ids = self._filter_old_duplicates(
            duplicates, cutoff_date, keep_strategy
        )

        context.logger.info(f"Identified {len(old_duplicate_ids)} old duplicates to remove")

        # Step 3: Remove old duplicates using framework fixer
        if old_duplicate_ids:
            context.logger.info("Step 3: Removing old duplicates...")

            if context.test_mode:
                # Limit to test_limit in test mode
                old_duplicate_ids = old_duplicate_ids[:10]
                context.logger.info(f"Test mode: limiting to {len(old_duplicate_ids)} records")

            if not context.dry_run:
                delete_result = context.collection.delete_many(
                    {"_id": {"$in": old_duplicate_ids}}
                )
                deleted_count = delete_result.deleted_count
                context.logger.info(f"Deleted {deleted_count} records")
            else:
                deleted_count = len(old_duplicate_ids)
                context.logger.info(f"Dry run: would delete {deleted_count} records")
        else:
            deleted_count = 0

        # Step 4: Find orphaned articles (if requested)
        orphans_archived = 0
        if archive_orphans:
            context.logger.info("Step 4: Finding orphaned articles...")
            articles_collection = context.database["articlesdocuments"]

            orphans = context.validators.find_orphans(
                source_collection=articles_collection,
                target_collection=context.collection,
                source_field="articleYid",
                target_field="link_yid",
            )

            context.logger.info(f"Found {len(orphans)} orphaned articles")

            # Step 5: Archive orphans
            if orphans and not context.dry_run:
                context.logger.info("Step 5: Archiving orphaned articles...")
                orphan_ids = [o["_id"] for o in orphans]

                if context.test_mode:
                    orphan_ids = orphan_ids[:10]

                archive_result = articles_collection.update_many(
                    {"_id": {"$in": orphan_ids}},
                    {
                        "$set": {
                            "archived": True,
                            "archived_at": datetime.utcnow(),
                            "archived_reason": "orphaned_after_link_cleanup",
                        }
                    },
                )
                orphans_archived = archive_result.modified_count
                context.logger.info(f"Archived {orphans_archived} articles")

        # Build result
        return ScriptResult(
            success=True,
            message=(
                f"Cleaned {deleted_count} old duplicates"
                + (f", archived {orphans_archived} orphans" if archive_orphans else "")
            ),
            records_processed=len(duplicates),
            records_deleted=deleted_count,
            records_modified=orphans_archived,
            details={
                "duplicate_groups_found": len(duplicates),
                "old_duplicates_removed": deleted_count,
                "orphans_found": len(orphans) if archive_orphans else 0,
                "orphans_archived": orphans_archived,
                "cutoff_date": cutoff_date.isoformat(),
                "field": field,
                "keep_strategy": keep_strategy,
            },
            warnings=[
                f"{len(duplicates) - deleted_count} duplicate groups were not old enough to remove"
            ]
            if deleted_count < len(duplicates)
            else [],
        )

    def _filter_old_duplicates(
        self, duplicates: List[Dict], cutoff_date: datetime, keep_strategy: str
    ) -> List[Any]:
        """
        Filter duplicates to only those older than cutoff date.

        This is custom business logic specific to this script.

        Args:
            duplicates: List of duplicate groups
            cutoff_date: Only keep duplicates older than this
            keep_strategy: Strategy for choosing which to keep

        Returns:
            List of document IDs to delete
        """
        ids_to_delete = []

        for dup_group in duplicates:
            # Get documents in this group
            docs = dup_group.get("documents", [])

            # Filter to only old documents
            old_docs = [
                doc for doc in docs if doc.get("created_at", datetime.min) < cutoff_date
            ]

            if len(old_docs) <= 1:
                # Not enough old docs to have duplicates
                continue

            # Sort based on keep strategy
            if keep_strategy == "oldest":
                old_docs.sort(key=lambda x: x.get("created_at", datetime.min))
            elif keep_strategy == "newest":
                old_docs.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            elif keep_strategy == "most_complete":
                old_docs.sort(
                    key=lambda x: sum(1 for v in x.values() if v is not None), reverse=True
                )

            # Keep first, delete rest
            ids_to_delete.extend([doc["_id"] for doc in old_docs[1:]])

        return ids_to_delete

    def validate_parameters(self, context: ScriptContext) -> List[str]:
        """
        Custom parameter validation.

        Args:
            context: Script context

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        age_threshold = context.parameters.get("age_threshold_days")
        if age_threshold and age_threshold < 1:
            errors.append("age_threshold_days must be at least 1")

        return errors

    def pre_execute_checks(self, context: ScriptContext) -> bool:
        """
        Pre-flight checks.

        Args:
            context: Script context

        Returns:
            True if safe to proceed
        """
        # Check collection is not empty
        count = context.collection.count_documents({})
        if count == 0:
            context.logger.warning("Collection is empty, skipping")
            return False

        context.logger.info(f"Collection has {count} documents")
        return True

    def get_affected_records_filter(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return filter for affected records (for optimized backup).

        Args:
            parameters: Script parameters

        Returns:
            MongoDB filter for affected records
        """
        age_threshold = parameters.get("age_threshold_days", 90)
        cutoff_date = datetime.utcnow() - timedelta(days=age_threshold)

        return {"created_at": {"$lt": cutoff_date}}

    def dry_run_preview(self, context: ScriptContext) -> DryRunPreview:
        """
        Generate preview of what would be affected by this cleanup.

        Args:
            context: Script context

        Returns:
            DryRunPreview with preview information
        """
        # Extract parameters
        age_threshold_days = context.parameters.get("age_threshold_days", 90)
        field = context.parameters.get("field", "url")
        keep_strategy = context.parameters.get("keep_strategy", "oldest")
        archive_orphans = context.parameters.get("archive_orphans", False)

        # Find duplicates
        duplicates = context.validators.find_duplicates(
            context.collection, field, return_details=True
        )

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=age_threshold_days)

        # Filter old duplicates
        old_duplicate_ids = self._filter_old_duplicates(
            duplicates, cutoff_date, keep_strategy
        )

        # Count orphans if requested
        orphans_count = 0
        if archive_orphans:
            articles_collection = context.database["articlesdocuments"]
            orphans = context.validators.find_orphans(
                source_collection=articles_collection,
                target_collection=context.collection,
                source_field="articleYid",
                target_field="link_yid",
            )
            orphans_count = len(orphans)

        # Build sample records
        samples = []
        for group in duplicates[:5]:
            value = group.get("value", "N/A")
            count = len(group.get("documents", []))
            samples.append({
                "value": value if len(str(value)) < 50 else str(value)[:47] + "...",
                "count": count
            })

        # Build estimated impact
        if archive_orphans:
            impact = f"{len(old_duplicate_ids)} old duplicates would be deleted, {orphans_count} orphaned articles would be archived"
        else:
            impact = f"{len(old_duplicate_ids)} old duplicates would be deleted"

        # Build warnings
        warnings = []
        if len(duplicates) == 0:
            warnings.append("No duplicate groups found")
        elif len(old_duplicate_ids) == 0:
            warnings.append(f"No duplicates older than {age_threshold_days} days found")

        if archive_orphans and orphans_count > 0:
            warnings.append(f"{orphans_count} orphaned articles would be archived - review carefully!")

        return DryRunPreview(
            operation_summary=f"Clean old duplicate {field} (older than {age_threshold_days} days)",
            total_records=context.collection.count_documents({}),
            affected_records_count=len(old_duplicate_ids) + (orphans_count if archive_orphans else 0),
            affected_groups_count=len(duplicates),
            sample_records=samples,
            estimated_impact=impact,
            safety_features=[
                "Backup would be created before deletion",
                f"Test mode: {'ON (limited to 10 records)' if context.test_mode else 'OFF (full execution)'}",
                "Verification would run after execution",
            ],
            warnings=warnings,
        )
