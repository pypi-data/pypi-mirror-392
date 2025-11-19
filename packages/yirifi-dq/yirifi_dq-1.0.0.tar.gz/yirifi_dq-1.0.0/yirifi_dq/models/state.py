"""
Pydantic models for operation state management.

These models define the structure of data stored in the SQLite state database.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from yirifi_dq.models.operation import Environment, OperationStatus, OperationType


class OperationState(BaseModel):
    """
    Operation state stored in SQLite database.

    This tracks the current state of all operations for quick querying and filtering.
    """

    # Primary key
    operation_id: str

    # Operation details
    operation_name: str
    operation_type: OperationType
    database: str
    collection: str
    field: Optional[str] = None
    environment: Environment
    test_mode: bool

    # Status tracking
    status: OperationStatus
    current_step: Optional[str] = None
    progress_percent: int = 0

    # Paths
    operation_folder: str
    backup_file: Optional[str] = None
    report_file: Optional[str] = None
    script_file: Optional[str] = None
    config_file: Optional[str] = None

    # Results
    records_affected: int = 0
    records_deleted: int = 0
    records_updated: int = 0
    records_inserted: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Lock management (for concurrent operations)
    locked: bool = False
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None

    # Error tracking
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None

    # User info
    created_by: str = "cli"
    updated_by: Optional[str] = None

    # INDEX.json migration fields (added 2025-11-16)
    summary: Optional[str] = None
    tags: Optional[str] = None  # JSON array as string
    learnings: Optional[str] = None  # JSON array as string
    execution_details: Optional[str] = None  # JSON object as string
    related_collections: Optional[str] = None  # JSON array as string
    next_actions: Optional[str] = None  # JSON array as string

    class Config:
        use_enum_values = True


class OperationLog(BaseModel):
    """
    Log entry for operation execution.

    Stores detailed logs for debugging and audit trails.
    """

    log_id: Optional[int] = None  # Auto-increment in SQLite
    operation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    details: Optional[str] = None  # JSON string for complex data

    class Config:
        use_enum_values = True


class OperationLock(BaseModel):
    """
    Lock for preventing concurrent execution of operations.

    Ensures that operations on the same collection don't run simultaneously.
    """

    lock_id: str  # e.g., "regdb.links"
    operation_id: str
    locked_by: str
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    reason: Optional[str] = None

    class Config:
        use_enum_values = True


class FrameworkStats(BaseModel):
    """
    Cached framework statistics.

    Updated after each operation for fast stats retrieval.
    """

    stat_id: int = 1  # Single row
    total_operations: int = 0
    operations_completed: int = 0
    operations_failed: int = 0
    operations_rolled_back: int = 0
    total_records_affected: int = 0
    total_records_deleted: int = 0
    total_records_updated: int = 0
    total_records_inserted: int = 0
    total_backups_created: int = 0
    last_operation_at: Optional[datetime] = None
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
