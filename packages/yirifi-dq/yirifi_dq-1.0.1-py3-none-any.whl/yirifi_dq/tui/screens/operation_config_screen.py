"""
Operation Configuration Screen

Context-aware configuration screen that dynamically adapts based on
operation requirements (collection, field, parameters, etc.).
"""

import builtins
import contextlib
from typing import Any, Dict, List

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, RadioButton, RadioSet, Select, Static

from yirifi_dq.config import OperationDefinition, OperationParameter
from yirifi_dq.models.operation import Environment


class OperationConfigScreen(Screen):
    """
    Smart operation configuration screen.

    Dynamically shows/hides configuration sections based on:
    - operation.requires_collection (ask for database/collection)
    - operation.requires_field (ask for field name)
    - operation.requires_environment (ask for DEV/UAT/PRD)
    - operation.auto_run (skip to execution if all info available)
    - operation.parameters (dynamic parameter inputs)
    """

    BINDINGS = [
        Binding("enter", "continue", "Continue", key_display="↵"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #config-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .config-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .operation-info {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .config-section {
        border: solid $secondary;
        padding: 1;
        margin-bottom: 1;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .input-group {
        margin: 1 0;
    }

    .input-label {
        color: $text;
        margin-bottom: 1;
    }

    .input-help {
        color: $text-muted;
        margin-left: 2;
    }

    .auto-run-notice {
        background: $success;
        color: $text;
        padding: 1;
        margin: 1 0;
        text-align: center;
    }

    .button-group {
        height: 3;
        align: center middle;
    }

    .hidden {
        display: none;
    }

    #csv-section, #manual-section, #query-section {
        margin-top: 1;
    }
    """

    def __init__(self, operation: OperationDefinition):
        super().__init__()
        self.operation = operation
        self.config_data: Dict[str, Any] = {}
        self.selected_input_method: str = "csv"  # Default to CSV

        # Check if this operation supports input methods (pipeline operations)
        self.supports_input_methods = self._has_input_methods()

    def _has_input_methods(self) -> bool:
        """Check if operation has input_methods configuration."""
        # Look for input_method parameter or check operation metadata
        return any(param.name == "input_method" for param in self.operation.parameters)

    def _get_supported_input_methods(self) -> List[str]:
        """Get list of supported input methods from operation config."""
        # Check if operation has input_methods in parameters
        for param in self.operation.parameters:
            if param.name == "input_method" and param.options:
                return [opt["value"] for opt in param.options]
        # Default to all three if not specified
        return ["csv", "manual", "query"]

    def compose(self) -> ComposeResult:
        """Compose the configuration screen dynamically."""
        yield Header()

        with Container(id="config-container"):
            yield Static(f"⚙️  Configure: {self.operation.name}", classes="config-title")
            yield Static(self.operation.description, classes="operation-info")

            # Show auto-run notice if applicable
            if self.operation.auto_run:
                yield Static(
                    "✓ This operation can run automatically without collection selection",
                    classes="auto-run-notice",
                )

            # Environment selection (if required)
            if self.operation.requires_environment:
                yield from self._build_environment_section()

            # Collection/Database selection (if required)
            if self.operation.requires_collection:
                yield from self._build_collection_section()

            # Field selection (if required)
            if self.operation.requires_field:
                yield from self._build_field_section()

            # Input method selection (for pipeline operations)
            if self.supports_input_methods:
                yield from self._build_input_method_section()

            # Operation-specific parameters (filtered based on input method)
            if self.operation.parameters:
                yield from self._build_parameters_section()

            # Test mode section (if supported)
            if self.operation.safety.get("supports_test_mode", True):
                yield from self._build_test_mode_section()

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")
                yield Button("Preview", id="preview-btn", variant="primary")

        yield Footer()

    def _build_environment_section(self):
        """Build environment selection section."""
        with Container(classes="config-section"):
            yield Static("MongoDB Environment:", classes="section-title")
            yield Static("Choose which MongoDB instance to connect to:", classes="input-label")

            with RadioSet(id="environment-select"):
                yield RadioButton("DEV - Development (Recommended for testing)", id="env-dev", value=True)
                yield RadioButton("UAT - User Acceptance Testing", id="env-uat")
                yield RadioButton("PRD - Production (Use with caution!)", id="env-prd")

    def _build_collection_section(self):
        """Build collection/database selection section."""
        with Container(classes="config-section"):
            yield Static("Database & Collection:", classes="section-title")

            with Vertical(classes="input-group"):
                yield Static("Database Name:", classes="input-label")
                yield Input(placeholder="e.g., regdb", id="database-input")
                yield Static("The MongoDB database to operate on", classes="input-help")

            with Vertical(classes="input-group"):
                yield Static("Collection Name:", classes="input-label")
                yield Input(placeholder="e.g., links", id="collection-input")
                yield Static("The collection within the database", classes="input-help")

    def _build_field_section(self):
        """Build field selection section."""
        with Container(classes="config-section"):
            yield Static("Field Configuration:", classes="section-title")

            with Vertical(classes="input-group"):
                yield Static("Field Name:", classes="input-label")
                yield Input(placeholder="e.g., url", id="field-input")
                yield Static("The field to perform the operation on", classes="input-help")

    def _build_input_method_section(self):
        """Build input method selection section for pipeline operations."""
        supported_methods = self._get_supported_input_methods()

        with Container(classes="config-section"):
            yield Static("Input Method:", classes="section-title")
            yield Static("Choose how to specify which documents to update:", classes="input-label")

            with RadioSet(id="input-method-select"):
                if "csv" in supported_methods:
                    yield RadioButton("CSV File - Load IDs from CSV file", id="method-csv", value=True)
                if "manual" in supported_methods:
                    yield RadioButton("Manual Entry - Enter IDs directly", id="method-manual")
                if "query" in supported_methods:
                    yield RadioButton("MongoDB Query - Find documents dynamically", id="method-query")

        # CSV File Section
        if "csv" in supported_methods:
            with Container(id="csv-section"), Vertical(classes="input-group"):
                yield Static("CSV File Path:", classes="input-label")
                yield Input(placeholder="/path/to/file.csv", id="csv-file-path")
                yield Static("CSV file with 'link_yid' or 'source_channel_id' column", classes="input-help")

        # Manual Entry Section
        if "manual" in supported_methods:
            with Container(id="manual-section", classes="hidden"), Vertical(classes="input-group"):
                yield Static("Enter IDs (one per line or comma-separated):", classes="input-label")
                yield Input(placeholder="link-yid-1,link-yid-2 or one per line", id="manual-ids")
                yield Static("Enter link_yid values (comma or newline separated)", classes="input-help")

        # Query Section
        if "query" in supported_methods:
            with Container(id="query-section", classes="hidden"):
                with Vertical(classes="input-group"):
                    yield Static("MongoDB Query (JSON):", classes="input-label")
                    yield Input(placeholder='{"status": "va_no"}', id="query-filter")
                    yield Static("MongoDB query in JSON format", classes="input-help")

                with Vertical(classes="input-group"):
                    yield Static("Limit (optional):", classes="input-label")
                    yield Input(placeholder="e.g., 100", id="query-limit")
                    yield Static("Maximum number of documents to process", classes="input-help")

    def _build_parameters_section(self):
        """Build operation-specific parameters section."""
        # Filter out input method-related parameters (we handle them separately)
        excluded_params = {"input_method", "csv_file_path", "manual_ids", "query_filter", "limit"}

        params_to_show = [p for p in self.operation.parameters if p.name not in excluded_params]

        if not params_to_show:
            return

        with Container(classes="config-section"):
            yield Static("Operation Parameters:", classes="section-title")

            for param in params_to_show:
                yield from self._build_parameter_input(param)

    def _build_parameter_input(self, param: OperationParameter):
        """
        Build input widget for a parameter.

        Args:
            param: Parameter definition
        """
        with Vertical(classes="input-group"):
            # Label with required indicator
            label_text = param.name.replace("_", " ").title()
            if param.required:
                label_text += " *"
            yield Static(f"{label_text}:", classes="input-label")

            # Input widget based on type
            if param.type == "boolean":
                with RadioSet(id=f"param-{param.name}"):
                    yield RadioButton("Yes", id=f"{param.name}-yes", value=(param.default))
                    yield RadioButton("No", id=f"{param.name}-no", value=(not param.default))

            elif param.type == "enum" and param.options:
                # Use Select for enum types
                # Textual Select expects (label, value) tuples
                options = [(opt["label"], opt["value"]) for opt in param.options]
                yield Select(options=options, id=f"param-{param.name}", value=param.default)

                # Show option descriptions
                for opt in param.options:
                    yield Static(f"  • {opt['label']}: {opt.get('description', '')}", classes="input-help")

            elif param.type in ["string", "int"]:
                yield Input(
                    placeholder=f"e.g., {param.default}" if param.default else "",
                    id=f"param-{param.name}",
                    value=str(param.default) if param.default else "",
                )

            # Help text
            if param.help:
                yield Static(param.help, classes="input-help")

    def _build_test_mode_section(self):
        """Build test mode section."""
        default_limit = self.operation.safety.get("default_test_limit", 10)

        with Container(classes="config-section"):
            yield Static("Test Mode:", classes="section-title")

            with RadioSet(id="test-mode-select"):
                yield RadioButton(
                    f"Test Mode ON - Limit to {default_limit} records (Recommended)",
                    id="test-on",
                    value=True,
                )
                yield RadioButton("Test Mode OFF - Process all matching records", id="test-off")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle input method selection changes."""
        if event.radio_set.id == "input-method-select":
            if event.pressed.id == "method-csv":
                self._show_input_section("csv")
            elif event.pressed.id == "method-manual":
                self._show_input_section("manual")
            elif event.pressed.id == "method-query":
                self._show_input_section("query")

    def _show_input_section(self, method: str) -> None:
        """Show only the selected input method section."""
        self.selected_input_method = method

        # Hide all sections
        with contextlib.suppress(builtins.BaseException):
            self.query_one("#csv-section").add_class("hidden")
        with contextlib.suppress(builtins.BaseException):
            self.query_one("#manual-section").add_class("hidden")
        with contextlib.suppress(builtins.BaseException):
            self.query_one("#query-section").add_class("hidden")

        # Show selected section
        if method == "csv":
            with contextlib.suppress(builtins.BaseException):
                self.query_one("#csv-section").remove_class("hidden")
        elif method == "manual":
            with contextlib.suppress(builtins.BaseException):
                self.query_one("#manual-section").remove_class("hidden")
        elif method == "query":
            with contextlib.suppress(builtins.BaseException):
                self.query_one("#query-section").remove_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()

        elif event.button.id == "preview-btn" and self._validate_and_collect_config():
            self._navigate_to_preview()

    def _validate_and_collect_config(self) -> bool:
        """
        Validate and collect all configuration data.

        Returns:
            True if validation passed, False otherwise
        """
        try:
            # Collect environment
            if self.operation.requires_environment:
                env_radio = self.query_one("#environment-select", RadioSet)
                if env_radio.pressed_button:
                    env_id = env_radio.pressed_button.id
                    if "dev" in env_id:
                        self.config_data["environment"] = Environment.DEV
                    elif "uat" in env_id:
                        self.config_data["environment"] = Environment.UAT
                    elif "prd" in env_id:
                        self.config_data["environment"] = Environment.PRD

            # Collect database/collection
            if self.operation.requires_collection:
                database = self.query_one("#database-input", Input).value.strip()
                collection = self.query_one("#collection-input", Input).value.strip()

                if not database or not collection:
                    # Show error
                    return False

                self.config_data["database"] = database
                self.config_data["collection"] = collection

            # Collect field
            if self.operation.requires_field:
                field = self.query_one("#field-input", Input).value.strip()

                if not field:
                    return False

                self.config_data["field"] = field

            # Collect input method and related data (for pipeline operations)
            if self.supports_input_methods:
                self.config_data["input_method"] = self.selected_input_method

                if self.selected_input_method == "csv":
                    try:
                        csv_path = self.query_one("#csv-file-path", Input).value.strip()
                        if not csv_path:
                            # Show error - CSV path required
                            return False
                        self.config_data["csv_file_path"] = csv_path
                    except Exception:
                        return False

                elif self.selected_input_method == "manual":
                    try:
                        manual_ids = self.query_one("#manual-ids", Input).value.strip()
                        if not manual_ids:
                            # Show error - IDs required
                            return False
                        self.config_data["manual_ids"] = manual_ids
                    except Exception:
                        return False

                elif self.selected_input_method == "query":
                    try:
                        query_filter = self.query_one("#query-filter", Input).value.strip()
                        if not query_filter:
                            # Show error - Query required
                            return False
                        self.config_data["query_filter"] = query_filter

                        # Optional limit
                        limit_str = self.query_one("#query-limit", Input).value.strip()
                        if limit_str:
                            self.config_data["limit"] = int(limit_str)
                    except Exception:
                        return False

            # Collect other parameters (excluding input method related ones)
            excluded_params = {
                "input_method",
                "csv_file_path",
                "manual_ids",
                "query_filter",
                "limit",
            }

            for param in self.operation.parameters:
                if param.name in excluded_params:
                    continue

                param_id = f"param-{param.name}"

                try:
                    if param.type == "boolean":
                        radio = self.query_one(f"#{param_id}", RadioSet)
                        if radio.pressed_button:
                            self.config_data[param.name] = "yes" in radio.pressed_button.id
                    elif param.type == "enum":
                        select = self.query_one(f"#{param_id}", Select)
                        self.config_data[param.name] = select.value
                    else:
                        input_widget = self.query_one(f"#{param_id}", Input)
                        value = input_widget.value.strip()

                        if param.required and not value:
                            return False

                        if param.type == "int":
                            self.config_data[param.name] = int(value) if value else None
                        else:
                            self.config_data[param.name] = value
                except Exception:
                    # Widget not found or error - skip
                    pass

            # Collect test mode
            if self.operation.safety.get("supports_test_mode"):
                test_radio = self.query_one("#test-mode-select", RadioSet)
                if test_radio.pressed_button:
                    self.config_data["test_mode"] = "test-on" in test_radio.pressed_button.id

            return True

        except Exception:
            # Log error and return False
            return False

    def _navigate_to_preview(self) -> None:
        """Navigate to preview screen."""
        # Store config in app's wizard data
        self.app.wizard_data["operation_config"] = self.config_data

        # TODO: Push preview screen
        # self.app.push_screen(PreviewScreen())
        pass

    def action_continue(self) -> None:
        """Continue to preview."""
        if self._validate_and_collect_config():
            self._navigate_to_preview()

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
