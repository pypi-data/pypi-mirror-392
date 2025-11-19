"""
Script Registry - Discovery and loading system for custom scripts.

The ScriptRegistry discovers all available scripts by scanning YAML configuration
files in the script_configs/ directory, validates them, and provides methods to
query and instantiate scripts dynamically.

Example:
    >>> from yirifi_dq.plugins.registry import get_registry
    >>>
    >>> # Get singleton registry
    >>> registry = get_registry()
    >>>
    >>> # List all scripts
    >>> scripts = registry.list_scripts()
    >>>
    >>> # Get specific script config
    >>> config = registry.get_script_config('links/clean-old-duplicates')
    >>>
    >>> # Instantiate script
    >>> script = registry.get_script_instance('links/clean-old-duplicates')
    >>> result = script.execute(context)
"""

import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from yirifi_dq.plugins.base_script import BaseScript
from yirifi_dq.plugins.exceptions import ScriptConfigError, ScriptLoadError
from yirifi_dq.plugins.models import ScriptConfig


class ScriptRegistry:
    """
    Discovers and indexes all custom scripts from YAML configs.

    Singleton pattern - loaded once at CLI/TUI startup for performance.
    Scripts are loaded lazily on first access.

    Attributes:
        config_dir: Directory containing YAML config files
        _registry: Dict mapping script_id to ScriptConfig
        _script_instances: Dict mapping script_id to instantiated BaseScript

    Example:
        >>> registry = ScriptRegistry()
        >>> scripts = registry.list_scripts(domain='links')
        >>> for script in scripts:
        ...     print(f"{script.id}: {script.name}")
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize registry and discover scripts.

        Args:
            config_dir: Directory containing YAML configs (defaults to yirifi_dq/script_configs)
        """
        if config_dir is None:
            # Default to yirifi_dq/script_configs
            config_dir = Path(__file__).parent.parent / "script_configs"

        self.config_dir = Path(config_dir)
        self._registry: Dict[str, ScriptConfig] = {}
        self._script_instances: Dict[str, BaseScript] = {}

        # Discover scripts on init
        self._discover_scripts()

    def _discover_scripts(self) -> None:
        """
        Scan config directory and load all YAML files.

        Recursively searches for *.yaml files in config_dir and subdirectories.
        Invalid configs generate warnings but don't stop discovery.
        """
        if not self.config_dir.exists():
            print(f"Warning: Config directory not found: {self.config_dir}")
            return

        discovered_count = 0
        error_count = 0

        # Recursively find all YAML files
        for yaml_file in self.config_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if not data:
                    print(f"Warning: Empty YAML file: {yaml_file.name}")
                    continue

                # Validate against Pydantic schema
                config = ScriptConfig(**data)

                # Register by ID
                if config.id in self._registry:
                    print(
                        f"Warning: Duplicate script ID '{config.id}' "
                        f"in {yaml_file.name} (ignoring)"
                    )
                    continue

                self._registry[config.id] = config
                discovered_count += 1

                print(f" Registered: {config.name} ({config.id})")

            except ValidationError as e:
                print(f" Invalid config {yaml_file.name}:")
                for error in e.errors():
                    field = " -> ".join(str(loc) for loc in error["loc"])
                    print(f"  {field}: {error['msg']}")
                error_count += 1

            except Exception as e:
                print(f" Failed to load {yaml_file.name}: {e}")
                error_count += 1

        print(f"\nScript discovery complete: {discovered_count} registered, {error_count} errors")

    def get_script_config(self, script_id: str) -> Optional[ScriptConfig]:
        """
        Get script configuration by ID.

        Args:
            script_id: Script identifier (e.g., 'links/clean-old-duplicates')

        Returns:
            ScriptConfig if found, None otherwise

        Example:
            >>> config = registry.get_script_config('links/clean-old-duplicates')
            >>> print(config.name)
            'Clean Old Duplicate Links'
        """
        return self._registry.get(script_id)

    def list_scripts(
        self, domain: Optional[str] = None, tag: Optional[str] = None
    ) -> List[ScriptConfig]:
        """
        List all registered scripts with optional filtering.

        Args:
            domain: Filter by domain (links, articles, pipeline, etc.)
            tag: Filter by tag

        Returns:
            List of ScriptConfig objects sorted by name

        Example:
            >>> # All scripts
            >>> all_scripts = registry.list_scripts()
            >>>
            >>> # Scripts in links domain
            >>> link_scripts = registry.list_scripts(domain='links')
            >>>
            >>> # Scripts tagged 'duplicates'
            >>> duplicate_scripts = registry.list_scripts(tag='duplicates')
        """
        scripts = list(self._registry.values())

        # Apply filters
        if domain:
            scripts = [s for s in scripts if s.domain == domain]

        if tag:
            scripts = [s for s in scripts if tag in s.tags]

        # Sort by name
        return sorted(scripts, key=lambda s: s.name)

    def get_script_instance(self, script_id: str) -> BaseScript:
        """
        Load and instantiate script class (cached).

        For custom scripts:
        - Dynamically imports Python module
        - Gets script class from module
        - Validates it inherits from BaseScript
        - Instantiates and caches

        For built-in operations:
        - Returns BuiltInOperationWrapper

        Args:
            script_id: Script identifier

        Returns:
            Instantiated BaseScript subclass

        Raises:
            ScriptLoadError: If script file/class not found or invalid

        Example:
            >>> script = registry.get_script_instance('links/clean-old-duplicates')
            >>> result = script.execute(context)
        """
        # Return cached instance if available
        if script_id in self._script_instances:
            return self._script_instances[script_id]

        # Get config
        config = self.get_script_config(script_id)
        if not config:
            raise ScriptLoadError(f"Script not found: {script_id}")

        # Handle built-in operations
        if config.script_type == "built-in":
            script_instance = self._create_builtin_wrapper(config)
            self._script_instances[script_id] = script_instance
            return script_instance

        # Handle custom scripts
        if not config.script_path:
            raise ScriptLoadError(f"No script_path defined for custom script: {script_id}")

        # Build absolute path to script file
        script_path = Path(config.script_path)
        if not script_path.is_absolute():
            # Relative to project root
            project_root = Path(__file__).parent.parent.parent
            script_path = project_root / script_path

        if not script_path.exists():
            raise ScriptLoadError(f"Script file not found: {script_path}")

        # Dynamically import module
        try:
            module = self._import_module(script_path, config.id)
        except Exception as e:
            raise ScriptLoadError(f"Failed to import {script_path}: {e}")

        # Get script class from module
        if not hasattr(module, config.script_class):
            raise ScriptLoadError(
                f"Class '{config.script_class}' not found in {script_path}\n"
                f"Available classes: {[name for name, obj in inspect.getmembers(module, inspect.isclass)]}"
            )

        script_class = getattr(module, config.script_class)

        # Validate it inherits from BaseScript
        if not issubclass(script_class, BaseScript):
            raise ScriptLoadError(
                f"{config.script_class} must inherit from BaseScript\n"
                f"Current bases: {[base.__name__ for base in script_class.__bases__]}"
            )

        # Instantiate and cache
        try:
            script_instance = script_class()
            self._script_instances[script_id] = script_instance
            return script_instance
        except Exception as e:
            raise ScriptLoadError(f"Failed to instantiate {config.script_class}: {e}")

    def _import_module(self, script_path: Path, script_id: str):
        """
        Dynamically import a Python module from file path.

        Args:
            script_path: Path to Python file
            script_id: Unique identifier for module name

        Returns:
            Imported module object
        """
        # Create unique module name from script_id
        module_name = f"custom_script.{script_id.replace('/', '.')}"

        # Load module from file
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if not spec or not spec.loader:
            raise ScriptLoadError(f"Failed to create module spec for {script_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def _create_builtin_wrapper(self, config: ScriptConfig) -> BaseScript:
        """
        Create wrapper for built-in operations.

        Built-in operations map to core framework functions without
        requiring custom Python scripts.

        Args:
            config: Script configuration

        Returns:
            BuiltInOperationWrapper instance
        """
        from yirifi_dq.plugins.builtin_wrapper import BuiltInOperationWrapper

        return BuiltInOperationWrapper(config.operation, config)

    def search_scripts(
        self,
        query: str,
        domain_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
    ) -> List[ScriptConfig]:
        """
        Search scripts by name or description.

        Args:
            query: Search query (case-insensitive)
            domain_filter: Optional domain filter
            tag_filter: Optional tag filter

        Returns:
            List of matching ScriptConfig objects

        Example:
            >>> results = registry.search_scripts('duplicate')
            >>> for script in results:
            ...     print(script.name)
        """
        query_lower = query.lower()
        results = []

        for config in self._registry.values():
            # Apply domain/tag filters first
            if domain_filter and config.domain != domain_filter:
                continue
            if tag_filter and tag_filter not in config.tags:
                continue

            # Search in name, description, and tags
            if (
                query_lower in config.name.lower()
                or query_lower in config.description.lower()
                or any(query_lower in tag.lower() for tag in config.tags)
            ):
                results.append(config)

        return sorted(results, key=lambda s: s.name)

    def get_script_count_by_domain(self) -> Dict[str, int]:
        """
        Get count of scripts per domain.

        Returns:
            Dict mapping domain to script count

        Example:
            >>> counts = registry.get_script_count_by_domain()
            >>> print(f"Links scripts: {counts['links']}")
        """
        counts: Dict[str, int] = {}
        for config in self._registry.values():
            counts[config.domain] = counts.get(config.domain, 0) + 1
        return counts

    def validate_all_configs(self) -> List[str]:
        """
        Validate all registered script configs.

        Checks:
        - Required parameters have defaults or are marked required
        - Enum parameters have options defined
        - Built-in operations reference valid operations
        - Custom scripts have valid paths

        Returns:
            List of validation warnings/errors

        Example:
            >>> warnings = registry.validate_all_configs()
            >>> if warnings:
            ...     print('\n'.join(warnings))
        """
        warnings = []

        for script_id, config in self._registry.items():
            # Validate parameters
            for param in config.parameters:
                if param.required and param.default is None:
                    # This is OK - required params don't need defaults
                    pass

                if param.type == "enum" and not param.enum:
                    warnings.append(f"{script_id}: Parameter '{param.name}' is enum but has no options")

            # Validate built-in operations
            if config.script_type == "built-in":
                if not config.operation:
                    warnings.append(f"{script_id}: Built-in script missing 'operation' field")

            # Validate custom scripts
            if config.script_type == "custom":
                if not config.script_path:
                    warnings.append(f"{script_id}: Custom script missing 'script_path' field")

        return warnings

    def reload(self) -> None:
        """
        Reload all scripts from disk.

        Clears caches and re-discovers all YAML files.
        Useful for development when configs are changed.

        Example:
            >>> registry.reload()
            Script discovery complete: 5 registered, 0 errors
        """
        self._registry.clear()
        self._script_instances.clear()
        self._discover_scripts()


# Singleton instance
_registry: Optional[ScriptRegistry] = None


def get_registry(config_dir: Optional[Path] = None) -> ScriptRegistry:
    """
    Get or create singleton registry instance.

    Args:
        config_dir: Optional config directory (only used on first call)

    Returns:
        ScriptRegistry singleton

    Example:
        >>> registry = get_registry()
        >>> scripts = registry.list_scripts()
    """
    global _registry
    if _registry is None:
        _registry = ScriptRegistry(config_dir)
    return _registry


def reset_registry() -> None:
    """
    Reset singleton registry (mainly for testing).

    Example:
        >>> reset_registry()
        >>> registry = get_registry()  # Fresh registry
    """
    global _registry
    _registry = None
