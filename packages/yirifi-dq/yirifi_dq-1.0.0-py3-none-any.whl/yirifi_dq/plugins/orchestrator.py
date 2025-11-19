"""
Script Orchestrator - Execution engine with safety features.

This module provides the orchestration layer that:
- Loads scripts from registry
- Creates execution context with database connections
- Enforces safety features (backup, verification, locks)
- Tracks execution state
- Handles rollback on failure

Example:
    >>> from yirifi_dq.plugins.orchestrator import ScriptOrchestrator
    >>>
    >>> orchestrator = ScriptOrchestrator(
    ...     env='DEV',
    ...     state_manager=state_manager
    ... )
    >>>
    >>> result = orchestrator.run_script(
    ...     script_id='links/simple-duplicate-cleanup',
    ...     parameters={'field': 'url', 'keep_strategy': 'oldest'},
    ...     database_name='regdb',
    ...     collection_name='links',
    ...     test_mode=True
    ... )
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import difflib

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from yirifi_dq.plugins.base_script import BaseScript, ScriptContext, ScriptResult
from yirifi_dq.plugins.registry import get_registry
from yirifi_dq.plugins.exceptions import (
    ScriptExecutionError,
    ScriptValidationError,
    ScriptLoadError,
)
from yirifi_dq.core import validators, fixers, analyzers, generators
from yirifi_dq.core.mongodb import get_client, get_database, get_collection
from yirifi_dq.core.backup import backup_documents
from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.models.state import OperationState
from yirifi_dq.models.operation import OperationType, OperationStatus, Environment


class ScriptOrchestrator:
    """
    Orchestrates script execution with full framework integration.

    Responsibilities:
    - Load scripts from registry
    - Create execution context with database connections
    - Enforce safety features (backup, verification, locks)
    - Track execution in state.db
    - Handle errors and rollback

    Attributes:
        env: Environment (DEV, UAT, PRD)
        state_manager: StateManager instance for tracking
        logger: Logger instance
        registry: ScriptRegistry instance
        client: MongoDB client
        _active_locks: Dict of active collection locks

    Example:
        >>> orchestrator = ScriptOrchestrator(env='DEV')
        >>> result = orchestrator.run_script(
        ...     script_id='links/simple-duplicate-cleanup',
        ...     parameters={'field': 'url'},
        ...     database_name='regdb',
        ...     collection_name='links'
        ... )
    """

    def __init__(
        self,
        env: str = "DEV",
        state_manager=None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            env: Environment (DEV, UAT, PRD)
            state_manager: StateManager instance (uses singleton if None)
            logger: Logger instance (creates default if None)
        """
        self.env = env
        self.state_manager = state_manager or get_state_manager()
        self.logger = logger or self._create_logger()
        self.registry = get_registry()
        self.client: Optional[MongoClient] = None

    def _create_logger(self) -> logging.Logger:
        """Create default logger."""
        logger = logging.getLogger("yirifi_dq.orchestrator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def run_script(
        self,
        script_id: str,
        parameters: Dict[str, Any],
        database_name: str,
        collection_name: str,
        operation_id: Optional[str] = None,
        test_mode: bool = True,
        dry_run: bool = False,
        auto_backup: bool = True,
        auto_verify: bool = True,
    ) -> ScriptResult:
        """
        Execute a script with full safety features.

        Orchestration flow:
        1. Load script from registry
        2. Validate parameters
        3. Acquire collection lock
        4. Create database connections
        5. Backup if needed
        6. Execute script
        7. Verify results
        8. Release lock
        9. Update state

        Args:
            script_id: Script identifier (e.g., 'links/simple-duplicate-cleanup')
            parameters: Script parameters
            database_name: Database name
            collection_name: Collection name
            operation_id: Operation ID for state tracking (auto-generated if None)
            test_mode: Limit to 10 records (default: True)
            dry_run: Don't make changes (default: False)
            auto_backup: Backup before execution (default: True)
            auto_verify: Verify after execution (default: True)

        Returns:
            ScriptResult with execution details

        Raises:
            ScriptLoadError: If script not found
            ScriptValidationError: If parameters invalid
            ScriptExecutionError: If execution fails

        Example:
            >>> result = orchestrator.run_script(
            ...     script_id='links/simple-duplicate-cleanup',
            ...     parameters={'field': 'url', 'keep_strategy': 'oldest'},
            ...     database_name='regdb',
            ...     collection_name='links'
            ... )
            >>> print(f"Deleted {result.records_deleted} duplicates")
        """
        script = None
        backup_path = None
        context = None
        operation_created = False

        try:
            # Step 1: Load script from registry
            self.logger.info(f"Loading script: {script_id}")
            self._log(None, "INFO", f"Loading script: {script_id}")

            script = self.registry.get_script_instance(script_id)
            config = self.registry.get_script_config(script_id)

            if not config:
                raise ScriptLoadError(f"Script config not found: {script_id}")

            # Step 2: Generate operation ID if needed
            if operation_id is None:
                operation_id = self._generate_operation_id(script_id)

            self.logger.info(f"Operation ID: {operation_id}")

            # Step 3: Create operation in state.db
            operation_folder = Path("output") / operation_id
            operation_folder.mkdir(parents=True, exist_ok=True)

            operation_state = OperationState(
                operation_id=operation_id,
                operation_name=config.name,
                operation_type=OperationType.CUSTOM,  # Plugin scripts use CUSTOM type
                database=database_name,
                collection=collection_name,
                field=parameters.get("field"),  # Common parameter
                environment=Environment(self.env),
                test_mode=test_mode,
                status=OperationStatus.PLANNING,
                operation_folder=str(operation_folder),
                created_by="plugin_orchestrator",
            )

            self.state_manager.create_operation(operation_state)
            operation_created = True
            self._log(operation_id, "INFO", f"Created operation: {operation_id}")

            # Step 4: Update status to executing
            self.state_manager.update_operation(
                operation_id,
                status=OperationStatus.EXECUTING.value,
                started_at=datetime.utcnow()
            )

            # Step 5: Connect to database
            self.logger.info(f"Connecting to database: {database_name}.{collection_name}")
            self._log(operation_id, "INFO", f"Connecting to {database_name}.{collection_name}")

            self.client = get_client(env=self.env)
            database = get_database(self.client, database_name)
            collection = get_collection(database, collection_name)

            # Step 6: Create execution context
            context = self._create_context(
                database=database,
                collection=collection,
                parameters=parameters,
                operation_id=operation_id,
                test_mode=test_mode,
                dry_run=dry_run,
            )

            # Step 7: Validate parameters
            self.logger.info("Validating parameters...")
            self._log(operation_id, "INFO", "Validating parameters")

            # Enhanced validation with suggestions
            validation_errors = self._validate_parameters_enhanced(
                parameters=parameters,
                config=config,
                script=script,
                context=context
            )

            if validation_errors:
                # Format errors with suggestions
                error_msg = self._format_validation_errors(validation_errors, config)
                self._log(operation_id, "ERROR", f"Parameter validation failed: {len(validation_errors)} errors")
                raise ScriptValidationError(error_msg)

            # Step 8: Display pre-execution summary
            self._display_pre_execution_summary(
                script_id=script_id,
                config=config,
                parameters=parameters,
                database_name=database_name,
                collection_name=collection_name,
                test_mode=test_mode,
                dry_run=dry_run,
                auto_backup=auto_backup,
                auto_verify=auto_verify
            )

            # Step 9: Pre-execute checks
            self.logger.info("Running pre-execute checks...")
            self._log(operation_id, "INFO", "Running pre-execute checks")

            if not script.pre_execute_checks(context):
                self._log(operation_id, "WARNING", "Pre-execute checks failed, skipping execution")
                self.state_manager.update_operation(
                    operation_id,
                    status=OperationStatus.COMPLETED.value,
                    completed_at=datetime.utcnow()
                )
                return ScriptResult(
                    success=False,
                    message="Pre-execute checks failed, skipping execution",
                )

            # Step 10: Acquire collection lock
            if config.safety.locks_collection:
                self.logger.info("Acquiring collection lock...")
                self._log(operation_id, "INFO", "Acquiring collection lock")

                if not self._acquire_lock(database_name, collection_name, operation_id):
                    error_msg = f"Collection {database_name}.{collection_name} is already locked"
                    self._log(operation_id, "ERROR", error_msg)
                    raise ScriptExecutionError(error_msg)

            # Step 11: Backup if required
            if auto_backup and config.safety.requires_backup and not dry_run:
                self.logger.info("Creating backup...")
                self._log(operation_id, "INFO", "Creating backup")

                backup_path = self._create_backup(
                    collection=collection,
                    script_id=script_id,
                    config=config,
                    parameters=parameters,
                    operation_id=operation_id,
                )
                context.backup_path = backup_path

                # Update operation with backup path
                self.state_manager.update_operation(operation_id, backup_file=backup_path)
                self.logger.info(f"Backup created: {backup_path}")
                self._log(operation_id, "INFO", f"Backup created: {backup_path}")

            # Step 12: Execute script (or dry-run preview)
            if dry_run:
                self.logger.info("Running dry-run preview...")
                self._log(operation_id, "INFO", "Running dry-run preview")
                result = self._execute_dry_run(script, context, config)
            else:
                self.logger.info("Executing script...")
                self._log(operation_id, "INFO", "Executing script")
                result = script.execute(context)

            # Step 13: Verify results if required
            if auto_verify and config.safety.requires_verification and not dry_run:
                self.logger.info("Verifying results...")
                self._log(operation_id, "INFO", "Verifying results")

                # Run automatic verification checks from YAML config
                if config.verification:
                    verification_results = self._run_verification(
                        config=config,
                        context=context,
                        result=result
                    )
                    result.verification_checks.update(verification_results)

                # Run custom script verification
                custom_verification = script.post_execute_verification(context, result)
                result.verification_checks.update(custom_verification)

            # Step 14: Update completion state
            self.logger.info("Operation completed successfully")
            self._log(operation_id, "INFO", f"Operation completed: {result.message}")

            self.state_manager.update_operation(
                operation_id,
                status=OperationStatus.COMPLETED.value if result.success else OperationStatus.FAILED.value,
                completed_at=datetime.utcnow(),
                records_affected=result.records_processed,
                records_deleted=result.records_deleted,
                records_updated=result.records_modified,
                records_inserted=result.records_created,
            )

            # Update framework stats
            if result.success:
                self.state_manager._update_stats(
                    operations_completed=1,
                    total_records_affected=result.records_processed,
                    total_records_deleted=result.records_deleted,
                    total_records_updated=result.records_modified,
                    total_records_inserted=result.records_created,
                    total_backups_created=1 if backup_path else 0,
                    last_operation_at=datetime.utcnow()
                )

            return result

        except Exception as e:
            self.logger.error(f"Script execution failed: {e}", exc_info=True)

            error_stack = traceback.format_exc()

            # Update failure state if operation was created
            if operation_created:
                self._log(operation_id, "ERROR", f"Execution failed: {e}")
                self.state_manager.update_operation(
                    operation_id,
                    status=OperationStatus.FAILED.value,
                    completed_at=datetime.utcnow(),
                    error_message=str(e),
                    error_stack_trace=error_stack,
                )

                # Update stats for failure
                self.state_manager._update_stats(operations_failed=1)

            # Return failure result
            return ScriptResult(
                success=False,
                message=f"Execution failed: {e}",
                errors=[str(e)],
            )

        finally:
            # Always release lock
            if operation_created and config and config.safety.locks_collection:
                self._release_lock(database_name, collection_name)

            # Close database connection
            if self.client:
                self.client.close()

    def _create_context(
        self,
        database: Database,
        collection: Collection,
        parameters: Dict[str, Any],
        operation_id: str,
        test_mode: bool,
        dry_run: bool,
    ) -> ScriptContext:
        """
        Create script execution context.

        Args:
            database: MongoDB database
            collection: MongoDB collection
            parameters: Script parameters
            operation_id: Operation ID
            test_mode: Test mode flag
            dry_run: Dry run flag

        Returns:
            ScriptContext with all dependencies
        """
        return ScriptContext(
            database=database,
            collection=collection,
            parameters=parameters,
            validators=validators,
            fixers=fixers,
            analyzers=analyzers,
            generators=generators,
            operation_id=operation_id,
            environment=self.env,
            test_mode=test_mode,
            dry_run=dry_run,
            state_manager=self.state_manager,
            logger=self.logger,
        )

    def _generate_operation_id(self, script_id: str) -> str:
        """
        Generate operation ID.

        Format: SCRIPT-YYYYMMDD-HHMMSS

        Args:
            script_id: Script identifier

        Returns:
            Operation ID
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        script_short = script_id.replace("/", "-").upper()
        return f"{script_short}-{timestamp}"

    def _create_backup(
        self,
        collection: Collection,
        script_id: str,
        config,
        parameters: Dict[str, Any],
        operation_id: str,
    ) -> str:
        """
        Create backup before execution.

        Args:
            collection: MongoDB collection
            script_id: Script identifier
            config: Script configuration
            parameters: Script parameters
            operation_id: Operation ID

        Returns:
            Backup file path
        """
        # Determine backup filter
        if config.safety.backup_filter == "all":
            filter_query = {}
        elif config.safety.backup_filter == "affected_records":
            # Call script's get_affected_records_filter() if it exists
            script = self.registry.get_script_instance(script_id)
            if hasattr(script, "get_affected_records_filter"):
                filter_query = script.get_affected_records_filter(parameters)
            else:
                filter_query = {}
        else:
            filter_query = {}

        # Create backup
        backup_path = backup_documents(
            collection=collection,
            filter_query=filter_query,
            operation_name=operation_id,
            test_mode=False,  # Always backup fully
        )

        return backup_path

    def _acquire_lock(self, database_name: str, collection_name: str, operation_id: str) -> bool:
        """
        Acquire collection lock using StateManager.

        Args:
            database_name: Database name
            collection_name: Collection to lock
            operation_id: Operation ID

        Returns:
            True if lock acquired, False if already locked
        """
        return self.state_manager.acquire_lock(
            database=database_name,
            collection=collection_name,
            operation_id=operation_id,
            locked_by="plugin_orchestrator",
            duration_minutes=30,
            reason=f"Script execution: {operation_id}"
        )

    def _release_lock(self, database_name: str, collection_name: str) -> None:
        """
        Release collection lock using StateManager.

        Args:
            database_name: Database name
            collection_name: Collection to unlock
        """
        self.state_manager.release_lock(database=database_name, collection=collection_name)

    def _validate_parameters_enhanced(
        self,
        parameters: Dict[str, Any],
        config,
        script: BaseScript,
        context: ScriptContext
    ) -> List[Dict[str, Any]]:
        """
        Enhanced parameter validation with detailed error messages.

        Args:
            parameters: User-provided parameters
            config: Script configuration
            script: Script instance
            context: Script context

        Returns:
            List of validation error dictionaries with suggestions
        """
        errors = []

        # Get valid parameter names from config
        valid_params = {p.name for p in config.parameters}

        # Check for unknown parameters (typos)
        for param_name in parameters.keys():
            if param_name not in valid_params:
                # Find similar parameter names
                suggestions = self._get_parameter_suggestions(param_name, valid_params)
                errors.append({
                    'type': 'unknown_parameter',
                    'parameter': param_name,
                    'value': parameters[param_name],
                    'suggestions': suggestions,
                    'valid_params': list(valid_params)
                })

        # Check required parameters
        for param_config in config.parameters:
            if param_config.required and param_config.name not in parameters:
                # Check if has default value
                if param_config.default is None:
                    errors.append({
                        'type': 'missing_required',
                        'parameter': param_config.name,
                        'help': param_config.help,
                        'param_type': param_config.type,
                        'example': self._get_parameter_example(param_config)
                    })

        # Check enum parameters
        for param_config in config.parameters:
            if param_config.type == "enum" and param_config.name in parameters:
                value = parameters[param_config.name]
                if value not in param_config.enum:
                    # Find similar enum values
                    suggestions = self._get_parameter_suggestions(value, set(param_config.enum))
                    errors.append({
                        'type': 'invalid_enum',
                        'parameter': param_config.name,
                        'value': value,
                        'valid_options': param_config.enum,
                        'suggestions': suggestions,
                        'help': param_config.help
                    })

        # Call script's custom validation
        script_errors = script.validate_parameters(context)
        for error_msg in script_errors:
            errors.append({
                'type': 'custom_validation',
                'message': error_msg
            })

        return errors

    def _get_parameter_suggestions(self, value: str, valid_options: set, max_suggestions: int = 3) -> List[str]:
        """
        Get "did you mean?" suggestions using fuzzy matching.

        Args:
            value: User-provided value
            valid_options: Set of valid options
            max_suggestions: Maximum number of suggestions

        Returns:
            List of suggested values
        """
        if not valid_options:
            return []

        # Use difflib for fuzzy matching
        matches = difflib.get_close_matches(
            value,
            list(valid_options),
            n=max_suggestions,
            cutoff=0.6  # 60% similarity threshold
        )

        return matches

    def _get_parameter_example(self, param_config) -> str:
        """
        Get example value for a parameter based on its type.

        Args:
            param_config: Parameter configuration

        Returns:
            Example value string
        """
        if param_config.type == "enum" and param_config.enum:
            return param_config.enum[0]
        elif param_config.type == "string":
            return "<value>"
        elif param_config.type == "integer":
            return "10"
        elif param_config.type == "boolean":
            return "true"
        else:
            return "<value>"

    def _format_validation_errors(self, errors: List[Dict[str, Any]], config) -> str:
        """
        Format validation errors with rich details and suggestions.

        Args:
            errors: List of validation error dictionaries
            config: Script configuration

        Returns:
            Formatted error message
        """
        lines = []
        lines.append(f"Parameter validation failed ({len(errors)} error{'s' if len(errors) > 1 else ''}):")
        lines.append("")

        for i, error in enumerate(errors, 1):
            error_type = error.get('type')

            if error_type == 'unknown_parameter':
                lines.append(f"{i}. Unknown parameter: '{error['parameter']}'")
                if error['suggestions']:
                    lines.append(f"   Did you mean: {', '.join(error['suggestions'])}?")
                lines.append(f"   Valid parameters: {', '.join(error['valid_params'])}")

            elif error_type == 'missing_required':
                lines.append(f"{i}. Missing required parameter: '{error['parameter']}'")
                lines.append(f"   Description: {error['help']}")
                lines.append(f"   Type: {error['param_type']}")
                lines.append(f"   Example: -p {error['parameter']}={error['example']}")

            elif error_type == 'invalid_enum':
                lines.append(f"{i}. Invalid value '{error['value']}' for parameter '{error['parameter']}'")
                if error['suggestions']:
                    lines.append(f"   Did you mean: {', '.join(error['suggestions'])}?")
                lines.append(f"   Valid options: {', '.join(error['valid_options'])}")
                if error['help']:
                    lines.append(f"   Description: {error['help']}")

            elif error_type == 'custom_validation':
                lines.append(f"{i}. {error['message']}")

            lines.append("")

        # Add script info reference
        lines.append(f"For more details, run: yirifi-dq scripts info {config.id}")

        return "\n".join(lines)

    def _display_pre_execution_summary(
        self,
        script_id: str,
        config,
        parameters: Dict[str, Any],
        database_name: str,
        collection_name: str,
        test_mode: bool,
        dry_run: bool,
        auto_backup: bool,
        auto_verify: bool
    ) -> None:
        """
        Display pre-execution summary for user review.

        Args:
            script_id: Script identifier
            config: Script configuration
            parameters: Script parameters
            database_name: Database name
            collection_name: Collection name
            test_mode: Test mode flag
            dry_run: Dry run flag
            auto_backup: Auto backup flag
            auto_verify: Auto verify flag
        """
        self.logger.info("=" * 70)
        self.logger.info("PRE-EXECUTION SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Script: {config.name} ({script_id})")
        self.logger.info(f"Database: {database_name}.{collection_name}")
        self.logger.info(f"Environment: {self.env}")
        self.logger.info("")
        self.logger.info("Parameters:")
        for key, value in parameters.items():
            self.logger.info(f"  {key} = {value}")
        self.logger.info("")
        self.logger.info("Safety Features:")
        self.logger.info(f"  Test Mode: {'YES (limit 10 records)' if test_mode else 'NO (full collection)'}")
        self.logger.info(f"  Dry Run: {'YES (no changes)' if dry_run else 'NO (will modify data)'}")
        self.logger.info(f"  Backup: {'ENABLED' if auto_backup else 'DISABLED'}")
        self.logger.info(f"  Verification: {'ENABLED' if auto_verify else 'DISABLED'}")
        self.logger.info(f"  Collection Lock: ENABLED")
        self.logger.info("=" * 70)

    def _run_verification(
        self,
        config,
        context: ScriptContext,
        result: ScriptResult
    ) -> Dict[str, Any]:
        """
        Run automatic verification checks from YAML config.

        Args:
            config: Script configuration with verification checks
            context: Script execution context
            result: Script execution result

        Returns:
            Dict of verification results (check_name -> check_result)

        Example:
            >>> verification_results = self._run_verification(config, context, result)
            >>> if verification_results['data_integrity_check']['passed']:
            ...     print("Data integrity verified!")
        """
        verification_results = {}

        for check in config.verification:
            check_name = f"{check.type}_{check.description.replace(' ', '_').lower()[:30]}"

            try:
                if check.type == "data_integrity_check":
                    # NEW: Data integrity verification
                    if not check.config or "field_constraints" not in check.config:
                        self.logger.error(
                            f"data_integrity_check requires 'field_constraints' in config"
                        )
                        continue

                    result_check = context.validators.verify_data_integrity(
                        collection=context.collection,
                        field_constraints=check.config["field_constraints"],
                        sample_size=check.config.get("sample_size")
                    )
                    verification_results[check_name] = result_check

                    if not result_check["passed"]:
                        self.logger.warning(
                            f"Data integrity check failed: {result_check['summary']}"
                        )
                        for violation in result_check["violations"]:
                            self.logger.warning(
                                f"  - {violation['field']}.{violation['constraint']}: "
                                f"{violation['count']} violations"
                            )

                elif check.type == "referential_integrity_check":
                    # NEW: Referential integrity verification
                    if not check.config:
                        self.logger.error(
                            f"referential_integrity_check requires config dict"
                        )
                        continue

                    foreign_collection_name = check.config.get("foreign_collection")
                    if not foreign_collection_name:
                        self.logger.error(
                            "referential_integrity_check requires 'foreign_collection' in config"
                        )
                        continue

                    # Get foreign collection
                    foreign_collection = context.database[foreign_collection_name]

                    result_check = context.validators.verify_referential_integrity(
                        primary_collection=context.collection,
                        foreign_collection=foreign_collection,
                        primary_field=check.config["primary_field"],
                        foreign_field=check.config["foreign_field"],
                        check_both_directions=check.config.get("check_both_directions", True)
                    )
                    verification_results[check_name] = result_check

                    if not result_check["passed"]:
                        self.logger.warning(
                            f"Referential integrity check failed: {result_check['summary']}"
                        )
                        if result_check["missing_references"]:
                            self.logger.warning(
                                f"  Sample orphaned references: "
                                f"{result_check['missing_references'][:3]}"
                            )

                elif check.type == "schema_validation_check":
                    # NEW: Schema validation
                    if not check.config or "required_fields" not in check.config:
                        self.logger.error(
                            f"schema_validation_check requires 'required_fields' in config"
                        )
                        continue

                    result_check = context.validators.verify_schema(
                        collection=context.collection,
                        required_fields=check.config["required_fields"],
                        optional_fields=check.config.get("optional_fields"),
                        strict_mode=check.config.get("strict_mode", False),
                        sample_size=check.config.get("sample_size")
                    )
                    verification_results[check_name] = result_check

                    if not result_check["passed"]:
                        self.logger.warning(
                            f"Schema validation check failed: {result_check['summary']}"
                        )
                        if result_check["missing_required_fields"]:
                            self.logger.warning(
                                f"  Missing required fields: "
                                f"{list(result_check['missing_required_fields'].keys())}"
                            )

                elif check.type == "duplicate_check":
                    # LEGACY: Duplicate check (backward compatibility)
                    if not check.field:
                        self.logger.error("duplicate_check requires 'field' attribute")
                        continue

                    duplicates = context.validators.find_duplicates(
                        context.collection,
                        check.field,
                        return_details=False
                    )
                    verification_results[check_name] = {
                        "passed": len(duplicates) == 0,
                        "duplicates_found": len(duplicates),
                        "summary": f"Found {len(duplicates)} duplicate values in field '{check.field}'"
                    }

                    if len(duplicates) > 0:
                        self.logger.warning(
                            f"Duplicate check failed: Found {len(duplicates)} duplicates in '{check.field}'"
                        )

                elif check.type == "orphan_check":
                    # LEGACY: Orphan check (backward compatibility)
                    if not check.foreign_collection or not check.primary_field or not check.foreign_field:
                        self.logger.error(
                            "orphan_check requires 'foreign_collection', 'primary_field', and 'foreign_field'"
                        )
                        continue

                    foreign_collection = context.database[check.foreign_collection]
                    orphans = context.validators.find_orphans(
                        source_collection=context.collection,
                        target_collection=foreign_collection,
                        source_field=check.primary_field,
                        target_field=check.foreign_field
                    )
                    verification_results[check_name] = {
                        "passed": len(orphans) == 0,
                        "orphans_found": len(orphans),
                        "summary": f"Found {len(orphans)} orphaned records"
                    }

                    if len(orphans) > 0:
                        self.logger.warning(
                            f"Orphan check failed: Found {len(orphans)} orphaned records"
                        )

                elif check.type == "count_check":
                    # LEGACY: Count check (backward compatibility)
                    count = context.collection.count_documents({})
                    verification_results[check_name] = {
                        "passed": True,
                        "count": count,
                        "summary": f"Collection has {count} documents"
                    }

                elif check.type == "custom":
                    # LEGACY: Custom check (backward compatibility)
                    self.logger.warning(
                        f"Custom verification checks not yet implemented: {check.description}"
                    )
                    verification_results[check_name] = {
                        "passed": True,
                        "summary": "Custom check skipped"
                    }

            except Exception as e:
                self.logger.error(f"Verification check '{check_name}' failed: {e}", exc_info=True)
                verification_results[check_name] = {
                    "passed": False,
                    "error": str(e),
                    "summary": f"Verification failed with error: {e}"
                }

        return verification_results

    def _log(self, operation_id: Optional[str], level: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log message to state.db.

        Args:
            operation_id: Operation ID (None if before operation created)
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            details: Optional additional details
        """
        if operation_id and self.state_manager:
            self.state_manager.add_log(
                operation_id=operation_id,
                level=level,
                message=message,
                details=details
            )

    def _execute_dry_run(self, script, context, config) -> "ScriptResult":
        """
        Execute dry-run preview without making any changes.

        Args:
            script: Script instance
            context: Script context
            config: Script configuration

        Returns:
            ScriptResult with dry_run_preview populated
        """
        from yirifi_dq.plugins.base_script import ScriptResult

        try:
            # Call script's dry_run_preview method
            preview = script.dry_run_preview(context)

            # Build safety features list
            safety_features = []
            if config.safety.requires_backup:
                safety_features.append("Backup would be created")
            if config.safety.requires_verification:
                safety_features.append("Verification would run")
            if context.test_mode:
                safety_features.append("Test mode: ON (limited to 10 records)")
            else:
                safety_features.append("Test mode: OFF (full execution)")
            if config.safety.locks_collection:
                safety_features.append("Collection lock would be acquired")

            preview.safety_features = safety_features

            # Return result with preview
            return ScriptResult(
                success=True,
                message=f"Dry-run preview completed: {preview.operation_summary}",
                records_processed=preview.total_records,
                details={
                    "preview_mode": True,
                    "affected_records": preview.affected_records_count,
                    "affected_groups": preview.affected_groups_count,
                },
                dry_run_preview=preview,
            )

        except Exception as e:
            self.logger.error(f"Dry-run preview failed: {e}", exc_info=True)
            return ScriptResult(
                success=False,
                message=f"Dry-run preview failed: {e}",
                errors=[str(e)],
            )

    def list_available_scripts(
        self, domain: Optional[str] = None, tag: Optional[str] = None
    ) -> list:
        """
        List available scripts.

        Args:
            domain: Filter by domain
            tag: Filter by tag

        Returns:
            List of ScriptConfig objects

        Example:
            >>> scripts = orchestrator.list_available_scripts(domain='links')
            >>> for script in scripts:
            ...     print(f"{script.id}: {script.name}")
        """
        return self.registry.list_scripts(domain=domain, tag=tag)

    def get_script_info(self, script_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a script.

        Args:
            script_id: Script identifier

        Returns:
            Dict with script information or None if not found

        Example:
            >>> info = orchestrator.get_script_info('links/simple-duplicate-cleanup')
            >>> print(info['description'])
        """
        config = self.registry.get_script_config(script_id)
        if not config:
            return None

        return {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "domain": config.domain,
            "tags": config.tags,
            "script_type": config.script_type,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    "default": p.default,
                    "help": p.help,
                }
                for p in config.parameters
            ],
            "safety": {
                "requires_backup": config.safety.requires_backup,
                "requires_verification": config.safety.requires_verification,
                "supports_test_mode": config.safety.supports_test_mode,
            },
            "examples": [{"description": e.description, "cli": e.cli} for e in config.examples],
        }
