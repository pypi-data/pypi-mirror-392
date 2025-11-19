"""
Base classes for the plugin system.

This module provides the foundation for creating custom business logic scripts:
- BaseScript: Abstract base class that all scripts must inherit from
- ScriptContext: Dependency injection container passed to scripts
- ScriptResult: Standardized return value from script execution

Example:
    >>> from yirifi_dq.plugins.base_script import BaseScript, ScriptContext, ScriptResult
    >>>
    >>> class MyCustomScript(BaseScript):
    ...     def execute(self, context: ScriptContext) -> ScriptResult:
    ...         # Your business logic here
    ...         duplicates = context.validators.find_duplicates(
    ...             context.collection,
    ...             context.parameters['field']
    ...         )
    ...
    ...         return ScriptResult(
    ...             success=True,
    ...             message=f"Found {len(duplicates)} duplicates",
    ...             records_processed=len(duplicates)
    ...         )
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo.collection import Collection
from pymongo.database import Database


@dataclass
class ScriptContext:
    """
    Dependency injection container passed to every script.

    The orchestrator populates this from YAML config and runtime state.
    Scripts access framework utilities through this context instead of
    importing directly, which enables:
    - Easy mocking for tests
    - Loose coupling between scripts and framework
    - Clear dependency visualization

    Attributes:
        database: Pre-initialized MongoDB database handle
        collection: Pre-initialized MongoDB collection handle
        parameters: User-provided parameters (validated from YAML)
        validators: yirifi_dq.core.validators module (lazy-loaded)
        fixers: yirifi_dq.core.fixers module (lazy-loaded)
        analyzers: yirifi_dq.core.analyzers module (lazy-loaded)
        generators: yirifi_dq.core.generators module (lazy-loaded)
        operation_id: Unique operation ID (for logging/state)
        environment: Environment (DEV/UAT/PRD)
        test_mode: Whether running in test mode (limit records)
        dry_run: Whether to simulate without making changes
        state_manager: StateManager instance for logging
        logger: Logger instance for this operation
        backup_path: Path to backup file (if created)

    Example:
        >>> def execute(self, context: ScriptContext) -> ScriptResult:
        ...     # Use validators from context (no import needed)
        ...     duplicates = context.validators.find_duplicates(
        ...         context.collection,
        ...         context.parameters['field']
        ...     )
        ...
        ...     # Use fixers from context
        ...     result = context.fixers.remove_duplicates(
        ...         collection=context.collection,
        ...         field=context.parameters['field'],
        ...         test_mode=context.test_mode
        ...     )
        ...
        ...     # Log to state database
        ...     context.logger.info(f"Removed {result['deleted_count']} duplicates")
    """

    # Database connections (pre-initialized by orchestrator)
    database: Database
    collection: Collection

    # User-provided parameters (validated from YAML)
    parameters: Dict[str, Any]

    # Framework utilities (lazy-loaded modules)
    validators: Any  # yirifi_dq.core.validators module
    fixers: Any  # yirifi_dq.core.fixers module
    analyzers: Any  # yirifi_dq.core.analyzers module
    generators: Any  # yirifi_dq.core.generators module

    # Execution metadata
    operation_id: str
    environment: str  # DEV/UAT/PRD
    test_mode: bool = True
    dry_run: bool = False

    # State management
    state_manager: Any = None  # StateManager instance
    logger: Any = None  # Logger instance for this operation

    # Backup/rollback
    backup_path: Optional[str] = None


@dataclass
class DryRunPreview:
    """
    Result of a dry-run preview showing what would be affected.

    Attributes:
        operation_summary: Brief description of the operation
        total_records: Total records that would be examined
        affected_records_count: Number of records that would be modified/deleted
        affected_groups_count: Number of groups (e.g., duplicate groups)
        sample_records: Sample of records that would be affected (first 5)
        estimated_impact: Human-readable impact summary
        safety_features: List of safety features that would be enabled
        warnings: Any warnings about the operation
    """

    operation_summary: str
    total_records: int
    affected_records_count: int
    affected_groups_count: int = 0
    sample_records: List[Dict[str, Any]] = field(default_factory=list)
    estimated_impact: str = ""
    safety_features: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ScriptResult:
    """
    Standardized return value from every script.

    The framework uses this for state tracking, verification, and reporting.
    All fields are optional except success and message.

    Attributes:
        success: Whether the script executed successfully
        message: Human-readable summary of what happened
        records_processed: Number of records examined
        records_modified: Number of records updated
        records_deleted: Number of records deleted
        records_created: Number of records created
        details: Detailed results (for reporting/debugging)
        errors: List of error messages encountered
        warnings: List of warnings encountered
        verification_checks: Results of verification checks
        dry_run_preview: Preview data if this was a dry run

    Example:
        >>> return ScriptResult(
        ...     success=True,
        ...     message="Cleaned 150 old duplicates, archived 20 orphans",
        ...     records_processed=500,
        ...     records_deleted=150,
        ...     records_modified=20,
        ...     details={
        ...         'duplicates_removed': 150,
        ...         'orphans_archived': 20,
        ...         'cutoff_date': '2024-01-01'
        ...     },
        ...     warnings=['10 records could not be verified'],
        ...     verification_checks={
        ...         'duplicate_check': {'passed': True, 'duplicates_found': 0},
        ...         'orphan_check': {'passed': True, 'orphans_found': 0}
        ...     }
        ... )
    """

    success: bool
    message: str

    # Metrics for verification
    records_processed: int = 0
    records_modified: int = 0
    records_deleted: int = 0
    records_created: int = 0

    # Detailed results (for reporting)
    details: Dict[str, Any] = field(default_factory=dict)

    # Errors/warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Verification data
    verification_checks: Dict[str, Any] = field(default_factory=dict)

    # Dry-run preview data
    dry_run_preview: Optional[DryRunPreview] = None

    # Execution metadata (populated by orchestrator)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class BaseScript(ABC):
    """
    Abstract base class for all custom business logic scripts.

    All scripts must inherit from this class and implement the execute() method.
    Optional methods can be overridden for custom validation and verification.

    Contract:
    - Implement execute() with your business logic
    - Return ScriptResult with success/failure and metrics
    - Use context.validators/fixers/analyzers (don't import directly)
    - Log to context.logger (framework handles state.db persistence)
    - Raise ScriptExecutionError for recoverable errors
    - Raise ScriptValidationError for parameter validation failures

    Example:
        >>> class CleanOldLinksScript(BaseScript):
        ...     '''Remove duplicate links older than threshold.'''
        ...
        ...     def execute(self, context: ScriptContext) -> ScriptResult:
        ...         # Extract parameters
        ...         age_threshold = context.parameters['age_threshold_days']
        ...         field = context.parameters.get('duplicate_field', 'url')
        ...
        ...         # Use framework utilities via context
        ...         duplicates = context.validators.find_duplicates(
        ...             context.collection,
        ...             field,
        ...             return_details=True
        ...         )
        ...
        ...         # Filter old duplicates (custom business logic)
        ...         cutoff_date = datetime.utcnow() - timedelta(days=age_threshold)
        ...         old_duplicates = [
        ...             d for d in duplicates
        ...             if d.get('created_at', datetime.min) < cutoff_date
        ...         ]
        ...
        ...         # Remove duplicates
        ...         if old_duplicates:
        ...             result = context.fixers.remove_duplicates(
        ...                 collection=context.collection,
        ...                 field=field,
        ...                 keep_strategy='oldest',
        ...                 test_mode=context.test_mode
        ...             )
        ...             deleted_count = result['deleted_count']
        ...         else:
        ...             deleted_count = 0
        ...
        ...         return ScriptResult(
        ...             success=True,
        ...             message=f"Removed {deleted_count} old duplicates",
        ...             records_processed=len(duplicates),
        ...             records_deleted=deleted_count,
        ...             details={
        ...                 'cutoff_date': cutoff_date.isoformat(),
        ...                 'total_duplicates': len(duplicates),
        ...                 'old_duplicates': len(old_duplicates)
        ...             }
        ...         )
    """

    @abstractmethod
    def execute(self, context: ScriptContext) -> ScriptResult:
        """
        Execute business logic.

        This is the main entry point for your script. Implement your
        business logic here using the utilities provided in context.

        Args:
            context: Pre-initialized dependencies and parameters

        Returns:
            ScriptResult with success/failure and metrics

        Raises:
            ScriptExecutionError: For recoverable errors (triggers rollback)
            ScriptValidationError: For parameter validation failures

        Example:
            >>> def execute(self, context: ScriptContext) -> ScriptResult:
            ...     # Your business logic here
            ...     result = context.fixers.remove_duplicates(...)
            ...
            ...     return ScriptResult(
            ...         success=True,
            ...         message="Operation completed",
            ...         records_deleted=result['deleted_count']
            ...     )
        """
        pass

    def validate_parameters(self, context: ScriptContext) -> List[str]:
        """
        Optional: Custom parameter validation beyond YAML schema.

        Override this method if you need business logic validation
        beyond type checking (e.g., "start_date must be before end_date").

        Args:
            context: Script context with parameters

        Returns:
            List of error messages (empty if valid)

        Example:
            >>> def validate_parameters(self, context: ScriptContext) -> List[str]:
            ...     errors = []
            ...     start = context.parameters.get('start_date')
            ...     end = context.parameters.get('end_date')
            ...
            ...     if start and end and start > end:
            ...         errors.append("start_date must be before end_date")
            ...
            ...     return errors
        """
        return []

    def pre_execute_checks(self, context: ScriptContext) -> bool:
        """
        Optional: Pre-flight checks before execution.

        Override this method for runtime environment checks
        (e.g., "collection must have at least 100 records").

        Args:
            context: Script context with initialized database/collection

        Returns:
            True if safe to proceed, False otherwise

        Example:
            >>> def pre_execute_checks(self, context: ScriptContext) -> bool:
            ...     # Check collection is not empty
            ...     count = context.collection.count_documents({})
            ...     if count == 0:
            ...         context.logger.warning("Collection is empty, skipping")
            ...         return False
            ...
            ...     return True
        """
        return True

    def post_execute_verification(
        self, context: ScriptContext, result: ScriptResult
    ) -> Dict[str, Any]:
        """
        Optional: Custom verification logic after execution.

        Override this method for business-specific verification checks
        beyond the automatic checks (count, duplicates, orphans).

        Args:
            context: Script context
            result: Result from execute()

        Returns:
            Dict of verification results (passed/failed checks)

        Example:
            >>> def post_execute_verification(self, context, result):
            ...     # Verify no records with negative values
            ...     negative_count = context.collection.count_documents({
            ...         'amount': {'$lt': 0}
            ...     })
            ...
            ...     return {
            ...         'negative_amount_check': {
            ...             'passed': negative_count == 0,
            ...             'negative_found': negative_count
            ...         }
            ...     }
        """
        return {}

    def get_affected_records_filter(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional: Return MongoDB filter for backup of affected records only.

        Override this method to optimize backups by only backing up
        records that will be modified, rather than the entire collection.

        Called by framework before backup if safety.backup_filter == 'affected_records'.

        Args:
            parameters: User-provided parameters

        Returns:
            MongoDB filter query for affected records

        Example:
            >>> def get_affected_records_filter(self, parameters):
            ...     age_threshold = parameters['age_threshold_days']
            ...     cutoff_date = datetime.utcnow() - timedelta(days=age_threshold)
            ...
            ...     return {
            ...         'created_at': {'$lt': cutoff_date},
            ...         'status': 'inactive'
            ...     }
        """
        return {}  # Default: no filter (backup all)

    def dry_run_preview(self, context: ScriptContext) -> DryRunPreview:
        """
        Optional: Generate preview of what would be affected by this operation.

        Override this method to provide a custom dry-run preview.
        Default implementation provides basic collection count.

        Args:
            context: Script context with database and parameters

        Returns:
            DryRunPreview with preview information

        Example:
            >>> def dry_run_preview(self, context: ScriptContext) -> DryRunPreview:
            ...     # Find duplicates
            ...     duplicates = context.validators.find_duplicates(
            ...         context.collection,
            ...         context.parameters['field'],
            ...         return_details=True
            ...     )
            ...
            ...     # Count affected records
            ...     affected_count = sum(len(g['documents']) - 1 for g in duplicates)
            ...
            ...     # Get sample records
            ...     samples = []
            ...     for group in duplicates[:5]:
            ...         samples.append({
            ...             'value': group['value'],
            ...             'count': len(group['documents'])
            ...         })
            ...
            ...     return DryRunPreview(
            ...         operation_summary=f"Remove duplicate {context.parameters['field']}",
            ...         total_records=context.collection.count_documents({}),
            ...         affected_records_count=affected_count,
            ...         affected_groups_count=len(duplicates),
            ...         sample_records=samples,
            ...         estimated_impact=f"{affected_count} duplicates would be deleted, {len(duplicates)} unique values would remain",
            ...         safety_features=['Backup enabled', 'Test mode: ON' if context.test_mode else 'Test mode: OFF'],
            ...         warnings=[] if affected_count > 0 else ['No duplicates found']
            ...     )
        """
        # Default implementation: basic collection count
        total_count = context.collection.count_documents({})

        return DryRunPreview(
            operation_summary="Custom operation",
            total_records=total_count,
            affected_records_count=0,
            affected_groups_count=0,
            sample_records=[],
            estimated_impact="No preview available - script does not implement dry_run_preview()",
            safety_features=[
                "Backup enabled",
                f"Test mode: {'ON' if context.test_mode else 'OFF'}",
                "Verification enabled",
            ],
            warnings=["This script does not provide dry-run preview details"],
        )
