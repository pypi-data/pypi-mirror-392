"""
Pydantic models for data quality operations.

These models provide type-safe configuration and validation for all operation types.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar

import yaml
from pydantic import BaseModel, Field, validator

T = TypeVar("T", bound="BaseModel")


class OperationType(str, Enum):
    """Types of data quality operations."""

    DUPLICATE_CLEANUP = "duplicate-cleanup"
    ORPHAN_CLEANUP = "orphan-cleanup"
    DATA_NORMALIZATION = "data-normalization"
    FIELD_MIGRATION = "field-migration"
    SLUG_GENERATION = "slug-generation"
    CUSTOM = "custom"


class OperationStatus(str, Enum):
    """Operation execution status."""

    PLANNING = "planning"
    READY = "ready"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Environment(str, Enum):
    """MongoDB environments."""

    PRD = "PRD"
    DEV = "DEV"
    UAT = "UAT"


class KeepStrategy(str, Enum):
    """Strategy for which duplicate record to keep."""

    OLDEST = "oldest"
    NEWEST = "newest"
    MOST_COMPLETE = "most_complete"
    MATCH_FOREIGN_KEY = "match_foreign_key"


class OperationConfig(BaseModel):
    """Base configuration for all operations."""

    operation_type: OperationType
    database: str
    collection: str
    field: Optional[str] = None
    environment: Environment = Environment.DEV
    test_mode: bool = True
    test_limit: int = 10
    auto_backup: bool = True
    auto_verify: bool = True

    class Config:
        use_enum_values = True

    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """
        Export model to YAML format.

        Args:
            file_path: Optional path to save YAML file

        Returns:
            YAML string representation
        """
        data = self.model_dump(mode="json")
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        return yaml_str

    @classmethod
    def from_yaml(cls: Type[T], source: Any) -> T:
        """
        Load model from YAML source.

        Args:
            source: YAML string, file path, or dict

        Returns:
            Model instance

        Raises:
            ValueError: If YAML is invalid
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.exists():
                # It's a file path
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                # It's a YAML string
                data = yaml.safe_load(str(source))
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f"Invalid YAML source type: {type(source)}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML must contain a dictionary, got {type(data).__name__}")

        return cls(**data)


class DuplicateCleanupConfig(OperationConfig):
    """Configuration for duplicate cleanup operations."""

    operation_type: Literal[OperationType.DUPLICATE_CLEANUP] = OperationType.DUPLICATE_CLEANUP
    field: str  # Required for duplicate cleanup
    keep_strategy: KeepStrategy = KeepStrategy.OLDEST
    check_foreign_keys: bool = True
    foreign_key_collections: Optional[List[str]] = None

    class Config:
        use_enum_values = True


class OrphanCleanupConfig(OperationConfig):
    """Configuration for orphan cleanup operations."""

    operation_type: Literal[OperationType.ORPHAN_CLEANUP] = OperationType.ORPHAN_CLEANUP
    foreign_key_field: str  # Field that contains foreign key
    parent_collection: str  # Collection to check for parent records
    parent_key_field: str = "_id"  # Field in parent collection (usually _id or unique key)
    delete_orphans: bool = True  # If False, just report

    class Config:
        use_enum_values = True


class DataNormalizationConfig(OperationConfig):
    """Configuration for data normalization operations."""

    operation_type: Literal[OperationType.DATA_NORMALIZATION] = OperationType.DATA_NORMALIZATION
    field: str  # Required
    normalization_type: Literal["url", "text", "case", "whitespace", "custom"]
    custom_normalizer: Optional[str] = None  # Python function name if custom

    class Config:
        use_enum_values = True


class FieldMigrationConfig(OperationConfig):
    """Configuration for field migration operations."""

    operation_type: Literal[OperationType.FIELD_MIGRATION] = OperationType.FIELD_MIGRATION
    source_field: str
    target_field: str
    transformation: Optional[str] = None  # Python function name for transformation
    delete_source: bool = False

    class Config:
        use_enum_values = True


class SlugGenerationConfig(OperationConfig):
    """Configuration for slug generation operations."""

    operation_type: Literal[OperationType.SLUG_GENERATION] = OperationType.SLUG_GENERATION
    field: Optional[str] = None  # Not required - uses slug_fields.yaml config
    fix_missing: bool = True
    fix_duplicates: bool = True
    limit: Optional[int] = None
    max_workers: int = 10

    class Config:
        use_enum_values = True


class CustomOperationConfig(OperationConfig):
    """Configuration for custom operations."""

    operation_type: Literal[OperationType.CUSTOM] = OperationType.CUSTOM
    script_path: str  # Path to Python script
    script_args: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class OperationResult(BaseModel):
    """Results from an operation execution."""

    operation_id: str
    status: OperationStatus
    records_affected: int = 0
    records_deleted: int = 0
    records_updated: int = 0
    records_inserted: int = 0
    backup_file: Optional[str] = None
    report_file: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        use_enum_values = True

    @validator("duration_seconds", always=True)
    def calculate_duration(cls, v, values):
        """Auto-calculate duration if not provided."""
        if v is None and "completed_at" in values and values["completed_at"]:
            started = values.get("started_at")
            completed = values["completed_at"]
            if started and completed:
                return (completed - started).total_seconds()
        return v

    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export model to YAML format."""
        data = self.model_dump(mode="json")
        # Convert datetime to ISO format for YAML
        if isinstance(data.get("started_at"), datetime):
            data["started_at"] = data["started_at"].isoformat()
        if isinstance(data.get("completed_at"), datetime):
            data["completed_at"] = data["completed_at"].isoformat()

        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        return yaml_str

    @classmethod
    def from_yaml(cls: Type[T], source: Any) -> T:
        """Load model from YAML source."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                data = yaml.safe_load(str(source))
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f"Invalid YAML source type: {type(source)}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML must contain a dictionary, got {type(data).__name__}")

        return cls(**data)


class DuplicateCleanupResult(BaseModel):
    """Results from duplicate cleanup operation."""

    records_affected: int = 0
    records_deleted: int = 0
    duplicates_found: int = 0
    duplicate_groups: int = 0
    backup_file: Optional[str] = None
    field: str
    keep_strategy: str = "oldest"

    class Config:
        use_enum_values = True


class OrphanCleanupResult(BaseModel):
    """Results from orphan cleanup operation."""

    records_affected: int = 0
    records_deleted: int = 0
    orphans_found: int = 0
    backup_file: Optional[str] = None
    foreign_key_field: str
    parent_collection: str

    class Config:
        use_enum_values = True


class RollbackResult(BaseModel):
    """Results from rollback operation."""

    success: bool
    restored_count: int = 0
    total_documents: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    restored_ids: List[str] = Field(default_factory=list)
    aborted: bool = False
    message: Optional[str] = None

    class Config:
        use_enum_values = True


class BackupResult(BaseModel):
    """Results from backup operation."""

    success: bool
    backup_file: Optional[str] = None
    documents_backed_up: int = 0
    backup_size_bytes: Optional[int] = None
    error_message: Optional[str] = None

    class Config:
        use_enum_values = True


class VerificationResult(BaseModel):
    """Results from operation verification."""

    operation_id: str
    passed: bool
    checks_performed: List[str]
    checks_passed: List[str]
    checks_failed: List[str]
    details: Dict[str, Any] = Field(default_factory=dict)
    verified_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export model to YAML format."""
        data = self.model_dump(mode="json")
        if isinstance(data.get("verified_at"), datetime):
            data["verified_at"] = data["verified_at"].isoformat()

        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        return yaml_str

    @classmethod
    def from_yaml(cls: Type[T], source: Any) -> T:
        """Load model from YAML source."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                data = yaml.safe_load(str(source))
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f"Invalid YAML source type: {type(source)}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML must contain a dictionary, got {type(data).__name__}")

        return cls(**data)


class OperationMetadata(BaseModel):
    """Metadata for an operation (stored in state DB and INDEX.yaml)."""

    operation_id: str
    operation_name: str
    operation_type: OperationType
    database: str
    collection: str
    field: Optional[str] = None
    environment: Environment
    status: OperationStatus
    test_mode: bool

    # Paths
    operation_folder: str
    backup_file: Optional[str] = None
    report_file: Optional[str] = None
    script_file: Optional[str] = None

    # Results
    records_affected: int = 0
    records_deleted: int = 0
    records_updated: int = 0
    records_inserted: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Additional
    created_by: str = "cli"
    error_message: Optional[str] = None
    learnings: Optional[List[str]] = None
    next_actions: Optional[List[str]] = None

    class Config:
        use_enum_values = True

    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export model to YAML format."""
        data = self.model_dump(mode="json")
        # Convert datetime fields to ISO format for YAML
        for field in ["created_at", "started_at", "completed_at"]:
            if isinstance(data.get(field), datetime):
                data[field] = data[field].isoformat()

        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        return yaml_str

    @classmethod
    def from_yaml(cls: Type[T], source: Any) -> T:
        """Load model from YAML source."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                data = yaml.safe_load(str(source))
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f"Invalid YAML source type: {type(source)}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML must contain a dictionary, got {type(data).__name__}")

        return cls(**data)
