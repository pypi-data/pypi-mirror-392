"""
SQLite state manager for operation tracking.

This module handles all interactions with the SQLite state database,
providing methods for CRUD operations on operation state, logs, locks, and statistics.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

from yirifi_dq.models.operation import OperationStatus
from yirifi_dq.models.state import FrameworkStats, OperationLog, OperationState


class StateManager:
    """Manages operation state in SQLite database."""

    # Whitelist of allowed field names for update_operation (prevents SQL injection)
    ALLOWED_OPERATION_UPDATE_FIELDS: ClassVar[set] = {
        "status",
        "current_step",
        "progress_percent",
        "backup_file",
        "report_file",
        "script_file",
        "config_file",
        "records_affected",
        "records_deleted",
        "records_updated",
        "records_inserted",
        "started_at",
        "completed_at",
        "last_updated_at",
        "locked",
        "locked_by",
        "locked_at",
        "error_message",
        "error_stack_trace",
        "updated_by",
        # INDEX.json migration fields (added 2025-11-16)
        "summary",
        "tags",
        "learnings",
        "execution_details",
        "related_collections",
        "next_actions",
    }

    # Whitelist of allowed field names for _update_stats (prevents SQL injection)
    ALLOWED_STATS_UPDATE_FIELDS: ClassVar[set] = {
        "total_operations",
        "operations_completed",
        "operations_failed",
        "operations_rolled_back",
        "total_records_affected",
        "total_records_deleted",
        "total_records_updated",
        "total_records_inserted",
        "total_backups_created",
        "last_operation_at",
        "last_updated_at",
    }

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize state manager.

        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            # Default to cli/db/state.db
            db_dir = Path(__file__).parent
            db_path = db_dir / "state.db"

        self.db_path = str(db_path)
        self._ensure_database()

    def _ensure_database(self):
        """Ensure database exists and schema is initialized."""
        schema_path = Path(__file__).parent / "schema.sql"

        with self._get_connection() as conn:
            with open(schema_path) as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    # ========== Operation State Methods ==========

    def create_operation(self, operation: OperationState) -> str:
        """
        Create a new operation state record.

        Args:
            operation: OperationState model

        Returns:
            operation_id
        """

        # Helper to get value from enum or string (handles both cases due to use_enum_values)
        def get_value(field):
            return field.value if hasattr(field, "value") else field

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO operations (
                    operation_id, operation_name, operation_type, database, collection,
                    field, environment, test_mode, status, operation_folder, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    operation.operation_id,
                    operation.operation_name,
                    get_value(operation.operation_type),
                    operation.database,
                    operation.collection,
                    operation.field,
                    get_value(operation.environment),
                    operation.test_mode,
                    get_value(operation.status),
                    operation.operation_folder,
                    operation.created_by,
                ),
            )
            conn.commit()

        self._update_stats(total_operations=1)
        return operation.operation_id

    def get_operation(self, operation_id: str) -> Optional[OperationState]:
        """
        Get operation state by ID.

        Args:
            operation_id: Operation ID

        Returns:
            OperationState or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM operations WHERE operation_id = ?", (operation_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_operation_state(row)

    def update_operation(self, operation_id: str, **updates) -> bool:
        """
        Update operation state.

        Args:
            operation_id: Operation ID
            **updates: Fields to update

        Returns:
            True if updated, False if not found

        Raises:
            ValueError: If any field name is not in the whitelist (prevents SQL injection)
        """
        # Validate field names against whitelist (SQL injection prevention)
        invalid_fields = set(updates.keys()) - self.ALLOWED_OPERATION_UPDATE_FIELDS
        if invalid_fields:
            raise ValueError(f"Invalid update fields: {invalid_fields}. Allowed fields: {sorted(self.ALLOWED_OPERATION_UPDATE_FIELDS)}")

        # Always update last_updated_at
        updates["last_updated_at"] = datetime.utcnow()

        # Build UPDATE query (safe now that field names are validated)
        set_clause = ", ".join([f"{key} = ?" for key in updates])
        values = [*list(updates.values()), operation_id]

        with self._get_connection() as conn:
            cursor = conn.execute(f"UPDATE operations SET {set_clause} WHERE operation_id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def list_operations(
        self,
        status: Optional[OperationStatus] = None,
        database: Optional[str] = None,
        collection: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[OperationState]:
        """
        List operations with optional filters.

        Args:
            status: Filter by status
            database: Filter by database
            collection: Filter by collection
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of OperationState
        """
        query = "SELECT * FROM operations WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status.value)

        if database:
            query += " AND database = ?"
            params.append(database)

        if collection:
            query += " AND collection = ?"
            params.append(collection)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_operation_state(row) for row in rows]

    def delete_operation(self, operation_id: str) -> bool:
        """
        Delete operation state (and related logs).

        Args:
            operation_id: Operation ID

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            # Delete logs first (foreign key)
            conn.execute("DELETE FROM operation_logs WHERE operation_id = ?", (operation_id,))

            # Delete operation
            cursor = conn.execute("DELETE FROM operations WHERE operation_id = ?", (operation_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ========== Operation Log Methods ==========

    def add_log(self, operation_id: str, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Add log entry for an operation.

        Args:
            operation_id: Operation ID
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            details: Optional details (will be JSON serialized)
        """
        details_json = json.dumps(details) if details else None

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO operation_logs (operation_id, level, message, details)
                VALUES (?, ?, ?, ?)
            """,
                (operation_id, level, message, details_json),
            )
            conn.commit()

    def get_logs(self, operation_id: str, level: Optional[str] = None, limit: int = 100) -> List[OperationLog]:
        """
        Get logs for an operation.

        Args:
            operation_id: Operation ID
            level: Filter by level
            limit: Maximum results

        Returns:
            List of OperationLog
        """
        query = "SELECT * FROM operation_logs WHERE operation_id = ?"
        params = [operation_id]

        if level:
            query += " AND level = ?"
            params.append(level)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_operation_log(row) for row in rows]

    # ========== Lock Management Methods ==========

    def acquire_lock(
        self,
        database: str,
        collection: str,
        operation_id: str,
        locked_by: str,
        duration_minutes: int = 60,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Acquire a lock on a collection.

        Args:
            database: Database name
            collection: Collection name
            operation_id: Operation ID requesting lock
            locked_by: User/system acquiring lock
            duration_minutes: Lock duration in minutes
            reason: Optional reason for lock

        Returns:
            True if lock acquired, False if collection already locked
        """
        lock_id = f"{database}.{collection}"
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)

        # Clean up expired locks first
        self._clean_expired_locks()

        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO operation_locks (lock_id, operation_id, locked_by, expires_at, reason)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (lock_id, operation_id, locked_by, expires_at, reason),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Lock already exists
            return False

    def release_lock(self, database: str, collection: str) -> bool:
        """
        Release a lock on a collection.

        Args:
            database: Database name
            collection: Collection name

        Returns:
            True if lock released, False if no lock existed
        """
        lock_id = f"{database}.{collection}"

        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM operation_locks WHERE lock_id = ?", (lock_id,))
            conn.commit()
            return cursor.rowcount > 0

    def is_locked(self, database: str, collection: str) -> bool:
        """
        Check if a collection is locked.

        Args:
            database: Database name
            collection: Collection name

        Returns:
            True if locked, False otherwise
        """
        lock_id = f"{database}.{collection}"

        # Clean up expired locks first
        self._clean_expired_locks()

        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM operation_locks WHERE lock_id = ?", (lock_id,))
            count = cursor.fetchone()[0]
            return count > 0

    def _clean_expired_locks(self):
        """Remove expired locks."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM operation_locks WHERE expires_at < ?", (datetime.utcnow(),))
            conn.commit()

    # ========== Statistics Methods ==========

    def get_stats(self) -> FrameworkStats:
        """
        Get current framework statistics.

        Returns:
            FrameworkStats
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM framework_stats WHERE stat_id = 1")
            row = cursor.fetchone()

            if not row:
                # Initialize if not exists
                return FrameworkStats()

            return FrameworkStats(
                stat_id=row["stat_id"],
                total_operations=row["total_operations"],
                operations_completed=row["operations_completed"],
                operations_failed=row["operations_failed"],
                operations_rolled_back=row["operations_rolled_back"],
                total_records_affected=row["total_records_affected"],
                total_records_deleted=row["total_records_deleted"],
                total_records_updated=row["total_records_updated"],
                total_records_inserted=row["total_records_inserted"],
                total_backups_created=row["total_backups_created"],
                last_operation_at=datetime.fromisoformat(row["last_operation_at"]) if row["last_operation_at"] else None,
                last_updated_at=datetime.fromisoformat(row["last_updated_at"]),
            )

    def _update_stats(self, **increments):
        """
        Update framework statistics.

        Args:
            **increments: Fields to increment (e.g., total_operations=1)

        Raises:
            ValueError: If any field name is not in the whitelist (prevents SQL injection)
        """
        # Validate field names against whitelist (SQL injection prevention)
        invalid_fields = set(increments.keys()) - self.ALLOWED_STATS_UPDATE_FIELDS
        if invalid_fields:
            raise ValueError(f"Invalid stats fields: {invalid_fields}. Allowed fields: {sorted(self.ALLOWED_STATS_UPDATE_FIELDS)}")

        # Build UPDATE query (safe now that field names are validated)
        set_clause = ", ".join([f"{key} = {key} + ?" for key in increments])
        set_clause += ", last_updated_at = ?"

        values = [*list(increments.values()), datetime.utcnow()]

        with self._get_connection() as conn:
            conn.execute(f"UPDATE framework_stats SET {set_clause} WHERE stat_id = 1", values)
            conn.commit()

    # ========== Helper Methods ==========

    def _safe_get(self, row: sqlite3.Row, key: str, default=None):
        """Safely get a value from sqlite3.Row with a default if key doesn't exist."""
        try:
            return row[key]
        except (KeyError, IndexError):
            return default

    def _row_to_operation_state(self, row: sqlite3.Row) -> OperationState:
        """Convert database row to OperationState model."""
        from yirifi_dq.models.operation import Environment, OperationStatus, OperationType

        return OperationState(
            operation_id=row["operation_id"],
            operation_name=row["operation_name"],
            operation_type=OperationType(row["operation_type"]),
            database=row["database"],
            collection=row["collection"],
            field=row["field"],
            environment=Environment(row["environment"]),
            test_mode=bool(row["test_mode"]),
            status=OperationStatus(row["status"]),
            current_step=row["current_step"],
            progress_percent=row["progress_percent"],
            operation_folder=row["operation_folder"],
            backup_file=row["backup_file"],
            report_file=row["report_file"],
            script_file=row["script_file"],
            config_file=row["config_file"],
            records_affected=row["records_affected"],
            records_deleted=row["records_deleted"],
            records_updated=row["records_updated"],
            records_inserted=row["records_inserted"],
            created_at=datetime.fromisoformat(row["created_at"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            last_updated_at=datetime.fromisoformat(row["last_updated_at"]),
            locked=bool(row["locked"]),
            locked_by=row["locked_by"],
            locked_at=datetime.fromisoformat(row["locked_at"]) if row["locked_at"] else None,
            error_message=row["error_message"],
            error_stack_trace=row["error_stack_trace"],
            created_by=row["created_by"],
            updated_by=row["updated_by"],
            # INDEX.json migration fields (added 2025-11-16)
            summary=self._safe_get(row, "summary"),
            tags=self._safe_get(row, "tags"),
            learnings=self._safe_get(row, "learnings"),
            execution_details=self._safe_get(row, "execution_details"),
            related_collections=self._safe_get(row, "related_collections"),
            next_actions=self._safe_get(row, "next_actions"),
        )

    def _row_to_operation_log(self, row: sqlite3.Row) -> OperationLog:
        """Convert database row to OperationLog model."""
        return OperationLog(
            log_id=row["log_id"],
            operation_id=row["operation_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            level=row["level"],
            message=row["message"],
            details=row["details"],
        )


# Module-level singleton pattern
_state_manager_instance: Optional[StateManager] = None


def get_state_manager(db_path: Optional[str] = None) -> StateManager:
    """
    Get singleton StateManager instance.

    This function ensures only one StateManager instance is created and reused
    across the application, preventing resource leaks from multiple SQLite
    connections.

    Args:
        db_path: Path to SQLite database. If None, uses default location.
                 Note: db_path is only used on first call. Subsequent calls
                 ignore this parameter and return the existing instance.

    Returns:
        StateManager: Singleton StateManager instance.

    Example:
        >>> from yirifi_dq.db.state_manager import get_state_manager
        >>> state_manager = get_state_manager()
        >>> # Subsequent calls return same instance
        >>> same_manager = get_state_manager()
        >>> assert state_manager is same_manager
    """
    global _state_manager_instance

    if _state_manager_instance is None:
        _state_manager_instance = StateManager(db_path=db_path)

    return _state_manager_instance


def reset_state_manager():
    """
    Reset singleton StateManager instance.

    This function is primarily useful for testing, allowing tests to create
    fresh StateManager instances with different configurations.

    Warning:
        This should NOT be used in production code. It's intended only for
        test cleanup.
    """
    global _state_manager_instance
    _state_manager_instance = None
