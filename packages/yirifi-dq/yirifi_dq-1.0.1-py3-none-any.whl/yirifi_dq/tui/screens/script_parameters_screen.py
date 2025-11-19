"""
Script Parameters Screen - Auto-generated parameter collection form.

This screen automatically generates form widgets from script YAML parameters,
allowing users to configure and execute plugin scripts interactively.
"""

import json
from typing import Dict, Any, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Select,
    Static,
    Switch,
    Label,
    TextArea,
)
from textual.validation import ValidationResult, Validator

from yirifi_dq.plugins.models import ScriptConfig, ScriptParameter


class JSONValidator(Validator):
    """
    Real-time JSON syntax validator for TextArea widget.

    Validates JSON on every change and provides clear error messages
    with line/column information.
    """

    def validate(self, value: str) -> ValidationResult:
        """
        Validate JSON syntax.

        Args:
            value: JSON string to validate

        Returns:
            ValidationResult with success or failure + error message
        """
        if not value.strip():
            # Empty is valid (will use default or mark as required)
            return self.success()

        try:
            json.loads(value)
            return self.success()
        except json.JSONDecodeError as e:
            # Provide clear error with line/column
            error_msg = f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"
            return self.failure(error_msg)
        except Exception as e:
            return self.failure(f"Invalid JSON: {str(e)}")


class JSONInputWidget(Container):
    """
    Multi-line JSON editor with real-time syntax validation.

    Features:
    - Multi-line TextArea for comfortable JSON editing
    - Real-time validation with clear error messages
    - Visual feedback (green border for valid, red for invalid)
    - Pretty-printing support on blur
    - Example JSON in placeholder

    This widget wraps a TextArea and adds a validation status indicator.
    """

    DEFAULT_CSS = """
    JSONInputWidget {
        width: 100%;
        height: auto;
    }

    JSONInputWidget TextArea {
        width: 100%;
        height: 8;
        border: solid $primary;
    }

    JSONInputWidget TextArea.valid-json {
        border: solid $success;
    }

    JSONInputWidget TextArea.invalid-json {
        border: solid $error;
    }

    JSONInputWidget .json-status {
        width: 100%;
        height: 1;
        margin-top: 0;
        padding: 0 1;
    }

    JSONInputWidget .json-status-valid {
        color: $success;
    }

    JSONInputWidget .json-status-error {
        color: $error;
    }
    """

    def __init__(
        self,
        param_name: str,
        param_type: str,
        example: Optional[str] = None,
        default: Optional[Any] = None,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """
        Initialize JSON input widget.

        Args:
            param_name: Parameter name for identification
            param_type: 'dict' or 'list'
            example: Example JSON to show in help
            default: Default value
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.param_name = param_name
        self.param_type = param_type
        self.example = example
        self.default = default
        self._is_valid = True
        self._error_message = ""

    def compose(self) -> ComposeResult:
        """Compose the JSON input widget."""
        # Prepare placeholder text
        if self.example:
            placeholder = self.example
        elif self.param_type == "dict":
            placeholder = '{"key": "value"}'
        else:  # list
            placeholder = '["item1", "item2"]'

        # Prepare initial value
        initial_value = ""
        if self.default is not None:
            if isinstance(self.default, (dict, list)):
                initial_value = json.dumps(self.default, indent=2)
            else:
                initial_value = str(self.default)

        # Create TextArea with JSON validator
        self.text_area = TextArea(
            text=initial_value,
            language="json",
            theme="monokai",
            id=f"json-{self.param_name}",
        )
        self.text_area.show_line_numbers = True

        yield self.text_area

        # Status indicator
        self.status_label = Static("", classes="json-status")
        yield self.status_label

    def on_mount(self) -> None:
        """Set up watchers after mounting."""
        self.text_area.watch(self.text_area, "text", self._validate_json)
        # Initial validation
        self._validate_json()

    def _validate_json(self, *args) -> None:
        """
        Validate JSON in real-time and update visual feedback.

        Called on every text change.
        """
        value = self.text_area.text

        if not value.strip():
            # Empty is valid (might be optional or have default)
            self._is_valid = True
            self._error_message = ""
            self.text_area.remove_class("invalid-json", "valid-json")
            self.status_label.update("")
            self.status_label.remove_class("json-status-error", "json-status-valid")
            return

        try:
            json.loads(value)
            # Valid JSON
            self._is_valid = True
            self._error_message = ""
            self.text_area.remove_class("invalid-json")
            self.text_area.add_class("valid-json")
            self.status_label.update("✓ Valid JSON")
            self.status_label.remove_class("json-status-error")
            self.status_label.add_class("json-status-valid")
        except json.JSONDecodeError as e:
            # Invalid JSON with detailed error
            self._is_valid = False
            self._error_message = f"{e.msg} at line {e.lineno}, col {e.colno}"
            self.text_area.remove_class("valid-json")
            self.text_area.add_class("invalid-json")
            self.status_label.update(f"✗ Invalid JSON: {self._error_message}")
            self.status_label.remove_class("json-status-valid")
            self.status_label.add_class("json-status-error")
        except Exception as e:
            # Other errors
            self._is_valid = False
            self._error_message = str(e)
            self.text_area.remove_class("valid-json")
            self.text_area.add_class("invalid-json")
            self.status_label.update(f"✗ Error: {self._error_message}")
            self.status_label.remove_class("json-status-valid")
            self.status_label.add_class("json-status-error")

    @property
    def value(self) -> str:
        """Get current text value."""
        return self.text_area.text

    @property
    def is_valid(self) -> bool:
        """Check if current JSON is valid."""
        return self._is_valid

    @property
    def error_message(self) -> str:
        """Get current error message if invalid."""
        return self._error_message

    def get_parsed_value(self) -> Optional[Any]:
        """
        Parse and return JSON value.

        Returns:
            Parsed dict/list or None if invalid/empty
        """
        if not self.value.strip():
            return None

        if not self._is_valid:
            return None

        try:
            return json.loads(self.value)
        except Exception:
            return None

    def pretty_print(self) -> None:
        """Format JSON with indentation (2 spaces)."""
        if self._is_valid and self.value.strip():
            try:
                parsed = json.loads(self.value)
                formatted = json.dumps(parsed, indent=2)
                self.text_area.text = formatted
            except Exception:
                pass  # Keep original if formatting fails


class ScriptParametersScreen(Screen):
    """
    Auto-generated parameter configuration screen.

    Dynamically creates form widgets based on script YAML parameter definitions.
    Supports:
    - String inputs (text_input)
    - Integer inputs (integer_input)
    - Boolean switches (checkbox)
    - Enum selects (dropdown)
    - Dict/List JSON editor (multi-line with syntax validation)

    JSON Editor Features:
    - Real-time syntax validation
    - Line numbers and syntax highlighting
    - Clear error messages with line/column info
    - Visual feedback (green=valid, red=invalid)
    - Example JSON shown in help text

    Keyboard Shortcuts:
    - Ctrl+R: Run script with current parameters
    - Ctrl+T: Toggle test mode
    - Ctrl+D: Toggle dry run
    - ESC: Back to scripts list
    - Tab: Navigate between fields
    """

    BINDINGS = [
        Binding("ctrl+r", "run_script", "Run", key_display="^R"),
        Binding("ctrl+t", "toggle_test_mode", "Test Mode", key_display="^T"),
        Binding("ctrl+d", "toggle_dry_run", "Dry Run", key_display="^D"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #params-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .params-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .script-info {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    /* 2-Column Layout */
    #main-columns {
        width: 100%;
        height: 1fr;
        margin-bottom: 1;
    }

    #left-column {
        width: 1fr;
        height: 100%;
        padding-right: 1;
    }

    #left-scroll {
        width: 100%;
        height: auto;
    }

    #params-scroll {
        width: 2fr;
        height: 100%;
        border: solid $primary;
        padding: 1 2;
    }

    .param-group {
        width: 100%;
        height: auto;
        margin-bottom: 2;
    }

    .param-label {
        text-style: bold;
        color: $text;
        margin-bottom: 0;
    }

    .param-help {
        color: $text-muted;
        margin-bottom: 1;
    }

    .param-meta {
        color: $accent;
        margin-bottom: 1;
    }

    .param-input {
        width: 100%;
        margin-bottom: 0;
    }

    .execution-settings {
        width: 100%;
        height: auto;
        padding: 1 1;
        background: $panel;
        margin-bottom: 1;
    }

    .settings-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .setting-row {
        height: auto;
        margin-bottom: 1;
    }

    .button-group {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    .validation-error {
        color: $error;
        text-style: bold;
        margin-top: 1;
    }

    .validation-success {
        color: $success;
        text-style: bold;
        margin-top: 1;
    }
    """

    def __init__(self, script_config: ScriptConfig):
        """
        Initialize parameters screen.

        Args:
            script_config: Script configuration from registry
        """
        super().__init__()
        self.script_config = script_config
        self.parameter_values: Dict[str, Any] = {}
        self.parameter_widgets: Dict[str, Any] = {}

        # Execution settings
        self.test_mode = True  # Default to test mode
        self.dry_run = False
        self.env = "DEV"  # Default environment

        # Database and collection (required for execution)
        self.database = "regdb"  # Default database
        self.collection = ""  # No default, must be filled

        # Initialize with default values
        for param in script_config.parameters:
            if param.default is not None:
                self.parameter_values[param.name] = param.default

    def compose(self) -> ComposeResult:
        """Compose the parameters screen."""
        yield Header()

        with Container(id="params-container"):
            # Title
            yield Static(
                f"⚙️  Configure: {self.script_config.name}",
                classes="params-title"
            )

            # Script info
            info_text = f"ID: {self.script_config.id} | Type: {self.script_config.script_type} | Domain: {self.script_config.domain}"
            yield Static(info_text, classes="script-info")

            # 2-Column Layout
            with Horizontal(id="main-columns"):
                # Left column: Database Connection + Execution Settings
                with Vertical(id="left-column"):
                    with ScrollableContainer(id="left-scroll"):
                        # Database and Collection inputs (required)
                        with Container(classes="execution-settings"):
                            yield Static("📊 Database Connection", classes="settings-title")

                            with Vertical(classes="setting-row"):
                                yield Label("Database Name:")
                                yield Input(
                                    placeholder="e.g., regdb",
                                    value=self.database,
                                    id="database-input"
                                )

                            with Vertical(classes="setting-row"):
                                yield Label("Collection Name:")
                                yield Input(
                                    placeholder="e.g., links, articlesdocuments",
                                    value=self.collection,
                                    id="collection-input"
                                )

                        # Execution settings
                        with Container(classes="execution-settings"):
                            yield Static("🎯 Execution Settings", classes="settings-title")

                            with Horizontal(classes="setting-row"):
                                yield Label("Test Mode (limit 10 records):")
                                yield Switch(value=self.test_mode, id="test-mode-switch")

                            with Horizontal(classes="setting-row"):
                                yield Label("Dry Run (preview only):")
                                yield Switch(value=self.dry_run, id="dry-run-switch")

                            with Horizontal(classes="setting-row"):
                                yield Label("Environment:")
                                yield Select(
                                    [("DEV", "DEV"), ("UAT", "UAT"), ("PRD", "PRD")],
                                    value="DEV",
                                    id="env-select"
                                )

                # Right column: Scrollable parameters form
                # NOTE: Widgets must be created inline (not via yield from) to render correctly in ScrollableContainer
                with ScrollableContainer(id="params-scroll"):
                    for param in sorted(self.script_config.parameters, key=lambda p: p.tui_order):
                        with Vertical(classes="param-group"):
                            # Parameter label with required indicator
                            label_text = param.name
                            if param.required:
                                label_text += " *"
                            yield Label(label_text, classes="param-label")

                            # Help text
                            if param.help:
                                yield Static(param.help, classes="param-help")

                            # Metadata (type, default, constraints)
                            meta_parts = [f"Type: {param.type}"]
                            if param.default is not None:
                                meta_parts.append(f"Default: {param.default}")
                            if param.min is not None or param.max is not None:
                                if param.min is not None and param.max is not None:
                                    meta_parts.append(f"Range: {param.min}-{param.max}")
                                elif param.min is not None:
                                    meta_parts.append(f"Min: {param.min}")
                                elif param.max is not None:
                                    meta_parts.append(f"Max: {param.max}")
                            yield Static(" | ".join(meta_parts), classes="param-meta")

                            # Widget based on type
                            widget_id = f"param-{param.name}"

                            if param.type == "boolean":
                                # Boolean → Switch
                                default_value = param.default if param.default is not None else False
                                widget = Switch(value=default_value, id=widget_id)
                                self.parameter_widgets[param.name] = widget
                                yield widget

                            elif param.type == "enum":
                                # Enum → Select dropdown
                                if param.enum:
                                    options = [(opt, opt) for opt in param.enum]
                                    default_value = param.default if param.default is not None else param.enum[0]
                                    widget = Select(options, value=default_value, id=widget_id)
                                    self.parameter_widgets[param.name] = widget
                                    yield widget
                                else:
                                    # Fallback if no options
                                    widget = Input(placeholder=f"Enter {param.name}...", id=widget_id, classes="param-input")
                                    if param.default is not None:
                                        widget.value = str(param.default)
                                    self.parameter_widgets[param.name] = widget
                                    yield widget

                            elif param.type == "integer":
                                # Integer → Input with numeric validation
                                placeholder = f"Enter integer"
                                if param.min is not None or param.max is not None:
                                    placeholder += f" ({param.min or '...'} - {param.max or '...'})"
                                widget = Input(placeholder=placeholder, id=widget_id, classes="param-input")
                                if param.default is not None:
                                    widget.value = str(param.default)
                                self.parameter_widgets[param.name] = widget
                                yield widget

                            elif param.type in ("dict", "list"):
                                # Dict/List → Full JSON editor with validation
                                widget = JSONInputWidget(
                                    param_name=param.name,
                                    param_type=param.type,
                                    example=param.example,
                                    default=param.default,
                                    id=widget_id,
                                    classes="param-input"
                                )
                                self.parameter_widgets[param.name] = widget
                                yield widget

                                # Example if provided (shown below JSON editor)
                                if param.example:
                                    yield Static(f"Example: {param.example}", classes="param-help")

                            else:  # string or other
                                # String → Text input
                                widget = Input(placeholder=f"Enter {param.name}...", id=widget_id, classes="param-input")
                                if param.default is not None:
                                    widget.value = str(param.default)
                                self.parameter_widgets[param.name] = widget
                                yield widget

            # Validation message placeholder
            yield Static("", id="validation-message")

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")
                yield Button("Validate", id="validate-btn", variant="primary")
                yield Button("Run Script", id="run-btn", variant="success")

        yield Footer()

    def _collect_parameter_values(self) -> Dict[str, Any]:
        """
        Collect current values from all parameter widgets.

        Returns:
            Dict mapping parameter name to value
        """
        values = {}

        for param in self.script_config.parameters:
            widget = self.parameter_widgets.get(param.name)

            if widget is None:
                continue

            if isinstance(widget, Switch):
                # Boolean from Switch
                values[param.name] = widget.value

            elif isinstance(widget, Select):
                # Enum from Select
                values[param.name] = widget.value

            elif isinstance(widget, JSONInputWidget):
                # Dict/List from JSON editor
                parsed = widget.get_parsed_value()

                if parsed is not None:
                    values[param.name] = parsed
                elif param.default is not None:
                    values[param.name] = param.default
                # If None and no default, skip (will be caught by validation if required)

            elif isinstance(widget, Input):
                # String, integer, or JSON (dict/list) from Input
                value_str = widget.value.strip()

                if not value_str:
                    # Use default if empty and available
                    if param.default is not None:
                        values[param.name] = param.default
                    continue

                # Type conversion based on parameter type
                if param.type == "integer":
                    try:
                        values[param.name] = int(value_str)
                    except ValueError:
                        # Invalid integer, will be caught by validation
                        values[param.name] = value_str

                elif param.type == "boolean":
                    values[param.name] = value_str.lower() in ("true", "1", "yes")

                elif param.type in ("dict", "list"):
                    # Parse JSON for dict/list parameters
                    try:
                        parsed = json.loads(value_str)
                        values[param.name] = parsed
                    except json.JSONDecodeError as e:
                        # Invalid JSON - keep as string for validation error reporting
                        # The validation step will catch this and provide helpful error
                        values[param.name] = value_str

                else:
                    # String or other types
                    values[param.name] = value_str

        return values

    def _validate_parameters(self) -> tuple[bool, list[str]]:
        """
        Validate collected parameter values.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        values = self._collect_parameter_values()

        for param in self.script_config.parameters:
            widget = self.parameter_widgets.get(param.name)

            # Special validation for JSON widgets
            if isinstance(widget, JSONInputWidget):
                if widget.value.strip() and not widget.is_valid:
                    errors.append(f"{param.name}: {widget.error_message}")
                    continue

            # Check required parameters
            if param.required and param.name not in values:
                errors.append(f"{param.name}: Required parameter missing")
                continue

            if param.name not in values:
                continue

            value = values[param.name]

            # Type validation
            if param.type == "integer":
                if not isinstance(value, int):
                    errors.append(f"{param.name}: Must be an integer")
                    continue

                # Range validation
                if param.min is not None and value < param.min:
                    errors.append(f"{param.name}: Must be >= {param.min}")
                if param.max is not None and value > param.max:
                    errors.append(f"{param.name}: Must be <= {param.max}")

            elif param.type == "enum":
                if param.enum and value not in param.enum:
                    errors.append(f"{param.name}: Must be one of {param.enum}")

            elif param.type == "dict":
                if not isinstance(value, dict):
                    errors.append(f"{param.name}: Must be a valid JSON object (dict)")

            elif param.type == "list":
                if not isinstance(value, list):
                    errors.append(f"{param.name}: Must be a valid JSON array (list)")

        return (len(errors) == 0, errors)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "validate-btn":
            self._validate_and_show_message()
        elif event.button.id == "run-btn":
            self._run_script()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggles."""
        if event.switch.id == "test-mode-switch":
            self.test_mode = event.value
        elif event.switch.id == "dry-run-switch":
            self.dry_run = event.value

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "env-select":
            self.env = event.value

    def _validate_and_show_message(self) -> None:
        """Validate parameters and show result message."""
        is_valid, errors = self._validate_parameters()

        msg_widget = self.query_one("#validation-message", Static)

        if is_valid:
            msg_widget.update("✓ All parameters valid")
            msg_widget.remove_class("validation-error")
            msg_widget.add_class("validation-success")
            self.notify("Parameters validated successfully", severity="information")
        else:
            error_text = "✗ Validation errors:\n" + "\n".join(f"  • {e}" for e in errors)
            msg_widget.update(error_text)
            msg_widget.remove_class("validation-success")
            msg_widget.add_class("validation-error")
            self.notify("Please fix validation errors", severity="error")

    def _run_script(self) -> None:
        """Validate and run the script."""
        # Collect database and collection
        database = self.query_one("#database-input", Input).value
        collection = self.query_one("#collection-input", Input).value

        # Validate database and collection
        if not database or not collection:
            msg_widget = self.query_one("#validation-message", Static)
            msg_widget.update("✗ Database and Collection are required")
            msg_widget.remove_class("validation-success")
            msg_widget.add_class("validation-error")
            self.notify("Please enter database and collection names", severity="error")
            return

        # Validate parameters
        is_valid, errors = self._validate_parameters()

        if not is_valid:
            self._validate_and_show_message()
            return

        # Collect final values
        parameters = self._collect_parameter_values()

        # Add database and collection to parameters
        # (ScriptExecutionScreen will extract them)
        parameters["database"] = database
        parameters["collection"] = collection

        # Import here to avoid circular dependency
        from yirifi_dq.tui.screens.script_execution_screen import ScriptExecutionScreen

        # Push execution screen
        self.app.push_screen(
            ScriptExecutionScreen(
                script_config=self.script_config,
                parameters=parameters,
                env=self.env,
                test_mode=self.test_mode,
                dry_run=self.dry_run,
            )
        )

    def action_run_script(self) -> None:
        """Keyboard shortcut to run script."""
        self._run_script()

    def action_toggle_test_mode(self) -> None:
        """Toggle test mode setting."""
        switch = self.query_one("#test-mode-switch", Switch)
        switch.value = not switch.value
        self.test_mode = switch.value
        self.notify(f"Test mode: {'ON' if self.test_mode else 'OFF'}", severity="information")

    def action_toggle_dry_run(self) -> None:
        """Toggle dry run setting."""
        switch = self.query_one("#dry-run-switch", Switch)
        switch.value = not switch.value
        self.dry_run = switch.value
        self.notify(f"Dry run: {'ON' if self.dry_run else 'OFF'}", severity="information")

    def action_back(self) -> None:
        """Go back to scripts list."""
        self.app.pop_screen()
