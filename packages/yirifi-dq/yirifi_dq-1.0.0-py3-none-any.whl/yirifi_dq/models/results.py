"""
Standardized result models for validators, fixers, and analyzers.

These Pydantic models provide type safety and consistent result formats
without the overhead of base class inheritance. They replace the deleted
BaseValidator, BaseFixer, and BaseAnalyzer classes with a simpler,
functional approach.

Author: Data Quality Framework
Last Updated: 2025-11-17
"""

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """
    Standardized result from a validation operation.

    Replaces the BaseValidator return format with a simple Pydantic model
    that can be used with functional validators.

    Example:
        >>> from yirifi_dq.models.results import ValidationResult
        >>>
        >>> def find_duplicates(collection, field) -> ValidationResult:
        ...     duplicates = list(collection.aggregate(...))
        ...     return ValidationResult(
        ...         validator_name="find_duplicates",
        ...         collection_name=collection.name,
        ...         database_name=collection.database.name,
        ...         issues_found=len(duplicates),
        ...         issue_details=duplicates
        ...     )
    """

    validator_name: str = Field(..., description="Name of the validator function")

    collection_name: str = Field(..., description="Name of the collection validated")

    database_name: str = Field(..., description="Name of the database")

    issues_found: int = Field(default=0, description="Number of issues/problems found")

    issue_details: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed information about each issue")

    execution_time_seconds: float = Field(default=0.0, description="Time taken to execute validation")

    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics and analysis")

    timestamp: datetime = Field(default_factory=datetime.now, description="When the validation was performed")

    class Config:
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}


class FixerResult(BaseModel):
    """
    Standardized result from a fixer operation.

    Replaces the BaseFixer return format with a simple Pydantic model
    that can be used with functional fixers.

    Example:
        >>> from yirifi_dq.models.results import FixerResult
        >>>
        >>> def remove_duplicates(collection, field) -> FixerResult:
        ...     # Perform deletion
        ...     result = collection.delete_many(...)
        ...
        ...     return FixerResult(
        ...         fixer_name="remove_duplicates",
        ...         collection_name=collection.name,
        ...         database_name=collection.database.name,
        ...         records_affected=result.deleted_count,
        ...         backup_file="/path/to/backup.json"
        ...     )
    """

    fixer_name: str = Field(..., description="Name of the fixer function")

    collection_name: str = Field(..., description="Name of the collection fixed")

    database_name: str = Field(..., description="Name of the database")

    records_affected: int = Field(default=0, description="Number of records modified/deleted")

    records_deleted: int = Field(default=0, description="Number of records deleted")

    records_updated: int = Field(default=0, description="Number of records updated")

    records_inserted: int = Field(default=0, description="Number of records inserted")

    backup_file: Optional[str] = Field(default=None, description="Path to backup file created before operation")

    execution_time_seconds: float = Field(default=0.0, description="Time taken to execute fix")

    test_mode: bool = Field(default=False, description="Whether operation was run in test mode")

    dry_run: bool = Field(default=False, description="Whether this was a dry run (no changes made)")

    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the fix")

    timestamp: datetime = Field(default_factory=datetime.now, description="When the fix was performed")

    class Config:
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}


class AnalyzerResult(BaseModel):
    """
    Standardized result from an analyzer operation.

    Replaces the BaseAnalyzer return format with a simple Pydantic model
    that can be used with functional analyzers.

    Example:
        >>> from yirifi_dq.models.results import AnalyzerResult
        >>>
        >>> def analyze_field_coverage(collection, field) -> AnalyzerResult:
        ...     total = collection.count_documents({})
        ...     with_field = collection.count_documents({field: {"$exists": True}})
        ...
        ...     return AnalyzerResult(
        ...         analyzer_name="analyze_field_coverage",
        ...         collection_name=collection.name,
        ...         database_name=collection.database.name,
        ...         insights={
        ...             "total_documents": total,
        ...             "documents_with_field": with_field,
        ...             "coverage_percent": (with_field / total * 100) if total > 0 else 0
        ...         }
        ...     )
    """

    analyzer_name: str = Field(..., description="Name of the analyzer function")

    collection_name: str = Field(..., description="Name of the collection analyzed")

    database_name: str = Field(..., description="Name of the database")

    insights: Dict[str, Any] = Field(default_factory=dict, description="Analysis insights and findings")

    recommendations: List[str] = Field(default_factory=list, description="Recommended actions based on analysis")

    execution_time_seconds: float = Field(default=0.0, description="Time taken to execute analysis")

    timestamp: datetime = Field(default_factory=datetime.now, description="When the analysis was performed")

    class Config:
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}


class OperationSummary(BaseModel):
    """
    High-level summary of any operation (validation, fix, or analysis).

    Useful for reporting and logging across different operation types.
    """

    operation_type: str = Field(..., description="Type of operation (validator, fixer, analyzer)")

    operation_name: str = Field(..., description="Name of the operation")

    collection_name: str = Field(..., description="Collection operated on")

    database_name: str = Field(..., description="Database name")

    success: bool = Field(default=True, description="Whether operation completed successfully")

    records_affected: int = Field(default=0, description="Total records affected")

    execution_time_seconds: float = Field(default=0.0, description="Execution time")

    error_message: Optional[str] = Field(default=None, description="Error message if operation failed")

    timestamp: datetime = Field(default_factory=datetime.now, description="When operation was performed")

    class Config:
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}
