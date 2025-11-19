"""
Built-in Operation Wrapper - Adapter for core framework operations.

This module provides a wrapper that adapts core framework operations
(duplicate-cleanup, orphan-cleanup, etc.) to the BaseScript interface.

This allows built-in operations to be used through the same script system
as custom scripts, without requiring Python code for simple operations.

Example YAML for built-in operation:
    id: links/simple-duplicate-cleanup
    name: "Simple Duplicate Cleanup"
    domain: links
    script_type: built-in  # No Python file needed!
    operation: duplicate-cleanup

    parameters:
      - name: field
        type: string
        required: true
      - name: keep_strategy
        type: enum
        enum: [oldest, newest, most_complete]
"""

from typing import Dict, Any, List

from yirifi_dq.plugins.base_script import BaseScript, ScriptContext, ScriptResult
from yirifi_dq.plugins.exceptions import ScriptExecutionError
from yirifi_dq.plugins.models import ScriptConfig


class BuiltInOperationWrapper(BaseScript):
    """
    Wrapper that adapts core operations to BaseScript interface.

    Supported operations:
    - duplicate-cleanup: Remove duplicates using core.fixers.remove_duplicates
    - orphan-cleanup: Clean orphans using core.fixers.clean_orphans
    - field-update: Bulk field updates using core.fixers.reset_pipeline_fields
    - slug-generation: Generate slugs using core.generators.SlugGenerator

    Attributes:
        operation: Operation name (e.g., 'duplicate-cleanup')
        config: Script configuration

    Example:
        >>> wrapper = BuiltInOperationWrapper('duplicate-cleanup', config)
        >>> result = wrapper.execute(context)
    """

    def __init__(self, operation: str, config: ScriptConfig):
        """
        Initialize wrapper with operation name.

        Args:
            operation: Built-in operation name
            config: Script configuration
        """
        self.operation = operation
        self.config = config

    def validate_parameters(self, context: ScriptContext) -> List[str]:
        """
        Validate parameters based on YAML config.

        Validates:
        - Required parameters are present
        - Enum values match allowed list
        - Integer/float values are within min/max ranges
        - Boolean values are actual booleans

        Args:
            context: Script context with parameters

        Returns:
            List of validation error messages (empty if valid)

        Example:
            >>> errors = wrapper.validate_parameters(context)
            >>> if errors:
            ...     print(f"Validation failed: {errors}")
        """
        errors = []

        # Loop through all parameter definitions in the YAML config
        for param_def in self.config.parameters:
            param_name = param_def.name
            param_value = context.parameters.get(param_name)

            # Check required parameters
            if param_def.required and param_value is None:
                errors.append(f"Required parameter '{param_name}' is missing")
                continue  # Skip further validation if missing

            # Skip remaining validation if parameter is not provided (and not required)
            if param_value is None:
                continue

            # Validate enum values
            if param_def.type == "enum" and param_def.enum:
                if param_value not in param_def.enum:
                    errors.append(
                        f"Parameter '{param_name}' must be one of {param_def.enum}, "
                        f"got '{param_value}'"
                    )

            # Validate integer ranges
            if param_def.type == "integer":
                if not isinstance(param_value, int):
                    errors.append(
                        f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__}"
                    )
                else:
                    if param_def.min is not None and param_value < param_def.min:
                        errors.append(
                            f"Parameter '{param_name}' must be >= {param_def.min}, got {param_value}"
                        )
                    if param_def.max is not None and param_value > param_def.max:
                        errors.append(
                            f"Parameter '{param_name}' must be <= {param_def.max}, got {param_value}"
                        )

            # Validate float ranges
            if param_def.type == "float":
                if not isinstance(param_value, (int, float)):
                    errors.append(
                        f"Parameter '{param_name}' must be a number, got {type(param_value).__name__}"
                    )
                else:
                    if param_def.min is not None and param_value < param_def.min:
                        errors.append(
                            f"Parameter '{param_name}' must be >= {param_def.min}, got {param_value}"
                        )
                    if param_def.max is not None and param_value > param_def.max:
                        errors.append(
                            f"Parameter '{param_name}' must be <= {param_def.max}, got {param_value}"
                        )

            # Validate boolean type
            if param_def.type == "boolean":
                if not isinstance(param_value, bool):
                    errors.append(
                        f"Parameter '{param_name}' must be a boolean (true/false), "
                        f"got {type(param_value).__name__}"
                    )

        return errors

    def execute(self, context: ScriptContext) -> ScriptResult:
        """
        Execute built-in operation.

        Routes to appropriate core framework function based on operation name.

        Args:
            context: Script context with parameters and database handles

        Returns:
            ScriptResult with operation outcome

        Raises:
            ScriptExecutionError: If operation fails or is unknown
        """
        # Route to appropriate operation
        if self.operation == "duplicate-cleanup":
            return self._execute_duplicate_cleanup(context)

        elif self.operation == "orphan-cleanup":
            return self._execute_orphan_cleanup(context)

        elif self.operation == "field-update":
            return self._execute_field_update(context)

        elif self.operation == "slug-generation":
            return self._execute_slug_generation(context)

        else:
            raise ScriptExecutionError(
                f"Unknown built-in operation: {self.operation}\n"
                f"Supported operations: duplicate-cleanup, orphan-cleanup, "
                f"field-update, slug-generation"
            )

    def _execute_duplicate_cleanup(self, context: ScriptContext) -> ScriptResult:
        """Execute duplicate cleanup operation."""
        # Extract parameters
        field = context.parameters.get("field")
        if not field:
            raise ScriptExecutionError("Parameter 'field' is required for duplicate-cleanup")

        keep_strategy = context.parameters.get("keep_strategy", "oldest")

        # Call core fixer
        try:
            result = context.fixers.remove_duplicates(
                collection=context.collection,
                field=field,
                keep_strategy=keep_strategy,
                test_mode=context.test_mode,
                auto_backup=True,  # Backup handled by framework
            )

            return ScriptResult(
                success=True,
                message=f"Removed {result.get('deleted_count', 0)} duplicate records",
                records_processed=result.get('total_found', 0),
                records_deleted=result.get('deleted_count', 0),
                details={
                    "field": field,
                    "keep_strategy": keep_strategy,
                    "duplicates_found": result.get('total_found', 0),
                    "deleted_count": result.get('deleted_count', 0),
                },
            )

        except Exception as e:
            raise ScriptExecutionError(f"Duplicate cleanup failed: {e}")

    def _execute_orphan_cleanup(self, context: ScriptContext) -> ScriptResult:
        """Execute orphan cleanup operation."""
        # Extract parameters
        foreign_collection_name = context.parameters.get("foreign_collection")
        if not foreign_collection_name:
            raise ScriptExecutionError(
                "Parameter 'foreign_collection' is required for orphan-cleanup"
            )

        primary_field = context.parameters.get("primary_field", "link_yid")
        foreign_field = context.parameters.get("foreign_field", "articleYid")
        action = context.parameters.get("action", "delete")  # delete or reassign

        # Get foreign collection
        foreign_collection = context.database[foreign_collection_name]

        # Call core fixer
        try:
            if action == "delete":
                result = context.fixers.clean_orphans(
                    source_collection=foreign_collection,
                    target_collection=context.collection,
                    source_field=foreign_field,
                    target_field=primary_field,
                    test_mode=context.test_mode,
                    auto_backup=True,
                )
            else:  # reassign
                result = context.fixers.reassign_orphans(
                    source_collection=foreign_collection,
                    target_collection=context.collection,
                    source_field=foreign_field,
                    target_field=primary_field,
                    test_mode=context.test_mode,
                )

            return ScriptResult(
                success=True,
                message=f"Cleaned {result.get('deleted_count', 0)} orphaned records",
                records_processed=result.get('orphans_found', 0),
                records_deleted=result.get('deleted_count', 0) if action == "delete" else 0,
                records_modified=result.get('reassigned_count', 0) if action == "reassign" else 0,
                details={
                    "foreign_collection": foreign_collection_name,
                    "primary_field": primary_field,
                    "foreign_field": foreign_field,
                    "action": action,
                    "orphans_found": result.get('orphans_found', 0),
                },
            )

        except Exception as e:
            raise ScriptExecutionError(f"Orphan cleanup failed: {e}")

    def _execute_field_update(self, context: ScriptContext) -> ScriptResult:
        """Execute field update operation."""
        # Extract parameters
        field_updates = context.parameters.get("field_updates")
        if not field_updates:
            raise ScriptExecutionError("Parameter 'field_updates' is required for field-update")

        input_method = context.parameters.get("input_method", "query")
        query_filter = context.parameters.get("query_filter", {})

        # Call core fixer
        try:
            operation_config = {
                "field_updates": field_updates,
                "id_field": context.parameters.get("id_field", "_id"),
            }

            input_data = {"query_filter": query_filter}

            result = context.fixers.reset_pipeline_fields(
                collection=context.collection,
                operation_config=operation_config,
                input_method=input_method,
                input_data=input_data,
                env=context.environment,
                test_mode=context.test_mode,
                auto_backup=True,
            )

            return ScriptResult(
                success=True,
                message=f"Updated {result.get('updated_count', 0)} records",
                records_processed=result.get('matched_count', 0),
                records_modified=result.get('updated_count', 0),
                details={
                    "field_updates": field_updates,
                    "matched_count": result.get('matched_count', 0),
                    "updated_count": result.get('updated_count', 0),
                },
            )

        except Exception as e:
            raise ScriptExecutionError(f"Field update failed: {e}")

    def _execute_slug_generation(self, context: ScriptContext) -> ScriptResult:
        """Execute slug generation operation."""
        # Extract parameters
        regenerate_existing = context.parameters.get("regenerate_existing", False)
        batch_size = context.parameters.get("batch_size", 100)

        # Call core generator
        try:
            from yirifi_dq.core.generators import SlugGenerator

            generator = SlugGenerator(
                collection=context.collection,
                env=context.environment,
                test_mode=context.test_mode,
            )

            result = generator.generate_slugs(
                regenerate_existing=regenerate_existing, batch_size=batch_size
            )

            return ScriptResult(
                success=True,
                message=f"Generated {result.get('generated_count', 0)} slugs",
                records_processed=result.get('total_processed', 0),
                records_modified=result.get('generated_count', 0),
                details={
                    "regenerate_existing": regenerate_existing,
                    "batch_size": batch_size,
                    "generated_count": result.get('generated_count', 0),
                    "skipped_count": result.get('skipped_count', 0),
                },
            )

        except Exception as e:
            raise ScriptExecutionError(f"Slug generation failed: {e}")
