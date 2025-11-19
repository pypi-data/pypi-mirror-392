"""
Pydantic models for script configuration YAML files.

These models provide type-safe validation of YAML configs and
enable IDE autocomplete for script configuration.

Example YAML that matches these models:
    id: links/clean-old-duplicates
    name: "Clean Old Duplicate Links"
    domain: links
    script_type: custom
    script_path: "yirifi_dq/scripts/links/clean_old_duplicates.py"
    script_class: "CleanOldDuplicatesScript"

    parameters:
      - name: age_threshold_days
        type: integer
        required: true
        default: 90
        min: 1
        max: 365
        help: "Only process duplicates older than this many days"
        cli_flag: "--age-threshold-days"
        tui_widget: "integer_input"
        tui_order: 1

    safety:
      requires_backup: true
      requires_verification: true
      supports_test_mode: true
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ScriptParameter(BaseModel):
    """
    Definition of a single parameter for a script.

    Parameters are defined in YAML and used to:
    - Generate CLI flags (--age-threshold-days)
    - Generate TUI form widgets (integer input, dropdown, etc.)
    - Validate user input (type, range, enum values)
    - Provide help text and defaults

    Attributes:
        name: Parameter name (snake_case, used in Python)
        type: Data type (integer, string, boolean, list, dict, enum)
        required: Whether parameter is mandatory
        default: Default value if not provided
        min: Minimum value (for integer/float)
        max: Maximum value (for integer/float)
        enum: List of allowed values (for enum type)
        help: Help text shown to user
        example: Example value (especially useful for dict/list JSON parameters)
        cli_flag: CLI flag name (e.g., "--age-threshold-days")
        tui_widget: TUI widget type (integer_input, dropdown, etc.)
        tui_order: Display order in TUI form (lower = first)

    Example:
        >>> param = ScriptParameter(
        ...     name="age_threshold_days",
        ...     type="integer",
        ...     required=True,
        ...     default=90,
        ...     min=1,
        ...     max=365,
        ...     help="Only process duplicates older than this many days",
        ...     cli_flag="--age-threshold-days",
        ...     tui_widget="integer_input",
        ...     tui_order=1
        ... )
    """

    name: str = Field(..., description="Parameter name (snake_case)")
    type: str = Field(
        ...,
        description="Data type",
        pattern="^(integer|string|boolean|float|list|dict|enum)$",
    )
    required: bool = Field(default=False, description="Whether parameter is mandatory")
    default: Optional[Any] = Field(None, description="Default value if not provided")

    # Validation constraints
    min: Optional[float] = Field(None, description="Minimum value (for numeric types)")
    max: Optional[float] = Field(None, description="Maximum value (for numeric types)")
    enum: Optional[List[Any]] = Field(None, description="Allowed values (for enum type)")

    # UI metadata
    help: str = Field(default="", description="Help text shown to user")
    example: Optional[str] = Field(None, description="Example value (especially for dict/list JSON)")
    cli_flag: str = Field(..., description="CLI flag name (e.g., '--age-threshold-days')")
    tui_widget: str = Field(
        default="text_input",
        description="TUI widget type",
        pattern="^(integer_input|text_input|checkbox|dropdown|multiselect)$",
    )
    tui_order: int = Field(default=999, description="Display order in TUI (lower = first)")

    @field_validator("cli_flag")
    @classmethod
    def validate_cli_flag(cls, v: str) -> str:
        """Validate CLI flag format."""
        if not v.startswith("--"):
            raise ValueError("cli_flag must start with '--'")
        if " " in v:
            raise ValueError("cli_flag cannot contain spaces")
        return v

    @field_validator("enum")
    @classmethod
    def validate_enum_with_type(cls, v: Optional[List[Any]], info) -> Optional[List[Any]]:
        """Validate that enum is provided when type is 'enum'."""
        if info.data.get("type") == "enum" and not v:
            raise ValueError("enum values required when type is 'enum'")
        return v


class SafetyConfig(BaseModel):
    """
    Safety configuration for a script.

    Controls backup, verification, and testing behavior.

    Attributes:
        requires_backup: Whether backup is mandatory before execution
        backup_filter: What to backup ('all', 'affected_records', 'none')
        requires_verification: Whether verification is mandatory after execution
        verification_type: Type of verification ('automatic', 'manual', 'both')
        locks_collection: Whether to acquire collection lock during execution
        lock_timeout_minutes: How long to wait for lock before failing
        supports_test_mode: Whether script can run in test mode (limited records)
        default_test_limit: Default number of records in test mode
        warn_if_count_exceeds: Show warning if record count exceeds this
        confirm_if_deleting: Require confirmation if script deletes records

    Example:
        >>> safety = SafetyConfig(
        ...     requires_backup=True,
        ...     backup_filter="affected_records",
        ...     requires_verification=True,
        ...     verification_type="automatic",
        ...     supports_test_mode=True,
        ...     default_test_limit=10
        ... )
    """

    requires_backup: bool = Field(
        default=True, description="Whether backup is mandatory before execution"
    )
    backup_filter: str = Field(
        default="all",
        description="What to backup",
        pattern="^(all|affected_records|none)$",
    )
    requires_verification: bool = Field(
        default=True, description="Whether verification is mandatory after execution"
    )
    verification_type: str = Field(
        default="automatic",
        description="Type of verification",
        pattern="^(automatic|manual|both)$",
    )

    locks_collection: bool = Field(
        default=True, description="Whether to acquire collection lock"
    )
    lock_timeout_minutes: int = Field(
        default=30, description="Lock timeout in minutes", ge=1, le=120
    )

    supports_test_mode: bool = Field(
        default=True, description="Whether script supports test mode"
    )
    default_test_limit: int = Field(
        default=10, description="Default test mode record limit", ge=1, le=1000
    )

    warn_if_count_exceeds: Optional[int] = Field(
        None, description="Show warning if record count exceeds this"
    )
    confirm_if_deleting: bool = Field(
        default=True, description="Require confirmation for delete operations"
    )


class VerificationCheck(BaseModel):
    """
    Definition of an automatic verification check.

    Verification checks run after script execution to ensure
    data integrity and operation success.

    Attributes:
        type: Check type (count_check, orphan_check, duplicate_check, custom,
              data_integrity_check, referential_integrity_check, schema_validation_check)
        description: Human-readable description of what's checked
        config: Configuration dict for the verification check (type-specific)

        Legacy fields (backward compatibility):
        field: Field to check (for duplicate_check)
        foreign_collection: Foreign collection name (for orphan_check)
        foreign_field: Foreign key field (for orphan_check)
        primary_field: Primary key field (for orphan_check)
        expected: Expected condition (for count_check)
        custom_check: Custom Python code (for custom type)

    Example - Legacy duplicate_check:
        >>> check = VerificationCheck(
        ...     type="duplicate_check",
        ...     description="Verify no duplicates remain for URL field",
        ...     field="url"
        ... )

    Example - New data_integrity_check:
        >>> check = VerificationCheck(
        ...     type="data_integrity_check",
        ...     description="Verify URL and title constraints",
        ...     config={
        ...         "field_constraints": {
        ...             "url": {"not_null": True, "unique": True, "regex": r"^https?://.*"},
        ...             "title": {"not_null": True, "min_length": 5, "max_length": 500}
        ...         }
        ...     }
        ... )

    Example - New referential_integrity_check:
        >>> check = VerificationCheck(
        ...     type="referential_integrity_check",
        ...     description="Verify articles -> links relationship",
        ...     config={
        ...         "foreign_collection": "links",
        ...         "primary_field": "articleYid",
        ...         "foreign_field": "link_yid",
        ...         "check_both_directions": True
        ...     }
        ... )

    Example - New schema_validation_check:
        >>> check = VerificationCheck(
        ...     type="schema_validation_check",
        ...     description="Verify document schema compliance",
        ...     config={
        ...         "required_fields": ["url", "title", "link_yid", "created_at"],
        ...         "optional_fields": ["description", "tags", "metadata"],
        ...         "strict_mode": False
        ...     }
        ... )
    """

    type: str = Field(
        ...,
        description="Check type",
        pattern="^(count_check|orphan_check|duplicate_check|custom|data_integrity_check|referential_integrity_check|schema_validation_check)$",
    )
    description: str = Field(..., description="Description of what's checked")

    # NEW: Unified config dict (preferred for new verification types)
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration dict for the verification check (type-specific)"
    )

    # LEGACY: Optional fields for backward compatibility with existing checks
    field: Optional[str] = Field(None, description="Field to check (for duplicate_check)")
    foreign_collection: Optional[str] = Field(
        None, description="Foreign collection name (for orphan_check)"
    )
    foreign_field: Optional[str] = Field(
        None, description="Foreign key field (for orphan_check)"
    )
    primary_field: Optional[str] = Field(
        None, description="Primary key field (for orphan_check)"
    )
    expected: Optional[str] = Field(None, description="Expected condition (for count_check)")
    custom_check: Optional[str] = Field(
        None, description="Custom Python code (for custom type)"
    )


class ScriptExample(BaseModel):
    """
    Example usage of a script.

    Examples are shown in help text and documentation.

    Attributes:
        description: Description of what this example does
        cli: CLI command example
        parameters: Parameter values for this example

    Example:
        >>> example = ScriptExample(
        ...     description="Clean duplicates older than 90 days (test mode)",
        ...     cli="yirifi-dq run links/clean-old-duplicates --age-threshold-days 90 --test-mode"
        ... )
    """

    description: str = Field(..., description="Description of what this example does")
    cli: Optional[str] = Field(None, description="CLI command example")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter values")


class ScriptConfig(BaseModel):
    """
    Complete configuration for a business logic script.

    This is the root model that validates an entire YAML config file.

    Attributes:
        id: Unique script ID (domain/name format, e.g., "links/clean-old-duplicates")
        version: Semantic version (e.g., "1.0.0")
        name: Human-readable name
        description: Detailed description of what the script does
        domain: Domain category (links, articles, pipeline, cross_domain, maintenance, framework)
        category: Category ID from categories.yaml (e.g., data_quality, relationships, pipeline_management)
        tags: Searchable tags
        script_type: Type of script ('custom' or 'built-in')
        script_path: Path to Python script file (relative to package root)
        script_class: Name of script class in Python file
        operation: Built-in operation name (if script_type is 'built-in')
        parameters: List of script parameters
        safety: Safety configuration
        verification: Verification checks
        examples: Usage examples
        documentation: Links to additional documentation

    Example:
        >>> config = ScriptConfig(
        ...     id="links/clean-old-duplicates",
        ...     name="Clean Old Duplicate Links",
        ...     description="Remove duplicate links older than threshold",
        ...     domain="links",
        ...     script_type="custom",
        ...     script_path="yirifi_dq/scripts/links/clean_old_duplicates.py",
        ...     script_class="CleanOldDuplicatesScript",
        ...     parameters=[...],
        ...     safety=SafetyConfig(...),
        ...     verification=[...]
        ... )
    """

    # Metadata
    id: str = Field(
        ...,
        description="Unique script ID (domain/name)",
        pattern="^[a-z0-9_]+/[a-z0-9_-]+$",
    )
    version: str = Field(
        default="1.0.0", description="Semantic version", pattern=r"^\d+\.\d+\.\d+$"
    )
    name: str = Field(..., description="Human-readable name", min_length=5, max_length=100)
    description: str = Field(default="", description="Detailed description")

    # Categorization
    domain: str = Field(
        ...,
        description="Domain category",
        pattern="^(links|articles|pipeline|cross_domain|maintenance|framework)$",
    )
    category: Optional[str] = Field(
        None,
        description="Category ID from categories.yaml (e.g., data_quality, relationships, pipeline_management)",
    )
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

    # Script location
    script_type: str = Field(
        ..., description="Type of script", pattern="^(custom|built-in)$"
    )
    script_path: Optional[str] = Field(
        None, description="Path to Python script (required if script_type=custom)"
    )
    script_class: str = Field(default="Script", description="Name of script class")
    operation: Optional[str] = Field(
        None, description="Built-in operation name (required if script_type=built-in)"
    )

    # Configuration
    parameters: List[ScriptParameter] = Field(
        default_factory=list, description="Script parameters"
    )
    safety: SafetyConfig = Field(default_factory=SafetyConfig, description="Safety config")
    verification: List[VerificationCheck] = Field(
        default_factory=list, description="Verification checks"
    )
    examples: List[ScriptExample] = Field(default_factory=list, description="Usage examples")

    # Documentation
    documentation: Dict[str, Any] = Field(
        default_factory=dict, description="Links to additional documentation"
    )

    @field_validator("script_path")
    @classmethod
    def validate_script_path_for_custom(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that script_path is provided when script_type is 'custom'."""
        if info.data.get("script_type") == "custom" and not v:
            raise ValueError("script_path required when script_type is 'custom'")
        return v

    @field_validator("operation")
    @classmethod
    def validate_operation_for_builtin(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that operation is provided when script_type is 'built-in'."""
        if info.data.get("script_type") == "built-in" and not v:
            raise ValueError("operation required when script_type is 'built-in'")
        return v

    @property
    def cli_command_name(self) -> str:
        """Convert ID to CLI-friendly command name."""
        return self.id.replace("_", "-")

    @property
    def script_module_path(self) -> str:
        """Convert script_path to Python module import path."""
        if not self.script_path:
            return ""
        # yirifi_dq/scripts/links/clean_old_duplicates.py -> yirifi_dq.scripts.links.clean_old_duplicates
        return self.script_path.replace("/", ".").replace(".py", "")


class BuiltInOperationConfig(BaseModel):
    """
    Configuration for a built-in operation (no custom Python code).

    Built-in operations map directly to core framework functions
    (e.g., duplicate-cleanup, orphan-cleanup) without requiring
    custom Python scripts.

    Attributes:
        operation: Core operation name (duplicate-cleanup, orphan-cleanup, etc.)
        parameters: Parameters to pass to the operation
        safety: Safety configuration
        verification: Verification checks

    Example:
        >>> config = BuiltInOperationConfig(
        ...     operation="duplicate-cleanup",
        ...     parameters={
        ...         'field': 'url',
        ...         'keep_strategy': 'oldest'
        ...     }
        ... )
    """

    operation: str = Field(..., description="Core operation name")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters to pass to operation"
    )
    safety: SafetyConfig = Field(default_factory=SafetyConfig, description="Safety config")
    verification: List[VerificationCheck] = Field(
        default_factory=list, description="Verification checks"
    )
