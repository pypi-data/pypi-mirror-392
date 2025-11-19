"""
Script Execution Screen - Run plugin scripts with real-time progress.

This screen executes plugin scripts using the ScriptOrchestrator,
showing real-time progress updates and final results.
"""

from typing import Dict, Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from yirifi_dq.plugins.models import ScriptConfig
from yirifi_dq.plugins.orchestrator import ScriptOrchestrator
from yirifi_dq.db.state_manager import get_state_manager


class ScriptExecutionScreen(Screen):
    """
    Plugin script execution screen with real-time progress.

    Executes plugin scripts using ScriptOrchestrator and displays:
    - Real-time progress updates (connecting, validating, executing, verifying)
    - Final results (records processed/deleted/modified/created)
    - Errors and warnings
    - Operation ID and backup file location

    Keyboard Shortcuts:
    - ESC: Back to scripts list
    - Q: Quit
    """

    BINDINGS = [
        Binding("escape", "back", "Back to Scripts", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #execution-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .execution-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .script-info {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .execution-settings {
        background: $panel;
        padding: 1 2;
        margin-bottom: 1;
        border: solid $secondary;
    }

    .settings-row {
        margin-bottom: 0;
    }

    #progress-section {
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 1;
        min-height: 15;
    }

    .progress-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #progress-status {
        margin-bottom: 1;
    }

    #progress-log {
        color: $text-muted;
        margin-top: 1;
    }

    #results-section {
        border: solid $success;
        padding: 1 2;
        margin-bottom: 1;
        display: none;
    }

    .results-title {
        text-style: bold;
        color: $success;
        margin-bottom: 1;
    }

    #results-content {
        margin-bottom: 1;
    }

    #error-section {
        border: solid $error;
        padding: 1 2;
        margin-bottom: 1;
        display: none;
    }

    .error-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #error-content {
        color: $error;
        margin-bottom: 1;
    }

    .button-group {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    .hidden {
        display: none;
    }

    .visible {
        display: block;
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
        Initialize execution screen.

        Args:
            script_config: Script configuration
            parameters: Script parameters (collected from parameters screen)
            env: Environment (DEV, UAT, PRD)
            test_mode: Test mode flag (limit to 10 records)
            dry_run: Dry run flag (preview only)
        """
        super().__init__()
        self.script_config = script_config
        self.parameters = parameters
        self.env = env
        self.test_mode = test_mode
        self.dry_run = dry_run
        self.operation_id = None
        self.execution_complete = False

    def compose(self) -> ComposeResult:
        """Compose the execution screen."""
        yield Header()

        with Container(id="execution-container"):
            # Title
            yield Static(
                f"⚡ Executing: {self.script_config.name}",
                classes="execution-title"
            )

            # Script info
            info_text = f"ID: {self.script_config.id} | Type: {self.script_config.script_type}"
            yield Static(info_text, classes="script-info")

            # Execution settings summary
            with Container(classes="execution-settings"):
                settings_text = Text()
                settings_text.append("⚙️  Execution Settings\n", style="bold cyan")
                settings_text.append(f"  Environment: ", style="dim")
                settings_text.append(f"{self.env}\n", style="yellow")
                settings_text.append(f"  Test Mode: ", style="dim")
                settings_text.append(f"{'ON (10 records max)' if self.test_mode else 'OFF'}\n", style="green" if self.test_mode else "red")
                settings_text.append(f"  Dry Run: ", style="dim")
                settings_text.append(f"{'ON (preview only)' if self.dry_run else 'OFF'}", style="green" if self.dry_run else "dim")
                yield Static(settings_text, classes="settings-row")

            # Progress section
            with Vertical(id="progress-section"):
                yield Static("📊 Execution Progress", classes="progress-title")
                yield Static("⏳ Starting execution...", id="progress-status")
                yield Static("", id="progress-log")

            # Results section (hidden until complete)
            with Vertical(id="results-section"):
                yield Static("✅ Execution Results", classes="results-title")
                yield Static("", id="results-content")

            # Error section (hidden unless error occurs)
            with Vertical(id="error-section"):
                yield Static("❌ Execution Error", classes="error-title")
                yield Static("", id="error-content")

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back to Scripts", id="back-btn", variant="default")
                yield Button("View Parameters", id="params-btn", variant="primary", disabled=True)

        yield Footer()

    async def on_mount(self) -> None:
        """Execute script when screen mounts."""
        # Get database and collection from parameters
        # Note: The ScriptOrchestrator requires these to be passed separately
        # For now, we'll need to extract them from parameters or have them passed in

        # Extract database and collection (these should be added to __init__ parameters)
        database_name = self.parameters.get("database", "regdb")
        collection_name = self.parameters.get("collection", "links")

        # Remove database/collection from script parameters
        script_params = {k: v for k, v in self.parameters.items() if k not in ["database", "collection"]}

        status_widget = self.query_one("#progress-status", Static)
        log_widget = self.query_one("#progress-log", Static)

        try:
            # Update progress
            status_widget.update("⏳ Initializing orchestrator...")
            log_widget.update("Creating ScriptOrchestrator instance")

            # Create orchestrator
            orchestrator = ScriptOrchestrator(
                env=self.env,
                state_manager=get_state_manager(),
            )

            # Update progress
            status_widget.update("⏳ Validating parameters...")
            log_widget.update("Validating script parameters\nConnecting to database")

            # Execute script
            result = orchestrator.run_script(
                script_id=self.script_config.id,
                parameters=script_params,
                database_name=database_name,
                collection_name=collection_name,
                test_mode=self.test_mode,
                dry_run=self.dry_run,
                auto_backup=True,
                auto_verify=True,
            )

            # Store operation ID if available
            if hasattr(result, 'operation_id'):
                self.operation_id = result.operation_id

            # Update UI based on result
            if result.success:
                self._show_success_results(result)
            else:
                self._show_error_results(result)

            # Mark execution as complete
            self.execution_complete = True

            # Enable params button to allow going back
            self.query_one("#params-btn", Button).disabled = False

        except Exception as e:
            # Handle unexpected errors
            self._show_error_results(None, error=str(e))
            self.execution_complete = True
            self.query_one("#params-btn", Button).disabled = False

    def _show_success_results(self, result) -> None:
        """
        Show successful execution results.

        Args:
            result: ScriptResult object
        """
        status_widget = self.query_one("#progress-status", Static)
        results_section = self.query_one("#results-section", Vertical)
        results_content = self.query_one("#results-content", Static)

        # Check if this was a dry-run
        if self.dry_run and result.dry_run_preview:
            # Show dry-run preview
            status_widget.update("🔍 Dry-run preview completed!")
            results_section.remove_class("hidden")
            results_section.add_class("visible")

            # Change title for dry-run
            results_section.query_one(".results-title", Static).update("🔍 Dry Run Preview")

            # Show preview results
            preview_text = self._format_dry_run_preview(result.dry_run_preview)
            results_content.update(preview_text)
            return

        # Regular execution results
        # Update progress status
        status_widget.update("✅ Execution completed successfully!")

        # Show results section
        results_section.remove_class("hidden")
        results_section.add_class("visible")

        # Build results text
        results_text = Text()

        # Summary
        results_text.append("📊 Summary\n", style="bold white")
        results_text.append(f"  Message: {result.message}\n\n", style="dim")

        # Statistics
        results_text.append("📈 Statistics\n", style="bold white")
        results_text.append(f"  Records Processed: ", style="dim")
        results_text.append(f"{result.records_processed}\n", style="cyan")

        if result.records_deleted > 0:
            results_text.append(f"  Records Deleted: ", style="dim")
            results_text.append(f"{result.records_deleted}\n", style="red")

        if result.records_modified > 0:
            results_text.append(f"  Records Modified: ", style="dim")
            results_text.append(f"{result.records_modified}\n", style="yellow")

        if result.records_created > 0:
            results_text.append(f"  Records Created: ", style="dim")
            results_text.append(f"{result.records_created}\n", style="green")

        # Details
        if result.details:
            results_text.append("\n📋 Details\n", style="bold white")
            for key, value in result.details.items():
                results_text.append(f"  {key}: ", style="dim")
                results_text.append(f"{value}\n", style="white")

        # Warnings
        if result.warnings:
            results_text.append("\n⚠️  Warnings\n", style="bold yellow")
            for warning in result.warnings:
                results_text.append(f"  • {warning}\n", style="yellow")

        # Verification
        if result.verification_checks:
            results_text.append("\n✓ Verification\n", style="bold green")
            for check_name, check_result in result.verification_checks.items():
                status_icon = "✓" if check_result else "✗"
                status_color = "green" if check_result else "red"
                results_text.append(f"  {status_icon} {check_name}\n", style=status_color)

        # Operation ID
        if self.operation_id:
            results_text.append("\n🔖 Operation ID\n", style="bold white")
            results_text.append(f"  {self.operation_id}\n", style="cyan")
            results_text.append(f"  View details: yirifi-dq show {self.operation_id}\n", style="dim")

        results_content.update(results_text)

    def _format_dry_run_preview(self, preview) -> Text:
        """
        Format dry-run preview for display.

        Args:
            preview: DryRunPreview object

        Returns:
            Rich Text object with formatted preview
        """
        text = Text()

        # Operation summary
        text.append("📋 Operation\n", style="bold white")
        text.append(f"  {preview.operation_summary}\n\n", style="dim")

        # Impact summary
        text.append("📊 Would Affect\n", style="bold white")
        if preview.affected_groups_count > 0:
            text.append(f"  Groups found: ", style="dim")
            text.append(f"{preview.affected_groups_count}\n", style="cyan")

        text.append(f"  Records affected: ", style="dim")
        text.append(f"{preview.affected_records_count}\n", style="yellow")

        text.append(f"  Total records: ", style="dim")
        text.append(f"{preview.total_records}\n\n", style="white")

        # Estimated impact
        if preview.estimated_impact:
            text.append("🎯 Estimated Impact\n", style="bold white")
            text.append(f"  {preview.estimated_impact}\n\n", style="dim")

        # Sample records
        if preview.sample_records:
            text.append(f"🔍 Sample Records (first {len(preview.sample_records)})\n", style="bold white")
            for i, sample in enumerate(preview.sample_records[:5], 1):
                if isinstance(sample, dict):
                    if 'value' in sample and 'count' in sample:
                        text.append(f"  {i}. ", style="dim")
                        text.append(f"{sample['value']}", style="yellow")
                        text.append(f" ({sample['count']} copies)\n", style="dim")
                    elif '_id' in sample:
                        text.append(f"  {i}. ID: ", style="dim")
                        text.append(f"{sample['_id']}\n", style="yellow")
                    else:
                        # Generic display
                        sample_str = ", ".join([f"{k}: {v}" for k, v in list(sample.items())[:3]])
                        text.append(f"  {i}. {sample_str}\n", style="dim")
                else:
                    text.append(f"  {i}. {sample}\n", style="dim")

            if preview.affected_groups_count > len(preview.sample_records):
                remaining = preview.affected_groups_count - len(preview.sample_records)
                text.append(f"  ... ({remaining} more groups)\n", style="dim")
            text.append("\n")

        # Safety features
        if preview.safety_features:
            text.append("🛡️  Safety Features\n", style="bold white")
            for feature in preview.safety_features:
                if "would" in feature.lower():
                    text.append(f"  ✓ {feature}\n", style="green")
                elif "ON" in feature:
                    text.append(f"  ✓ {feature}\n", style="green")
                else:
                    text.append(f"  • {feature}\n", style="dim")
            text.append("\n")

        # Warnings
        if preview.warnings:
            text.append("⚠️  Warnings\n", style="bold yellow")
            for warning in preview.warnings:
                text.append(f"  • {warning}\n", style="yellow")
            text.append("\n")

        # Note about dry-run
        text.append("ℹ️  Note\n", style="bold cyan")
        text.append("  This was a dry-run preview. No changes were made.\n", style="dim")
        text.append("  To execute for real, disable dry-run mode.\n", style="dim")

        return text

    def _show_error_results(self, result=None, error: str = None) -> None:
        """
        Show error results.

        Args:
            result: ScriptResult object (if available)
            error: Error message (if result not available)
        """
        status_widget = self.query_one("#progress-status", Static)
        error_section = self.query_one("#error-section", Vertical)
        error_content = self.query_one("#error-content", Static)

        # Update progress status
        status_widget.update("❌ Execution failed")

        # Show error section
        error_section.remove_class("hidden")
        error_section.add_class("visible")

        # Build error text
        error_text = Text()

        if result:
            error_text.append(f"Message: {result.message}\n\n", style="red")

            if result.errors:
                error_text.append("Errors:\n", style="bold red")
                for err in result.errors:
                    error_text.append(f"  • {err}\n", style="red")
        else:
            error_text.append(f"Unexpected error:\n{error}\n", style="red")

        # Operation ID if available
        if self.operation_id:
            error_text.append(f"\nOperation ID: {self.operation_id}\n", style="dim")
            error_text.append(f"View logs: yirifi-dq logs {self.operation_id}\n", style="dim")

        error_content.update(error_text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "params-btn":
            # Go back to parameters screen
            self.app.pop_screen()

    def action_back(self) -> None:
        """Go back to scripts list."""
        # Pop twice: once for this screen, once for parameters screen
        self.app.pop_screen()
        self.app.pop_screen()
