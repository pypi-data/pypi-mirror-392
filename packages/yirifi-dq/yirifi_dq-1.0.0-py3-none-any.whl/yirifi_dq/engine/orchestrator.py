"""
Operation Orchestrator

The orchestrator is the heart of the CLI system. It coordinates all operations,
enforces safety rules, manages state transitions, and integrates with lib utilities.

Key responsibilities:
1. Create operation folder structure
2. Enforce auto-backup before destructive operations
3. Execute operations using lib utilities
4. Enforce auto-verification after operations
5. Update state database
6. Generate reports
7. Handle errors and rollbacks

NOTE: Uses state.db (SQLite) for operation tracking.
"""

import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from yirifi_dq.db.state_manager import StateManager, get_state_manager
from yirifi_dq.models.operation import (
    DuplicateCleanupConfig,
    OperationConfig,
    OperationResult,
    OperationStatus,
    OperationType,
    OrphanCleanupConfig,
    SlugGenerationConfig,
)
from yirifi_dq.models.state import OperationState
from yirifi_dq.core.mongodb import get_client, get_collection, get_database

# Import YAML utilities
from yirifi_dq.utils.path_validation import validate_safe_path_component


class OperationOrchestrator:
    """
    Orchestrates data quality operations from start to finish.

    This is the main engine that coordinates:
    - Folder creation
    - State management
    - Safety enforcement (backup, verification)
    - Execution via lib utilities
    - Documentation (INDEX.json, reports)
    """

    def __init__(self, state_manager: Optional[StateManager] = None):
        """
        Initialize orchestrator.

        Args:
            state_manager: StateManager instance (uses singleton if None)
        """
        self.state_manager = state_manager or get_state_manager()
        self.framework_root = Path(__file__).parent.parent.parent  # yirifi-data-fixes/

    def create_operation(self, config: OperationConfig) -> str:
        """
        Create a new operation with folder structure and initial state.

        Args:
            config: OperationConfig (or subclass)

        Returns:
            operation_id

        Raises:
            ValueError: If a similar active operation already exists
        """
        # Check for duplicate/conflicting operations
        self._check_duplicate_operation(config)

        # Generate operation ID
        operation_id = self._generate_operation_id(config)

        # Create operation folder structure
        operation_folder = self._create_folder_structure(config, operation_id)

        # Create initial state
        operation_state = OperationState(
            operation_id=operation_id,
            operation_name=operation_id,
            operation_type=config.operation_type,
            database=config.database,
            collection=config.collection,
            field=config.field,
            environment=config.environment,
            test_mode=config.test_mode,
            status=OperationStatus.PLANNING,
            operation_folder=str(operation_folder),
            created_by="cli",
        )

        # Save to state database
        self.state_manager.create_operation(operation_state)

        # Log creation
        self.state_manager.add_log(
            operation_id,
            "INFO",
            f"Operation created: {config.operation_type.value}",
            {
                "database": config.database,
                "collection": config.collection,
                "field": config.field,
                "environment": config.environment.value,
                "test_mode": config.test_mode,
            },
        )

        # Save configuration
        self._save_config(operation_folder, config)

        return operation_id

    def execute_operation(self, operation_id: str) -> OperationResult:
        """
        Execute an operation end-to-end.

        Workflow:
        1. Pre-flight checks
        2. Acquire lock
        3. Connect to MongoDB
        4. Auto-backup (if destructive)
        5. Execute operation
        6. Auto-verify
        7. Update INDEX.json
        8. Generate report
        9. Release lock

        Args:
            operation_id: Operation ID

        Returns:
            OperationResult
        """
        started_at = datetime.utcnow()
        operation = None  # Initialize to None for finally block
        client = None  # Initialize to None for connection cleanup

        try:
            # Get operation state
            operation = self.state_manager.get_operation(operation_id)
            if not operation:
                raise ValueError(f"Operation {operation_id} not found")

            # Update status to EXECUTING
            self._update_status(operation_id, OperationStatus.EXECUTING, "Starting execution")

            # Pre-flight checks
            self._preflight_checks(operation)

            # Acquire lock
            if not self._acquire_lock(operation):
                raise RuntimeError(f"Cannot acquire lock on {operation.database}.{operation.collection}")

            # Load configuration
            config = self._load_config(operation.operation_folder)

            # Connect to MongoDB
            client = get_client(env=operation.environment.value)
            db = get_database(client, operation.database)
            collection = get_collection(db, operation.collection)

            # Execute based on operation type
            result = None
            if operation.operation_type == OperationType.DUPLICATE_CLEANUP:
                result = self._execute_duplicate_cleanup(operation, collection, config)
            elif operation.operation_type == OperationType.ORPHAN_CLEANUP:
                result = self._execute_orphan_cleanup(operation, db, collection, config)
            elif operation.operation_type == OperationType.SLUG_GENERATION:
                result = self._execute_slug_generation(operation, collection, config)
            else:
                raise NotImplementedError(f"Operation type {operation.operation_type} not yet implemented")

            # Auto-verify
            if config.auto_verify:
                self._update_status(operation_id, OperationStatus.VERIFYING, "Running verification")
                verification = self._verify_operation(operation, collection, config)
                if not verification["passed"]:
                    raise RuntimeError(f"Verification failed: {verification['failures']}")

            # Generate report
            report_file = self._generate_report(operation, result)
            self.state_manager.update_operation(operation_id, report_file=report_file)

            # Mark as completed
            completed_at = datetime.utcnow()
            self._update_status(operation_id, OperationStatus.COMPLETED, "Operation completed successfully")
            self.state_manager.update_operation(
                operation_id,
                completed_at=completed_at,
                records_affected=result.get("records_affected", 0),
                records_deleted=result.get("records_deleted", 0),
                records_updated=result.get("records_updated", 0),
            )

            self.state_manager.add_log(operation_id, "INFO", "Operation completed successfully", result)

            return OperationResult(
                operation_id=operation_id,
                status=OperationStatus.COMPLETED,
                records_affected=result.get("records_affected", 0),
                records_deleted=result.get("records_deleted", 0),
                records_updated=result.get("records_updated", 0),
                backup_file=result.get("backup_file"),
                report_file=report_file,
                started_at=started_at,
                completed_at=completed_at,
            )

        except Exception as e:
            # Mark as failed
            error_message = str(e)
            error_trace = traceback.format_exc()

            self._update_status(operation_id, OperationStatus.FAILED, error_message)
            self.state_manager.update_operation(operation_id, error_message=error_message, error_stack_trace=error_trace)
            self.state_manager.add_log(operation_id, "ERROR", error_message, {"trace": error_trace})

            return OperationResult(
                operation_id=operation_id,
                status=OperationStatus.FAILED,
                error_message=error_message,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        finally:
            # Always release lock and close connection
            if operation:
                self._release_lock(operation)

            # Close MongoDB connection to prevent connection leaks
            if client:
                try:
                    client.close()
                except Exception as e:
                    # Log but don't raise - we're in cleanup
                    if operation:
                        self.state_manager.add_log(
                            operation.operation_id,
                            "WARNING",
                            f"Error closing MongoDB connection: {e!s}",
                        )

    # ========== Execution Methods ==========

    def _execute_duplicate_cleanup(self, operation: OperationState, collection, config: DuplicateCleanupConfig) -> Dict[str, Any]:
        """Execute duplicate cleanup operation."""
        from yirifi_dq.core.fixers import remove_duplicates
        from yirifi_dq.core.validators import find_duplicates

        self.state_manager.add_log(operation.operation_id, "INFO", "Finding duplicates...")

        # Find duplicates
        duplicates = find_duplicates(collection, config.field, return_details=True)

        if not duplicates or len(duplicates) == 0:
            self.state_manager.add_log(operation.operation_id, "INFO", "No duplicates found")
            return {"records_affected": 0, "records_deleted": 0, "duplicates_found": 0}

        duplicate_count = len(duplicates)
        self.state_manager.add_log(
            operation.operation_id,
            "INFO",
            f"Found {duplicate_count} duplicate groups",
            {"duplicate_count": duplicate_count},
        )

        # Test mode limiting
        if config.test_mode:
            self.state_manager.add_log(
                operation.operation_id,
                "WARNING",
                f"TEST MODE: Limiting to {config.test_limit} records",
            )

        # Auto-backup before deletion
        if config.auto_backup:
            self.state_manager.add_log(operation.operation_id, "INFO", "Creating backup...")
            # Backup handled internally by remove_duplicates

        # Remove duplicates
        self.state_manager.add_log(operation.operation_id, "INFO", "Removing duplicates...")
        result = remove_duplicates(
            collection=collection,
            field=config.field,
            keep_strategy=config.keep_strategy.value,
            test_mode=config.test_mode,
            test_limit=config.test_limit,
            auto_backup=config.auto_backup,
        )

        # Update state with backup file
        if result.get("backup_file"):
            self.state_manager.update_operation(operation.operation_id, backup_file=result["backup_file"])

        return result

    def _execute_orphan_cleanup(
        self,
        operation: OperationState,
        db,  # Database instance passed from execute_operation
        collection,
        config: OrphanCleanupConfig,
    ) -> Dict[str, Any]:
        """Execute orphan cleanup operation."""
        from yirifi_dq.core.fixers import clean_orphans
        from yirifi_dq.core.validators import find_orphans

        self.state_manager.add_log(operation.operation_id, "INFO", "Finding orphans...")

        # Get parent collection (reuse existing db connection)
        parent_collection = get_collection(db, config.parent_collection)

        # Find orphans
        orphans = find_orphans(
            collection=collection,
            foreign_key_field=config.foreign_key_field,
            parent_collection=parent_collection,
            parent_key_field=config.parent_key_field,
            return_details=True,
        )

        if not orphans or len(orphans) == 0:
            self.state_manager.add_log(operation.operation_id, "INFO", "No orphans found")
            return {"records_affected": 0, "records_deleted": 0, "orphans_found": 0}

        orphan_count = len(orphans)
        self.state_manager.add_log(operation.operation_id, "INFO", f"Found {orphan_count} orphan records")

        # Clean orphans
        if config.delete_orphans:
            self.state_manager.add_log(operation.operation_id, "INFO", "Cleaning orphans...")
            result = clean_orphans(
                collection=collection,
                orphan_ids=[o["_id"] for o in orphans],
                test_mode=config.test_mode,
                test_limit=config.test_limit,
                auto_backup=config.auto_backup,
            )
        else:
            self.state_manager.add_log(operation.operation_id, "INFO", "Report-only mode, not deleting")
            result = {
                "records_affected": 0,
                "records_deleted": 0,
                "orphans_found": orphan_count,
                "orphans": orphans,
            }

        return result

    def _execute_slug_generation(self, operation: OperationState, collection, config: SlugGenerationConfig) -> Dict[str, Any]:
        """Execute slug generation operation."""
        from yirifi_dq.core.generators.slugs import SlugGenerator

        self.state_manager.add_log(operation.operation_id, "INFO", "Initializing slug generator...")

        # Initialize SlugGenerator
        generator = SlugGenerator(env=operation.environment.value)
        results = {"operations": {}}

        # Fix missing slugs
        if config.fix_missing:
            self.state_manager.add_log(operation.operation_id, "INFO", "Fixing missing slugs...")

            missing_result = generator.fix_missing_slugs(
                database=operation.database,
                collection_name=operation.collection,
                test_mode=config.test_mode,
                limit=config.limit if config.limit else (config.test_limit if config.test_mode else None),
                max_workers=config.max_workers,
            )
            results["operations"]["fix_missing_slugs"] = missing_result

            self.state_manager.add_log(
                operation.operation_id,
                "INFO",
                f"Missing slugs: {missing_result.get('slugs_generated', 0)} generated",
                missing_result,
            )

        # Fix duplicate slugs
        if config.fix_duplicates:
            self.state_manager.add_log(operation.operation_id, "INFO", "Fixing duplicate slugs...")

            duplicate_result = generator.fix_duplicate_slugs(
                database=operation.database,
                collection_name=operation.collection,
                test_mode=config.test_mode,
                max_workers=config.max_workers,
            )
            results["operations"]["fix_duplicate_slugs"] = duplicate_result

            self.state_manager.add_log(
                operation.operation_id,
                "INFO",
                f"Duplicate slugs: {duplicate_result.get('duplicates_fixed', 0)} fixed",
                duplicate_result,
            )

        # Aggregate results
        total_processed = 0
        total_generated = 0

        if "fix_missing_slugs" in results["operations"]:
            total_processed += results["operations"]["fix_missing_slugs"].get("total_processed", 0)
            total_generated += results["operations"]["fix_missing_slugs"].get("slugs_generated", 0)

        if "fix_duplicate_slugs" in results["operations"]:
            total_processed += results["operations"]["fix_duplicate_slugs"].get("duplicates_found", 0)
            total_generated += results["operations"]["fix_duplicate_slugs"].get("duplicates_fixed", 0)

        return {
            "records_affected": total_processed,
            "records_updated": total_generated,
            "operations": results["operations"],
        }

    # ========== Safety & Verification Methods ==========

    def _preflight_checks(self, operation: OperationState):
        """
        Run pre-flight checks before execution.

        Validates:
        - Operation folder exists
        - Not already completed
        - Not locked by another operation
        - Database and collection exist in MongoDB
        - Field exists in collection (if field-specific operation)
        """
        self.state_manager.add_log(operation.operation_id, "INFO", "Running pre-flight checks...")

        # Check if operation folder exists
        if not os.path.exists(operation.operation_folder):
            raise RuntimeError(f"Operation folder not found: {operation.operation_folder}")

        # Check if already completed
        if operation.status == OperationStatus.COMPLETED:
            raise RuntimeError(f"Operation {operation.operation_id} already completed")

        # Check if locked by another operation
        if self.state_manager.is_locked(operation.database, operation.collection):
            raise RuntimeError(f"Collection {operation.database}.{operation.collection} is locked by another operation")

        # Validate MongoDB database and collection exist
        self._validate_mongodb_target(operation)

        self.state_manager.add_log(operation.operation_id, "INFO", "Pre-flight checks passed")

    def _verify_operation(self, operation: OperationState, collection, config: OperationConfig) -> Dict[str, Any]:
        """Run verification checks after operation."""
        from yirifi_dq.core.validators import find_duplicates

        verification = {"passed": True, "checks": [], "failures": []}

        # Verify no duplicates remain (if duplicate cleanup)
        if operation.operation_type == OperationType.DUPLICATE_CLEANUP:
            duplicates = find_duplicates(collection, config.field)
            if duplicates and len(duplicates) > 0:
                verification["passed"] = False
                verification["failures"].append(f"Found {len(duplicates)} remaining duplicates")
            else:
                verification["checks"].append("No duplicates remain")

        # Verify record counts
        total_count = collection.count_documents({})
        verification["checks"].append(f"Total records: {total_count}")

        self.state_manager.add_log(
            operation.operation_id,
            "INFO" if verification["passed"] else "ERROR",
            "Verification " + ("passed" if verification["passed"] else "failed"),
            verification,
        )

        return verification

    # ========== Helper Methods ==========

    def _validate_mongodb_target(self, operation: OperationState) -> None:
        """
        Validate that MongoDB database, collection, and field (if applicable) exist.

        Args:
            operation: OperationState to validate

        Raises:
            ValueError: If database, collection, or field doesn't exist
        """
        client = None
        try:
            # Connect to MongoDB
            client = get_client(env=operation.environment.value)

            # Check if database exists
            db_list = client.list_database_names()
            if operation.database not in db_list:
                raise ValueError(f"Database '{operation.database}' does not exist in {operation.environment.value} environment. Available databases: {', '.join(sorted(db_list))}")

            # Check if collection exists
            db = get_database(client, operation.database)
            coll_list = db.list_collection_names()
            if operation.collection not in coll_list:
                raise ValueError(f"Collection '{operation.collection}' does not exist in database '{operation.database}'. Available collections: {', '.join(sorted(coll_list))}")

            # If field-specific operation, validate field exists in at least one document
            if operation.field:
                collection = get_collection(db, operation.collection)

                # Check if field exists in collection schema (sample 100 documents)
                sample_doc = collection.find_one({operation.field: {"$exists": True}})

                if not sample_doc:
                    # Field might still exist but not in sampled docs, check count
                    field_count = collection.count_documents({operation.field: {"$exists": True}})
                    if field_count == 0:
                        raise ValueError(f"Field '{operation.field}' does not exist in any documents in collection '{operation.database}.{operation.collection}'")

            self.state_manager.add_log(
                operation.operation_id,
                "INFO",
                f"Validated MongoDB target: {operation.database}.{operation.collection}" + (f" (field: {operation.field})" if operation.field else ""),
            )

        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass  # Best effort cleanup

    def _check_duplicate_operation(self, config: OperationConfig) -> None:
        """
        Check for duplicate or conflicting operations.

        Prevents creating a new operation if there's already an active (non-terminal)
        operation on the same database/collection/field with the same type.

        Args:
            config: OperationConfig to check

        Raises:
            ValueError: If a conflicting operation exists
        """
        # Get all operations for this database/collection
        existing_ops = self.state_manager.list_operations(
            database=config.database,
            collection=config.collection,
            limit=100,  # Check last 100 operations
        )

        # Define terminal statuses (operations that are "done")
        terminal_statuses = {
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.ROLLED_BACK,
        }

        # Check for active operations with same characteristics
        for op in existing_ops:
            # Skip if operation is in terminal state
            if op.status in terminal_statuses:
                continue

            # Check if it's the same type of operation
            if op.operation_type != config.operation_type:
                continue

            # Check if it's on the same field (if field-specific)
            if config.field and op.field != config.field:
                continue

            # Found a conflicting operation
            raise ValueError(
                f"Cannot create operation: Active {op.operation_type.value} operation already exists "
                f"on {op.database}.{op.collection}"
                + (f" (field: {op.field})" if op.field else "")
                + f"\nOperation ID: {op.operation_id}, Status: {op.status.value}"
                + "\nPlease wait for it to complete, or cancel it first."
            )

    def _generate_operation_id(self, config: OperationConfig) -> str:
        """Generate unique operation ID."""
        type_short = config.operation_type.value.replace("-", "_")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{type_short}_{config.collection}_{timestamp}"

    def _create_folder_structure(self, config: OperationConfig, operation_id: str) -> Path:
        """
        Create 5-level folder structure.

        databases/{database}/{collection}/{field}/{type}/{operation_name}/

        Raises:
            ValueError: If any path component contains unsafe characters (prevents path traversal)
        """
        # Validate all path components to prevent path traversal attacks
        validate_safe_path_component(config.database, "Database name")
        validate_safe_path_component(config.collection, "Collection name")

        if config.field:
            validate_safe_path_component(config.field, "Field name")

        validate_safe_path_component(operation_id, "Operation ID")

        # Determine type based on operation_type
        type_map = {
            OperationType.DUPLICATE_CLEANUP: f"duplicate_{config.field}" if config.field else "duplicates",
            OperationType.ORPHAN_CLEANUP: "orphans",
            OperationType.DATA_NORMALIZATION: f"normalize_{config.field}" if config.field else "normalization",
            OperationType.FIELD_MIGRATION: "migration",
            OperationType.CUSTOM: "custom",
        }

        type_folder = type_map.get(config.operation_type, "unknown")

        # Validate the generated type_folder as well (though it's internally generated)
        validate_safe_path_component(type_folder, "Type folder")

        # Build path (safe now that all components are validated)
        operation_folder = self.framework_root / "databases" / config.database / config.collection

        if config.field:
            operation_folder = operation_folder / config.field

        operation_folder = operation_folder / type_folder / operation_id

        # Create folders
        (operation_folder / "input").mkdir(parents=True, exist_ok=True)
        (operation_folder / "scripts").mkdir(parents=True, exist_ok=True)
        (operation_folder / "output").mkdir(parents=True, exist_ok=True)
        (operation_folder / "analysis").mkdir(parents=True, exist_ok=True)

        # Create OPERATION.md placeholder
        operation_md = operation_folder / "OPERATION.md"
        if not operation_md.exists():
            with open(operation_md, "w") as f:
                f.write(f"# {operation_id}\n\n")
                f.write(f"**Type:** {config.operation_type.value}\n")
                f.write(f"**Database:** {config.database}\n")
                f.write(f"**Collection:** {config.collection}\n")
                if config.field:
                    f.write(f"**Field:** {config.field}\n")
                f.write(f"**Environment:** {config.environment.value}\n")
                f.write(f"**Test Mode:** {config.test_mode}\n\n")
                f.write("## Status\n\nIn progress...\n")

        return operation_folder

    def _save_config(self, operation_folder: Path, config: OperationConfig):
        """Save operation configuration as JSON."""
        config_file = operation_folder / "config.json"
        with open(config_file, "w") as f:
            json.dump(config.dict(), f, indent=2, default=str)

    def _load_config(self, operation_folder: str) -> OperationConfig:
        """Load operation configuration from JSON."""
        config_file = Path(operation_folder) / "config.json"
        with open(config_file) as f:
            config_data = json.load(f)

        # Reconstruct appropriate config class
        operation_type = OperationType(config_data["operation_type"])

        if operation_type == OperationType.DUPLICATE_CLEANUP:
            return DuplicateCleanupConfig(**config_data)
        elif operation_type == OperationType.ORPHAN_CLEANUP:
            return OrphanCleanupConfig(**config_data)
        else:
            return OperationConfig(**config_data)

    def _update_status(self, operation_id: str, status: OperationStatus, message: str):
        """Update operation status and log."""
        self.state_manager.update_operation(operation_id, status=status.value)
        self.state_manager.add_log(operation_id, "INFO", message)

    def _acquire_lock(self, operation: OperationState) -> bool:
        """Acquire lock on collection."""
        return self.state_manager.acquire_lock(
            database=operation.database,
            collection=operation.collection,
            operation_id=operation.operation_id,
            locked_by="cli",
            duration_minutes=60,
            reason=f"{operation.operation_type.value} operation",
        )

    def _release_lock(self, operation: OperationState):
        """Release lock on collection."""
        self.state_manager.release_lock(operation.database, operation.collection)

    def _generate_report(self, operation: OperationState, result: Dict[str, Any]) -> str:
        """Generate operation report."""
        output_folder = Path(operation.operation_folder) / "output"
        report_file = output_folder / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            "operation_id": operation.operation_id,
            "operation_type": operation.operation_type.value,
            "database": operation.database,
            "collection": operation.collection,
            "field": operation.field,
            "environment": operation.environment.value,
            "test_mode": operation.test_mode,
            "created_at": operation.created_at.isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "result": result,
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(report_file)
