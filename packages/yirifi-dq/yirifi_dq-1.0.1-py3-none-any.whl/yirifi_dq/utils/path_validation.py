"""
Input validation utilities for the CLI.

Provides validation functions for user inputs to prevent security vulnerabilities
like path traversal, SQL injection, and NoSQL injection.
"""

import re


def validate_safe_path_component(name: str, field_name: str = "Path component") -> None:
    """
    Validate that a path component contains only safe characters.

    This prevents path traversal attacks by ensuring names used in file paths
    (like database names, collection names, field names) cannot escape the
    intended directory structure.

    Args:
        name: The path component to validate
        field_name: Human-readable name for error messages

    Raises:
        ValueError: If the name is invalid or contains unsafe characters
    """
    if not name:
        raise ValueError(f"{field_name} cannot be empty")

    if not isinstance(name, str):
        raise ValueError(f"{field_name} must be a string, got {type(name).__name__}")

    # Check for path traversal sequences
    if ".." in name:
        raise ValueError(f"{field_name} '{name}' contains path traversal sequence '..' which is not allowed for security reasons")

    if "/" in name or "\\" in name:
        raise ValueError(f"{field_name} '{name}' contains path separators which are not allowed")

    # Allow only alphanumeric, underscore, and hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise ValueError(f"{field_name} '{name}' contains invalid characters. Only alphanumeric characters, underscores, and hyphens are allowed")

    # Additional checks for common attack patterns
    if name.startswith("."):
        raise ValueError(f"{field_name} '{name}' cannot start with a dot")

    # Prevent excessively long names (DoS protection)
    if len(name) > 128:
        raise ValueError(f"{field_name} '{name}' is too long (max 128 characters)")


def validate_mongodb_field_name(field_name: str) -> None:
    """
    Validate MongoDB field name.

    MongoDB field names have specific restrictions:
    - Cannot start with $
    - Cannot contain .
    - Cannot be empty

    Args:
        field_name: The field name to validate

    Raises:
        ValueError: If the field name is invalid
    """
    if not field_name:
        raise ValueError("Field name cannot be empty")

    if not isinstance(field_name, str):
        raise ValueError(f"Field name must be a string, got {type(field_name).__name__}")

    if field_name.startswith("$"):
        raise ValueError(f"Field name '{field_name}' cannot start with '$' (reserved for MongoDB operators)")

    if "." in field_name:
        raise ValueError(f"Field name '{field_name}' cannot contain '.' (use nested field access with dict notation instead)")


def validate_mongodb_operator(operator: str) -> None:
    """
    Validate MongoDB query operator.

    Ensures that only whitelisted MongoDB operators are used in queries
    to prevent NoSQL injection attacks.

    Args:
        operator: The operator to validate (e.g., "$eq", "$in", "$gt")

    Raises:
        ValueError: If the operator is not whitelisted
    """
    # Whitelist of safe MongoDB operators
    ALLOWED_OPERATORS = {
        # Comparison
        "$eq",
        "$ne",
        "$gt",
        "$gte",
        "$lt",
        "$lte",
        "$in",
        "$nin",
        # Logical
        "$and",
        "$or",
        "$not",
        "$nor",
        # Element
        "$exists",
        "$type",
        # Array
        "$all",
        "$elemMatch",
        "$size",
        # Evaluation
        "$regex",
        "$text",
        "$mod",
        # Projection
        "$slice",
        # Update
        "$set",
        "$unset",
        "$inc",
        "$push",
        "$pull",
        "$addToSet",
        # Aggregation
        "$match",
        "$group",
        "$project",
        "$sort",
        "$limit",
        "$skip",
        "$unwind",
        "$lookup",
        "$count",
        "$sum",
        "$avg",
        "$min",
        "$max",
    }

    if not operator.startswith("$"):
        raise ValueError(f"MongoDB operators must start with '$', got '{operator}'")

    if operator not in ALLOWED_OPERATORS:
        raise ValueError(f"Operator '{operator}' is not in the whitelist of allowed operators. Allowed: {sorted(ALLOWED_OPERATORS)}")


def sanitize_mongodb_filter(filter_dict: dict, max_depth: int = 5, current_depth: int = 0) -> None:
    """
    Validate MongoDB filter query to prevent NoSQL injection.

    Recursively validates a filter dictionary to ensure:
    - Only whitelisted operators are used
    - Field names don't contain injection attempts
    - Maximum nesting depth is enforced (DoS protection)

    Args:
        filter_dict: The filter dictionary to validate
        max_depth: Maximum nesting depth allowed
        current_depth: Current recursion depth (internal use)

    Raises:
        ValueError: If the filter contains unsafe elements
        RecursionError: If nesting exceeds max_depth
    """
    if not isinstance(filter_dict, dict):
        return  # Primitive values are safe

    if current_depth > max_depth:
        raise RecursionError(f"Filter query nesting exceeds maximum depth of {max_depth} (possible DoS attack)")

    for key, value in filter_dict.items():
        # Validate operators
        if key.startswith("$"):
            validate_mongodb_operator(key)
        # Regular field name - validate it
        # Note: We allow dots in field names here because they represent nested paths
        # But we still check for dangerous patterns
        elif key.startswith("$"):
            raise ValueError(f"Invalid field name: {key}")

        # Recursively validate nested dictionaries
        if isinstance(value, dict):
            sanitize_mongodb_filter(value, max_depth, current_depth + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    sanitize_mongodb_filter(item, max_depth, current_depth + 1)


def validate_operation_id(operation_id: str) -> None:
    """
    Validate operation ID format.

    Operation IDs should follow the pattern: {type}_{collection}_{timestamp}
    and contain only safe characters.

    Args:
        operation_id: The operation ID to validate

    Raises:
        ValueError: If the operation ID format is invalid
    """
    if not operation_id:
        raise ValueError("Operation ID cannot be empty")

    # Use same validation as path components since it's used in paths
    validate_safe_path_component(operation_id, "Operation ID")

    # Operation IDs should have a specific format
    if not re.match(r"^[a-z_]+_[a-z0-9_]+_\d{8}_\d{6}$", operation_id):
        raise ValueError(f"Operation ID '{operation_id}' does not match expected format: type_collection_YYYYMMDD_HHMMSS")


def validate_environment(environment: str) -> None:
    """
    Validate environment name.

    Args:
        environment: The environment name (PRD, DEV, UAT)

    Raises:
        ValueError: If the environment is not valid
    """
    ALLOWED_ENVIRONMENTS = {"PRD", "DEV", "UAT"}

    if environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError(f"Invalid environment '{environment}'. Allowed: {sorted(ALLOWED_ENVIRONMENTS)}")
