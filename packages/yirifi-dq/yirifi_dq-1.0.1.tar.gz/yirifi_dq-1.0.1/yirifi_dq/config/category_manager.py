#!/usr/bin/env python3
"""
Category and Operation Manager for Yirifi Data Quality Framework.

Manages categorization of operations, loading operation definitions,
and providing flexible organization by domain, workflow, and functionality.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from yirifi_dq.utils import YAMLError, load_yaml


class Category(BaseModel):
    """Represents a category of operations."""

    id: str
    name: str
    description: str
    icon: Optional[str] = None
    order: int = 999
    auto_run: bool = False
    domain: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class OperationParameter(BaseModel):
    """Represents a parameter for an operation."""

    name: str
    type: str  # enum, string, boolean, list, int
    required: bool = False
    default: Any = None
    options: Optional[List[Dict[str, str]]] = None
    help: Optional[str] = None


class OperationDefinition(BaseModel):
    """Represents an operation definition loaded from YAML."""

    id: str
    name: str
    description: str
    version: str = "1.0"
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Requirements
    requires_collection: bool = True
    requires_field: bool = False
    requires_environment: bool = True
    auto_run: bool = False

    # Parent-Child hierarchy support
    is_parent: bool = False
    parent_operation: Optional[str] = None
    sub_operations: List[str] = Field(default_factory=list)
    display_as_submenu: bool = False

    # Parameters
    parameters: List[OperationParameter] = Field(default_factory=list)

    # Safety
    safety: Dict[str, Any] = Field(default_factory=dict)
    verification: List[Dict[str, str]] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)


class QuickAccessGroup(BaseModel):
    """Quick access group of frequently used operations."""

    name: str
    operations: List[str]


class CategoriesConfig(BaseModel):
    """Root configuration for categories."""

    version: str
    framework: str
    categories: List[Category]
    quick_access: List[QuickAccessGroup] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class CategoryManager:
    """
    Manages categories and operation definitions.

    Provides flexible multi-dimensional organization of operations
    by domain, workflow, functionality, and data quality concern.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize CategoryManager.

        Args:
            config_dir: Path to config directory (defaults to cli/config)
        """
        if config_dir is None:
            # Assume we're running from project root
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)

        self.categories_file = self.config_dir / "categories.yaml"
        self.operations_dir = self.config_dir / "operations"

        self._categories: Optional[CategoriesConfig] = None
        self._operations: Dict[str, OperationDefinition] = {}

        # Load on init
        self._load_categories()
        self._load_operations()

    def _load_categories(self) -> None:
        """Load categories configuration from YAML."""
        if not self.categories_file.exists():
            raise YAMLError(f"Categories file not found: {self.categories_file}")

        try:
            data = load_yaml(self.categories_file)
            self._categories = CategoriesConfig(**data)
        except Exception as e:
            raise YAMLError(f"Error loading categories: {e}")

    def _load_operations(self) -> None:
        """Load all operation definitions from YAML files (including subdirectories)."""
        if not self.operations_dir.exists():
            # No operations defined yet, that's okay
            return

        # Load operations from root directory
        for yaml_file in self.operations_dir.glob("*.yaml"):
            try:
                data = load_yaml(yaml_file)
                operation = OperationDefinition(**data)
                self._operations[operation.id] = operation
            except Exception as e:
                # Log but don't fail - continue loading other operations
                print(f"Warning: Failed to load operation {yaml_file.name}: {e}")

        # Load operations from subdirectories (e.g., operations/pipeline/*.yaml)
        for yaml_file in self.operations_dir.glob("**/*.yaml"):
            if yaml_file.parent == self.operations_dir:
                # Skip root level files (already loaded above)
                continue
            try:
                data = load_yaml(yaml_file)
                operation = OperationDefinition(**data)
                self._operations[operation.id] = operation
            except Exception as e:
                # Log but don't fail - continue loading other operations
                print(f"Warning: Failed to load operation {yaml_file.name}: {e}")

    # Category methods

    def get_categories(self, include_auto_run: bool = True) -> List[Category]:
        """
        Get all categories, optionally filtering out auto-run categories.

        Args:
            include_auto_run: Whether to include categories with auto_run=True

        Returns:
            List of categories, sorted by order
        """
        if not self._categories:
            return []

        categories = self._categories.categories
        if not include_auto_run:
            categories = [c for c in categories if not c.auto_run]

        return sorted(categories, key=lambda c: c.order)

    def get_category(self, category_id: str) -> Optional[Category]:
        """
        Get a specific category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category or None if not found
        """
        if not self._categories:
            return None

        for category in self._categories.categories:
            if category.id == category_id:
                return category
        return None

    def get_categories_by_tag(self, tag: str) -> List[Category]:
        """
        Get categories that have a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of matching categories
        """
        if not self._categories:
            return []

        return [c for c in self._categories.categories if tag in c.tags]

    # Operation methods

    def get_operations(self) -> List[OperationDefinition]:
        """
        Get all operations.

        Returns:
            List of all operation definitions
        """
        return list(self._operations.values())

    def get_operation(self, operation_id: str) -> Optional[OperationDefinition]:
        """
        Get a specific operation by ID.

        Args:
            operation_id: Operation ID

        Returns:
            OperationDefinition or None if not found
        """
        return self._operations.get(operation_id)

    def get_operations_by_category(self, category_id: str, include_sub_operations: bool = False) -> List[OperationDefinition]:
        """
        Get all operations that belong to a specific category.

        Args:
            category_id: Category ID
            include_sub_operations: If False, only return parent operations (filter out sub-operations)

        Returns:
            List of operations in that category
        """
        operations = [op for op in self._operations.values() if category_id in op.categories]

        # Filter out sub-operations unless explicitly requested
        if not include_sub_operations:
            operations = [op for op in operations if not op.parent_operation]

        return operations

    def get_operations_by_tag(self, tag: str) -> List[OperationDefinition]:
        """
        Get all operations that have a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of matching operations
        """
        return [op for op in self._operations.values() if tag in op.tags]

    def get_auto_run_operations(self) -> List[OperationDefinition]:
        """
        Get all operations that can auto-run without collection selection.

        Returns:
            List of auto-run operations
        """
        return [op for op in self._operations.values() if op.auto_run]

    def search_operations(self, query: str, category_filter: Optional[str] = None, tag_filter: Optional[str] = None) -> List[OperationDefinition]:
        """
        Search operations by name/description.

        Args:
            query: Search query (case-insensitive)
            category_filter: Optional category ID to filter by
            tag_filter: Optional tag to filter by

        Returns:
            List of matching operations
        """
        query_lower = query.lower()
        results = []

        for op in self._operations.values():
            # Apply filters
            if category_filter and category_filter not in op.categories:
                continue
            if tag_filter and tag_filter not in op.tags:
                continue

            # Search in name and description
            if query_lower in op.name.lower() or query_lower in op.description.lower():
                results.append(op)

        return results

    # Hierarchical operation methods

    def is_parent_operation(self, operation_id: str) -> bool:
        """
        Check if an operation is a parent operation.

        Args:
            operation_id: Operation ID to check

        Returns:
            True if operation is a parent operation
        """
        op = self.get_operation(operation_id)
        return op.is_parent if op else False

    def get_sub_operations(self, parent_id: str) -> List[OperationDefinition]:
        """
        Get all sub-operations of a parent operation.

        Args:
            parent_id: Parent operation ID

        Returns:
            List of sub-operations (in order specified by parent)
        """
        parent = self.get_operation(parent_id)
        if not parent or not parent.is_parent:
            return []

        # Return sub-operations in the order specified by parent.sub_operations
        sub_ops = []
        for sub_id in parent.sub_operations:
            sub_op = self.get_operation(sub_id)
            if sub_op:
                sub_ops.append(sub_op)
            else:
                print(f"Warning: Sub-operation '{sub_id}' not found for parent '{parent_id}'")

        return sub_ops

    def get_parent_operation(self, operation_id: str) -> Optional[OperationDefinition]:
        """
        Get the parent operation of a sub-operation.

        Args:
            operation_id: Operation ID

        Returns:
            Parent operation or None if operation has no parent
        """
        op = self.get_operation(operation_id)
        if not op or not op.parent_operation:
            return None

        return self.get_operation(op.parent_operation)

    # Quick access methods

    def get_quick_access_groups(self) -> List[QuickAccessGroup]:
        """
        Get quick access groups.

        Returns:
            List of quick access groups
        """
        if not self._categories:
            return []
        return self._categories.quick_access

    # Settings methods

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a category system setting.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        if not self._categories:
            return default
        return self._categories.settings.get(key, default)

    # Utility methods

    def get_operation_count_by_category(self) -> Dict[str, int]:
        """
        Get count of operations per category.

        Returns:
            Dict mapping category_id to operation count
        """
        counts: Dict[str, int] = {}

        for op in self._operations.values():
            for cat_id in op.categories:
                counts[cat_id] = counts.get(cat_id, 0) + 1

        return counts

    def validate_operation_categories(self) -> List[str]:
        """
        Validate that all operations reference valid categories.

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        valid_category_ids = {c.id for c in self.get_categories()}

        for op in self._operations.values():
            for cat_id in op.categories:
                if cat_id not in valid_category_ids:
                    errors.append(f"Operation '{op.id}' references invalid category '{cat_id}'")

        return errors

    def reload(self) -> None:
        """Reload all categories and operations from disk."""
        self._categories = None
        self._operations = {}
        self._load_categories()
        self._load_operations()
