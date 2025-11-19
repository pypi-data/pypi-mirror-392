"""
Preview Screen - Show configuration preview before execution.

Displays a summary of the operation/script configuration and allows
the user to confirm or go back to make changes.
"""

from typing import Any, Dict, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from yirifi_dq.plugins.models import ScriptConfig


class PreviewScreen(Screen):
    """
    Configuration preview screen.

    Shows a summary of the operation/script configuration before execution.
    Allows the user to confirm or go back to make changes.

    Keyboard Shortcuts:
    - Enter: Confirm and execute
    - ESC: Go back to make changes
    - Q: Quit
    """

    BINDINGS = [
        Binding("enter", "confirm", "Execute", key_display="Enter"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #preview-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .preview-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .preview-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .preview-section {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .config-item {
        margin: 0 0 0 2;
    }

    .config-key {
        color: $text;
        min-width: 20;
    }

    .config-value {
        color: $accent;
    }

    .safety-info {
        background: $success-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .warning-info {
        background: $warning-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .button-group {
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        script_config: ScriptConfig,
        parameters: Dict[str, Any],
        env: str = "DEV",
        test_mode: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize preview screen.

        Args:
            script_config: The script configuration
            parameters: The collected parameter values
            env: Environment (DEV/UAT/PRD)
            test_mode: Whether to run in test mode
            dry_run: Whether to run in dry-run mode
        """
        super().__init__()
        self.script_config = script_config
        self.parameters = parameters
        self.env = env
        self.test_mode = test_mode
        self.dry_run = dry_run

    def compose(self) -> ComposeResult:
        """Compose the preview screen."""
        yield Header()

        with Container(id="preview-container"):
            yield Static("📋 Preview & Confirm", classes="preview-title")
            yield Static("Review your configuration before execution", classes="preview-subtitle")

            # Script info section
            with Vertical(classes="preview-section"):
                yield Static("Script Information", classes="section-title")
                yield Static(self._format_script_info())

            # Execution settings section
            with Vertical(classes="preview-section"):
                yield Static("Execution Settings", classes="section-title")
                yield Static(self._format_execution_settings())

            # Parameters section
            if self.parameters:
                with Vertical(classes="preview-section"):
                    yield Static("Parameters", classes="section-title")
                    yield Static(self._format_parameters())

            # Safety features section
            with Vertical(classes="safety-info"):
                yield Static("Safety Features", classes="section-title")
                yield Static(self._format_safety_info())

            # Warnings section
            if self.env == "PRD" or not self.test_mode:
                with Vertical(classes="warning-info"):
                    yield Static("Warnings", classes="section-title")
                    yield Static(self._format_warnings())

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")
                yield Button("Execute", id="execute-btn", variant="success")

        yield Footer()

    def _format_script_info(self) -> Text:
        """Format script information."""
        text = Text()

        items = [
            ("Name", self.script_config.name),
            ("ID", self.script_config.id),
            ("Domain", self.script_config.domain),
            ("Type", self.script_config.script_type),
        ]

        for key, value in items:
            text.append(f"  {key}:".ljust(22), style="dim")
            text.append(f"{value}\n", style="cyan")

        return text

    def _format_execution_settings(self) -> Text:
        """Format execution settings."""
        text = Text()

        # Environment with color coding
        text.append(f"  Environment:".ljust(22), style="dim")
        env_style = "red bold" if self.env == "PRD" else "yellow" if self.env == "UAT" else "green"
        text.append(f"{self.env}\n", style=env_style)

        # Database and collection
        db = self.parameters.get("database", "N/A")
        coll = self.parameters.get("collection", "N/A")
        text.append(f"  Database:".ljust(22), style="dim")
        text.append(f"{db}\n", style="cyan")
        text.append(f"  Collection:".ljust(22), style="dim")
        text.append(f"{coll}\n", style="cyan")

        # Test mode
        text.append(f"  Test Mode:".ljust(22), style="dim")
        if self.test_mode:
            text.append("ON (10 records max)\n", style="green")
        else:
            text.append("OFF (all records)\n", style="yellow bold")

        # Dry run
        text.append(f"  Dry Run:".ljust(22), style="dim")
        if self.dry_run:
            text.append("ON (no changes)\n", style="blue")
        else:
            text.append("OFF (will modify data)\n", style="cyan")

        return text

    def _format_parameters(self) -> Text:
        """Format parameter values."""
        text = Text()

        # Filter out database/collection as they're shown in execution settings
        excluded = {"database", "collection", "env", "test_mode", "dry_run"}

        for key, value in sorted(self.parameters.items()):
            if key in excluded:
                continue

            # Format value based on type
            if isinstance(value, bool):
                value_str = "Yes" if value else "No"
            elif isinstance(value, (dict, list)):
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            else:
                value_str = str(value)

            text.append(f"  {key}:".ljust(22), style="dim")
            text.append(f"{value_str}\n", style="cyan")

        if not any(k not in excluded for k in self.parameters):
            text.append("  No additional parameters\n", style="dim")

        return text

    def _format_safety_info(self) -> Text:
        """Format safety features information."""
        text = Text()
        safety = self.script_config.safety

        features = []
        if safety.requires_backup:
            features.append("Auto-backup before changes")
        if safety.requires_verification:
            features.append("Auto-verification after execution")
        if safety.supports_test_mode:
            features.append("Test mode available")
        if safety.locks_collection:
            features.append("Collection locking enabled")

        for feature in features:
            text.append(f"  - {feature}\n", style="white")

        return text

    def _format_warnings(self) -> Text:
        """Format warning messages."""
        text = Text()

        warnings = []

        if self.env == "PRD":
            warnings.append("PRODUCTION environment selected!")

        if not self.test_mode:
            warnings.append("Test mode is OFF - will process all matching records")

        if not self.dry_run:
            warnings.append("Dry run is OFF - will modify actual data")

        for warning in warnings:
            text.append(f"  - {warning}\n", style="yellow bold")

        return text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "execute-btn":
            self.action_confirm()

    def action_back(self) -> None:
        """Go back to parameters screen."""
        self.app.pop_screen()

    def action_confirm(self) -> None:
        """Confirm and proceed to execution."""
        from yirifi_dq.tui.screens.script_execution_screen import ScriptExecutionScreen

        # Pop this screen and push execution screen
        self.app.pop_screen()
        self.app.push_screen(
            ScriptExecutionScreen(
                script_config=self.script_config,
                parameters=self.parameters,
                env=self.env,
                test_mode=self.test_mode,
                dry_run=self.dry_run,
            )
        )

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
