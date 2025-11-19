#!/usr/bin/env python3
"""
YAML utilities for configuration management.

Provides safe YAML loading/dumping with validation and migration support.
"""

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from bson import ObjectId


class YAMLError(Exception):
    """Base exception for YAML operations."""

    pass


class YAMLValidationError(YAMLError):
    """Raised when YAML validation fails."""

    pass


def represent_datetime(dumper: yaml.Dumper, data: datetime) -> yaml.Node:
    """Custom YAML representer for datetime objects."""
    return dumper.represent_scalar("tag:yaml.org,2002:timestamp", data.isoformat())


def represent_date(dumper: yaml.Dumper, data: date) -> yaml.Node:
    """Custom YAML representer for date objects."""
    return dumper.represent_scalar("tag:yaml.org,2002:timestamp", data.isoformat())


def represent_objectid(dumper: yaml.Dumper, data: ObjectId) -> yaml.Node:
    """Custom YAML representer for MongoDB ObjectId."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


# Register custom representers
yaml.add_representer(datetime, represent_datetime)
yaml.add_representer(date, represent_date)
yaml.add_representer(ObjectId, represent_objectid)


def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load YAML file safely.

    Args:
        file_path: Path to YAML file

    Returns:
        Dict containing parsed YAML data

    Raises:
        YAMLError: If file doesn't exist or YAML is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise YAMLError(f"YAML file not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            if not isinstance(data, dict):
                raise YAMLError(f"YAML file must contain a dictionary, got {type(data).__name__}")
            return data
    except yaml.YAMLError as e:
        raise YAMLError(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        raise YAMLError(f"Error reading YAML file {path}: {e}")


def save_yaml(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    sort_keys: bool = False,
    add_header: Optional[str] = None,
) -> None:
    """
    Save data to YAML file with proper formatting.

    Args:
        data: Dictionary to save
        file_path: Path to save YAML file
        sort_keys: Whether to sort dictionary keys
        add_header: Optional comment header to add at the top

    Raises:
        YAMLError: If save operation fails
    """
    path = Path(file_path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding="utf-8") as f:
            # Add header comment if provided
            if add_header:
                for line in add_header.strip().split("\n"):
                    f.write(f"# {line}\n")
                f.write("\n")

            # Dump YAML with nice formatting
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=sort_keys,
                allow_unicode=True,
                indent=2,
                width=120,
            )
    except Exception as e:
        raise YAMLError(f"Error writing YAML file {path}: {e}")


def validate_yaml_structure(data: Dict[str, Any], required_keys: List[str], optional_keys: Optional[List[str]] = None) -> None:
    """
    Validate YAML structure has required keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys
        optional_keys: List of optional keys (for documentation)

    Raises:
        YAMLValidationError: If validation fails
    """
    missing_keys = set(required_keys) - set(data.keys())
    if missing_keys:
        raise YAMLValidationError(f"Missing required keys: {', '.join(missing_keys)}")

    # Check for unexpected keys (optional, just warning)
    all_allowed = set(required_keys) | set(optional_keys or [])
    unexpected = set(data.keys()) - all_allowed
    if unexpected:
        # This is just informational, not an error
        pass


def save_yaml_with_metadata(data: Dict[str, Any], file_path: Union[str, Path], operation_name: Optional[str] = None) -> None:
    """
    Save YAML with auto-generated metadata header.

    Args:
        data: Data to save
        file_path: Path to YAML file
        operation_name: Optional operation name for header
    """
    header_lines = [
        "Yirifi Data Quality Framework",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if operation_name:
        header_lines.append(f"Operation: {operation_name}")

    header_lines.append("")
    header_lines.append("WARNING: Do not manually edit this file unless you know what you're doing")

    save_yaml(data, file_path, add_header="\n".join(header_lines))
