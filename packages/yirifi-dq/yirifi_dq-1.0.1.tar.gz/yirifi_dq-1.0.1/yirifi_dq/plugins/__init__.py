"""
Plugin System Package

Provides infrastructure for creating custom business logic scripts.

This package contains:
- base_script: BaseScript, ScriptContext, ScriptResult
- exceptions: Custom exceptions for plugin system
- models: Pydantic models for YAML config validation
- registry: ScriptRegistry for discovering and loading scripts (Week 3)
- orchestrator: ScriptOrchestrator for executing scripts (Week 3)

Example:
    >>> from yirifi_dq.plugins import BaseScript, ScriptContext, ScriptResult
    >>>
    >>> class MyScript(BaseScript):
    ...     def execute(self, context: ScriptContext) -> ScriptResult:
    ...         return ScriptResult(success=True, message="Done")
"""

# Base classes
from .base_script import BaseScript, ScriptContext, ScriptResult, DryRunPreview

# Exceptions
from .exceptions import (
    ScriptConfigError,
    ScriptExecutionError,
    ScriptLoadError,
    ScriptValidationError,
)

# Pydantic models
from .models import (
    BuiltInOperationConfig,
    SafetyConfig,
    ScriptConfig,
    ScriptExample,
    ScriptParameter,
    VerificationCheck,
)

__all__ = [
    # Base classes
    "BaseScript",
    "ScriptContext",
    "ScriptResult",
    "DryRunPreview",
    # Exceptions
    "ScriptExecutionError",
    "ScriptValidationError",
    "ScriptLoadError",
    "ScriptConfigError",
    # Pydantic models
    "ScriptParameter",
    "SafetyConfig",
    "VerificationCheck",
    "ScriptExample",
    "ScriptConfig",
    "BuiltInOperationConfig",
]
