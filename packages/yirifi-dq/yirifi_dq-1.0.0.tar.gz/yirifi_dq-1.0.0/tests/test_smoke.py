"""
Smoke tests for quick validation that core components load correctly.
Run with: pytest tests/test_smoke.py -m smoke
"""

import pytest


@pytest.mark.smoke
class TestImports:
    """Test that all core modules can be imported."""

    def test_import_models(self):
        """Test importing models."""
        from yirifi_dq.models import operation, state

        assert operation is not None
        assert state is not None

    def test_import_db(self):
        """Test importing database modules."""
        from yirifi_dq.db import state_manager

        assert state_manager is not None

    def test_import_engine(self):
        """Test importing engine modules."""
        from yirifi_dq.engine import orchestrator, safety

        assert orchestrator is not None
        assert safety is not None

    def test_import_utils(self):
        """Test importing utility modules."""
        from yirifi_dq.utils import validators

        assert validators is not None

    def test_import_commands(self):
        """Test importing command modules."""
        from yirifi_dq.commands import new, rollback, verify

        assert new is not None
        assert verify is not None
        assert rollback is not None


@pytest.mark.smoke
class TestModels:
    """Test that core models can be instantiated."""

    def test_operation_config_creation(self):
        """Test creating operation config."""
        from yirifi_dq.models.operation import DuplicateCleanupConfig, Environment, KeepStrategy

        config = DuplicateCleanupConfig(
            database="test_db",
            collection="test_coll",
            field="test_field",
            environment=Environment.DEV,
            keep_strategy=KeepStrategy.OLDEST,
        )

        assert config.database == "test_db"
        assert config.collection == "test_coll"
        assert config.field == "test_field"

    def test_operation_result_models(self):
        """Test creating result models."""
        from yirifi_dq.models.operation import (
            BackupResult,
            DuplicateCleanupResult,
            OrphanCleanupResult,
            RollbackResult,
        )

        dup_result = DuplicateCleanupResult(
            records_affected=10,
            records_deleted=5,
            duplicates_found=5,
            field="url",
            keep_strategy="oldest",
        )
        assert dup_result.records_deleted == 5

        orphan_result = OrphanCleanupResult(orphans_found=3, foreign_key_field="link_yid", parent_collection="links")
        assert orphan_result.orphans_found == 3

        rollback_result = RollbackResult(success=True, restored_count=5, total_documents=5)
        assert rollback_result.success is True

        backup_result = BackupResult(success=True, documents_backed_up=10)
        assert backup_result.success is True


@pytest.mark.smoke
class TestValidators:
    """Test that validators work correctly."""

    def test_path_validation(self):
        """Test path component validation."""
        from yirifi_dq.utils.path_validation import validate_safe_path_component

        # Should not raise
        validate_safe_path_component("valid_name", "Test")

        # Should raise
        with pytest.raises(ValueError):
            validate_safe_path_component("../invalid", "Test")

    def test_environment_validation(self):
        """Test environment validation."""
        from yirifi_dq.utils.path_validation import validate_environment

        # Should not raise
        validate_environment("PRD")
        validate_environment("DEV")
        validate_environment("UAT")

        # Should raise
        with pytest.raises(ValueError):
            validate_environment("INVALID")


@pytest.mark.smoke
class TestStateManager:
    """Test that StateManager can be instantiated."""

    def test_state_manager_creation(self, temp_dir):
        """Test creating StateManager with temp database."""
        from yirifi_dq.db.state_manager import StateManager

        db_path = temp_dir / "test_state.db"
        manager = StateManager(db_path=str(db_path))

        assert manager is not None
        assert db_path.exists()

    def test_state_manager_operations(self, temp_dir):
        """Test basic StateManager operations."""
        from yirifi_dq.db.state_manager import StateManager
        from yirifi_dq.models.operation import Environment, OperationStatus, OperationType
        from yirifi_dq.models.state import OperationState

        db_path = temp_dir / "test_state.db"
        manager = StateManager(db_path=str(db_path))

        # Create operation
        operation = OperationState(
            operation_id="test_123",
            operation_name="test_operation",
            operation_type=OperationType.DUPLICATE_CLEANUP,
            database="test_db",
            collection="test_coll",
            field="test_field",
            environment=Environment.DEV,
            test_mode=True,
            status=OperationStatus.PLANNING,
            operation_folder=str(temp_dir),
            created_by="pytest",
        )

        operation_id = manager.create_operation(operation)
        assert operation_id == "test_123"

        # Retrieve operation
        retrieved = manager.get_operation("test_123")
        assert retrieved is not None
        assert retrieved.operation_id == "test_123"
        assert retrieved.database == "test_db"
