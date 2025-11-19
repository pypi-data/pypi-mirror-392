"""
Custom exceptions for the plugin system.

These exceptions provide clear error handling for script execution,
validation, and loading failures.
"""


class ScriptExecutionError(Exception):
    """
    Raised when a script execution fails.

    This is a recoverable error - the orchestrator will:
    - Mark operation as failed
    - Offer rollback if backup exists
    - Log detailed error information

    Example:
        >>> if not validation_passed:
        ...     raise ScriptExecutionError("Data validation failed: missing required field 'email'")
    """

    pass


class ScriptValidationError(Exception):
    """
    Raised when script parameter validation fails.

    This prevents execution from starting - the orchestrator will:
    - Not create operation record
    - Not acquire locks
    - Show validation errors to user

    Example:
        >>> if age < 0:
        ...     raise ScriptValidationError("Parameter 'age' must be positive")
    """

    pass


class ScriptLoadError(Exception):
    """
    Raised when a script cannot be loaded or instantiated.

    Common causes:
    - Script file not found
    - Script class not found in module
    - Script class doesn't inherit from BaseScript
    - Import errors in script module

    Example:
        >>> raise ScriptLoadError(f"Script class {class_name} not found in {script_path}")
    """

    pass


class ScriptConfigError(Exception):
    """
    Raised when script YAML configuration is invalid.

    Common causes:
    - YAML syntax errors
    - Missing required fields
    - Invalid parameter types
    - Schema validation failures

    Example:
        >>> raise ScriptConfigError(f"Invalid YAML in {yaml_file}: {validation_error}")
    """

    pass
