"""
Configuration management for Yirifi Data Quality Framework.

Manages categories, operations, templates, and application configuration.
"""

from .app_config import Config, config
from .category_manager import (
    CategoriesConfig,
    Category,
    CategoryManager,
    OperationDefinition,
    OperationParameter,
    QuickAccessGroup,
)

__all__ = [
    "CategoriesConfig",
    "Category",
    # Category management
    "CategoryManager",
    "Config",
    "OperationDefinition",
    "OperationParameter",
    "QuickAccessGroup",
    # Application configuration (NEW: centralized config)
    "config",
]
