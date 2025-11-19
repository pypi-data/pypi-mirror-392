"""
Integration tests for the plugin system.

This module provides comprehensive end-to-end tests for the plugin system,
covering script discovery, parameter validation, execution, and TUI integration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from yirifi_dq.plugins.registry import ScriptRegistry, get_registry
from yirifi_dq.plugins.orchestrator import ScriptOrchestrator
from yirifi_dq.plugins.models import ScriptConfig, ScriptParameter
from yirifi_dq.plugins.base_script import ScriptContext, ScriptResult
from yirifi_dq.plugins.exceptions import (
    ScriptLoadError,
    ScriptValidationError,
    ScriptExecutionError,
)


class TestScriptRegistry:
    """Test script registry discovery and loading."""

    def test_registry_singleton(self):
        """Test registry is a singleton."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_script_discovery(self):
        """Test scripts are discovered from script_configs directory."""
        registry = get_registry()
        scripts = registry.list_scripts()

        assert len(scripts) > 0, "Should discover at least one script"

        # Check that known scripts are loaded
        script_ids = [s.id for s in scripts]
        assert "links/simple-duplicate-cleanup" in script_ids
        assert "cross_domain/orphan-cleanup" in script_ids

    def test_get_script_config(self):
        """Test retrieving individual script configurations."""
        registry = get_registry()

        # Get a known script
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        assert config is not None
        assert config.id == "links/simple-duplicate-cleanup"
        assert config.name == "Simple Duplicate Cleanup"
        assert config.script_type == "built-in"
        assert config.operation == "duplicate-cleanup"
        assert len(config.parameters) > 0

    def test_filter_by_domain(self):
        """Test filtering scripts by domain."""
        registry = get_registry()

        links_scripts = registry.list_scripts(domain="links")

        assert len(links_scripts) > 0
        for script in links_scripts:
            assert script.domain == "links"

    def test_filter_by_tag(self):
        """Test filtering scripts by tag."""
        registry = get_registry()

        duplicate_scripts = registry.list_scripts(tag="duplicates")

        assert len(duplicate_scripts) > 0
        for script in duplicate_scripts:
            assert "duplicates" in script.tags

    def test_builtin_script_instantiation(self):
        """Test built-in scripts can be instantiated."""
        registry = get_registry()

        # Get a built-in script instance
        script = registry.get_script_instance("links/simple-duplicate-cleanup")

        assert script is not None
        assert hasattr(script, "execute")
        assert hasattr(script, "validate_parameters")


class TestScriptParameters:
    """Test script parameter validation."""

    def test_parameter_types(self):
        """Test different parameter types are loaded correctly."""
        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        # Find field parameter (string type)
        field_param = next((p for p in config.parameters if p.name == "field"), None)
        assert field_param is not None
        assert field_param.type == "string"
        assert field_param.required is True

        # Find keep_strategy parameter (enum type)
        strategy_param = next((p for p in config.parameters if p.name == "keep_strategy"), None)
        assert strategy_param is not None
        assert strategy_param.type == "enum"
        assert len(strategy_param.enum) > 0

    def test_required_parameters(self):
        """Test required parameter validation."""
        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        required_params = [p for p in config.parameters if p.required]
        assert len(required_params) > 0

        # Should have at least 'field' as required
        required_names = [p.name for p in required_params]
        assert "field" in required_names

    def test_default_values(self):
        """Test parameters with default values."""
        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        # keep_strategy should have a default
        strategy_param = next((p for p in config.parameters if p.name == "keep_strategy"), None)
        assert strategy_param is not None
        assert strategy_param.default is not None


class TestScriptSafety:
    """Test script safety configurations."""

    def test_safety_features_configured(self):
        """Test safety features are properly configured."""
        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        assert config.safety is not None
        assert config.safety.requires_backup is True
        assert config.safety.requires_verification is True
        assert config.safety.supports_test_mode is True
        assert config.safety.locks_collection is True

    def test_backup_requirements(self):
        """Test backup requirements for destructive operations."""
        registry = get_registry()

        # Duplicate cleanup should require backup
        dup_config = registry.get_script_config("links/simple-duplicate-cleanup")
        assert dup_config.safety.requires_backup is True

        # Orphan cleanup should require backup
        orphan_config = registry.get_script_config("cross_domain/orphan-cleanup")
        assert orphan_config.safety.requires_backup is True

    def test_test_mode_support(self):
        """Test all scripts support test mode."""
        registry = get_registry()
        scripts = registry.list_scripts()

        for script in scripts:
            assert script.safety.supports_test_mode is True, \
                f"Script {script.id} should support test mode"


class TestBuiltInOperations:
    """Test built-in operation wrappers."""

    def test_duplicate_cleanup_operation(self):
        """Test duplicate cleanup built-in operation."""
        registry = get_registry()
        script = registry.get_script_instance("links/simple-duplicate-cleanup")

        # Create mock context
        context = self._create_mock_context({
            "field": "url",
            "keep_strategy": "oldest"
        })

        # Mock the remove_duplicates function to return success
        with patch.object(context.fixers, 'remove_duplicates') as mock_remove:
            mock_remove.return_value = {
                'total_found': 10,
                'deleted_count': 5
            }

            result = script.execute(context)

            assert result.success is True
            assert result.records_deleted == 5
            mock_remove.assert_called_once()

    def test_orphan_cleanup_operation(self):
        """Test orphan cleanup built-in operation."""
        registry = get_registry()
        script = registry.get_script_instance("cross_domain/orphan-cleanup")

        # Create mock context
        context = self._create_mock_context({
            "foreign_collection": "articlesdocuments",
            "primary_field": "link_yid",
            "foreign_field": "articleYid",
            "action": "delete"
        })

        # Mock the clean_orphans function
        with patch.object(context.fixers, 'clean_orphans') as mock_clean:
            mock_clean.return_value = {
                'orphans_found': 8,
                'deleted_count': 8
            }

            result = script.execute(context)

            assert result.success is True
            assert result.records_deleted == 8
            mock_clean.assert_called_once()

    def _create_mock_context(self, parameters: dict) -> ScriptContext:
        """Create a mock script context for testing."""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"

        context = ScriptContext(
            database=mock_db,
            collection=mock_collection,
            parameters=parameters,
            validators=MagicMock(),
            fixers=MagicMock(),
            analyzers=MagicMock(),
            generators=MagicMock(),
            operation_id="TEST-001",
            environment="DEV",
            test_mode=True,
            dry_run=False,
            state_manager=MagicMock(),
            logger=MagicMock(),
        )

        return context


class TestScriptOrchestrator:
    """Test script orchestrator integration."""

    @patch('yirifi_dq.plugins.orchestrator.get_client')
    @patch('yirifi_dq.plugins.orchestrator.get_database')
    @patch('yirifi_dq.plugins.orchestrator.get_collection')
    def test_orchestrator_initialization(self, mock_get_collection, mock_get_database, mock_get_client):
        """Test orchestrator can be initialized."""
        orchestrator = ScriptOrchestrator(env="DEV")

        assert orchestrator is not None
        assert orchestrator.env == "DEV"
        assert orchestrator.registry is not None

    def test_list_available_scripts(self):
        """Test orchestrator can list available scripts."""
        orchestrator = ScriptOrchestrator(env="DEV")

        scripts = orchestrator.list_available_scripts()

        assert len(scripts) > 0
        assert all(hasattr(s, 'id') for s in scripts)

    def test_get_script_info(self):
        """Test orchestrator can get script information."""
        orchestrator = ScriptOrchestrator(env="DEV")

        info = orchestrator.get_script_info("links/simple-duplicate-cleanup")

        assert info is not None
        assert info['id'] == "links/simple-duplicate-cleanup"
        assert info['name'] == "Simple Duplicate Cleanup"
        assert 'parameters' in info
        assert 'safety' in info


class TestTUIIntegration:
    """Test TUI screen integration."""

    def test_scripts_list_screen_import(self):
        """Test ScriptsListScreen can be imported."""
        from yirifi_dq.tui.screens import ScriptsListScreen

        assert ScriptsListScreen is not None

    def test_script_parameters_screen_import(self):
        """Test ScriptParametersScreen can be imported."""
        from yirifi_dq.tui.screens import ScriptParametersScreen

        assert ScriptParametersScreen is not None

    def test_script_execution_screen_import(self):
        """Test ScriptExecutionScreen can be imported."""
        from yirifi_dq.tui.screens import ScriptExecutionScreen

        assert ScriptExecutionScreen is not None

    def test_scripts_list_screen_creation(self):
        """Test ScriptsListScreen can be created."""
        from yirifi_dq.tui.screens import ScriptsListScreen

        screen = ScriptsListScreen()

        assert screen is not None
        assert len(screen.all_scripts) > 0
        assert len(screen.filtered_scripts) > 0

    def test_script_parameters_screen_creation(self):
        """Test ScriptParametersScreen can be created with script config."""
        from yirifi_dq.tui.screens import ScriptParametersScreen

        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        screen = ScriptParametersScreen(config)

        assert screen is not None
        assert screen.script_config == config
        assert screen.test_mode is True
        assert screen.env == "DEV"


class TestCLICommands:
    """Test CLI command integration."""

    def test_scripts_list_command_import(self):
        """Test scripts list command can be imported."""
        from yirifi_dq.commands.scripts import execute_scripts_list_command

        assert execute_scripts_list_command is not None

    def test_scripts_info_command_import(self):
        """Test scripts info command can be imported."""
        from yirifi_dq.commands.scripts import execute_scripts_info_command

        assert execute_scripts_info_command is not None

    def test_run_command_import(self):
        """Test run command can be imported."""
        from yirifi_dq.commands.run import execute_run_command

        assert execute_run_command is not None


class TestErrorHandling:
    """Test error handling in plugin system."""

    def test_invalid_script_id(self):
        """Test handling of invalid script ID."""
        registry = get_registry()

        config = registry.get_script_config("invalid/nonexistent-script")

        assert config is None

    def test_missing_required_parameters(self):
        """Test validation of missing required parameters."""
        registry = get_registry()
        script = registry.get_script_instance("links/simple-duplicate-cleanup")

        # Create context without required 'field' parameter
        context = self._create_mock_context({})

        # Validate should fail
        errors = script.validate_parameters(context)

        assert len(errors) > 0
        assert any("field" in error.lower() for error in errors)

    def test_invalid_enum_value(self):
        """Test validation of invalid enum values."""
        registry = get_registry()
        script = registry.get_script_instance("links/simple-duplicate-cleanup")

        # Create context with invalid keep_strategy
        context = self._create_mock_context({
            "field": "url",
            "keep_strategy": "invalid_strategy"
        })

        # Validate should fail
        errors = script.validate_parameters(context)

        assert len(errors) > 0

    def _create_mock_context(self, parameters: dict) -> ScriptContext:
        """Create a mock script context for testing."""
        mock_db = MagicMock()
        mock_collection = MagicMock()

        context = ScriptContext(
            database=mock_db,
            collection=mock_collection,
            parameters=parameters,
            validators=MagicMock(),
            fixers=MagicMock(),
            analyzers=MagicMock(),
            generators=MagicMock(),
            operation_id="TEST-001",
            environment="DEV",
            test_mode=True,
            dry_run=False,
            state_manager=MagicMock(),
            logger=MagicMock(),
        )

        return context


class TestDomainOrganization:
    """Test domain-based organization."""

    def test_all_domains_present(self):
        """Test expected domains are present."""
        registry = get_registry()
        scripts = registry.list_scripts()

        domains = set(s.domain for s in scripts)

        assert "links" in domains
        assert "articles" in domains
        assert "cross_domain" in domains
        assert "maintenance" in domains

    def test_domain_specific_scripts(self):
        """Test domain-specific scripts are properly categorized."""
        registry = get_registry()

        # Links domain scripts
        links_scripts = registry.list_scripts(domain="links")
        assert len(links_scripts) >= 2  # At least simple-duplicate-cleanup and orphan-articles-cleanup

        # Articles domain scripts
        articles_scripts = registry.list_scripts(domain="articles")
        assert len(articles_scripts) >= 1  # At least duplicate-cleanup


class TestScriptExamples:
    """Test script examples and documentation."""

    def test_examples_provided(self):
        """Test scripts have usage examples."""
        registry = get_registry()
        scripts = registry.list_scripts()

        for script in scripts:
            assert len(script.examples) > 0, \
                f"Script {script.id} should have at least one example"

    def test_example_format(self):
        """Test examples have required fields."""
        registry = get_registry()
        config = registry.get_script_config("links/simple-duplicate-cleanup")

        for example in config.examples:
            assert hasattr(example, 'description')
            assert hasattr(example, 'cli')
            assert len(example.description) > 0
            assert len(example.cli) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
