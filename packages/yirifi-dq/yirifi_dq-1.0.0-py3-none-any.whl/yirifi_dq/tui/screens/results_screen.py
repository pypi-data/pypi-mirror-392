"""
Results Screen - Show operation results and next steps.

Displays the results of an operation/script execution and provides
guidance on next steps like verification and rollback.
"""

from typing import Any, Dict, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from yirifi_dq.plugins.models import ScriptConfig


class ResultsScreen(Screen):
    """
    Operation results screen.

    Shows the results of a completed operation/script and provides
    next steps for verification and potential rollback.

    Keyboard Shortcuts:
    - Enter: Done (return to scripts list)
    - V: Verify operation
    - R: Rollback operation
    - ESC: Back
    - Q: Quit
    """

    BINDINGS = [
        Binding("enter", "done", "Done", key_display="Enter"),
        Binding("v", "verify", "Verify", key_display="V"),
        Binding("r", "rollback_op", "Rollback", key_display="R"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #results-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .results-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .results-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .results-section {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .success-section {
        background: $success-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .error-section {
        background: $error-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .warning-section {
        background: $warning-darken-2;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .next-steps {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
    }

    .cli-command {
        font-family: monospace;
        background: $surface;
        padding: 1;
        margin: 0 0 1 2;
        color: $primary;
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
        operation_id: str,
        status: str,
        records_affected: int = 0,
        records_deleted: int = 0,
        records_updated: int = 0,
        records_created: int = 0,
        duration_seconds: float = 0.0,
        backup_file: Optional[str] = None,
        error_message: Optional[str] = None,
        verification_passed: Optional[bool] = None,
    ):
        """
        Initialize results screen.

        Args:
            script_config: The script configuration
            operation_id: The operation ID
            status: Operation status (completed, failed, etc.)
            records_affected: Total records affected
            records_deleted: Records deleted
            records_updated: Records updated
            records_created: Records created
            duration_seconds: Execution duration
            backup_file: Path to backup file
            error_message: Error message if failed
            verification_passed: Whether verification passed
        """
        super().__init__()
        self.script_config = script_config
        self.operation_id = operation_id
        self.status = status
        self.records_affected = records_affected
        self.records_deleted = records_deleted
        self.records_updated = records_updated
        self.records_created = records_created
        self.duration_seconds = duration_seconds
        self.backup_file = backup_file
        self.error_message = error_message
        self.verification_passed = verification_passed

    def compose(self) -> ComposeResult:
        """Compose the results screen."""
        yield Header()

        with Container(id="results-container"):
            # Title based on status
            if self.status == "completed":
                yield Static("Operation Results", classes="results-title")
            else:
                yield Static("Operation Failed", classes="results-title")

            yield Static(f"Operation ID: {self.operation_id}", classes="results-subtitle")

            # Status section
            if self.status == "completed":
                with Vertical(classes="success-section"):
                    yield Static("Status: COMPLETED", classes="section-title")
                    yield Static(self._format_success_summary())
            else:
                with Vertical(classes="error-section"):
                    yield Static("Status: FAILED", classes="section-title")
                    yield Static(self._format_error_summary())

            # Statistics section
            with Vertical(classes="results-section"):
                yield Static("Statistics", classes="section-title")
                yield Static(self._format_statistics())

            # Verification section
            if self.verification_passed is not None:
                section_class = "success-section" if self.verification_passed else "warning-section"
                with Vertical(classes=section_class):
                    yield Static("Verification", classes="section-title")
                    yield Static(self._format_verification())

            # Backup info section
            if self.backup_file:
                with Vertical(classes="results-section"):
                    yield Static("Backup", classes="section-title")
                    yield Static(self._format_backup_info())

            # Next steps section
            with Vertical(classes="next-steps"):
                yield Static("Next Steps", classes="section-title")
                yield Static(self._format_next_steps())

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Done", id="done-btn", variant="primary")
                if self.status == "completed":
                    yield Button("Verify", id="verify-btn", variant="default")
                if self.backup_file:
                    yield Button("Rollback", id="rollback-btn", variant="warning")

        yield Footer()

    def _format_success_summary(self) -> Text:
        """Format success summary."""
        text = Text()
        text.append("Operation completed successfully!\n", style="green bold")
        text.append(f"Duration: {self.duration_seconds:.2f}s\n", style="white")
        text.append(f"Total records affected: {self.records_affected:,}", style="cyan")
        return text

    def _format_error_summary(self) -> Text:
        """Format error summary."""
        text = Text()
        text.append("Operation failed!\n", style="red bold")
        if self.error_message:
            text.append(f"Error: {self.error_message}\n", style="white")
        text.append("Check logs for more details.", style="dim")
        return text

    def _format_statistics(self) -> Text:
        """Format statistics."""
        text = Text()

        stats = [
            ("Records Affected", self.records_affected),
            ("Records Deleted", self.records_deleted),
            ("Records Updated", self.records_updated),
            ("Records Created", self.records_created),
            ("Duration", f"{self.duration_seconds:.2f}s"),
        ]

        for label, value in stats:
            text.append(f"  {label}:".ljust(22), style="dim")
            if isinstance(value, int):
                text.append(f"{value:,}\n", style="cyan")
            else:
                text.append(f"{value}\n", style="cyan")

        return text

    def _format_verification(self) -> Text:
        """Format verification results."""
        text = Text()

        if self.verification_passed:
            text.append("All verification checks passed!\n", style="green")
            text.append("  - No remaining duplicates\n", style="white")
            text.append("  - Record count decreased as expected\n", style="white")
        else:
            text.append("Verification checks failed or incomplete.\n", style="yellow")
            text.append("Please run manual verification.\n", style="white")

        return text

    def _format_backup_info(self) -> Text:
        """Format backup information."""
        text = Text()
        text.append(f"  Backup file: {self.backup_file}\n", style="cyan")
        text.append("  Use this file for rollback if needed.", style="dim")
        return text

    def _format_next_steps(self) -> str:
        """Format next steps with CLI commands."""
        return f"""
  To verify operation:
    yirifi-dq verify {self.operation_id}

  To view operation details:
    yirifi-dq show {self.operation_id}

  To rollback (if needed):
    yirifi-dq rollback {self.operation_id}

  To view all operations:
    yirifi-dq list
"""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "done-btn":
            self.action_done()
        elif event.button.id == "verify-btn":
            self.action_verify()
        elif event.button.id == "rollback-btn":
            self.action_rollback_op()

    def action_done(self) -> None:
        """Return to scripts list."""
        # Pop back to scripts list (or dashboard)
        while len(self.app.screen_stack) > 2:
            self.app.pop_screen()
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_verify(self) -> None:
        """Run verification on the operation."""
        self.app.notify(f"Running verification for {self.operation_id}...", severity="information")
        # TODO: Implement verification via orchestrator
        # For now, show CLI command
        self.app.notify(f"Run: yirifi-dq verify {self.operation_id}", severity="information")

    def action_rollback_op(self) -> None:
        """Initiate rollback of the operation."""
        if self.backup_file:
            self.app.notify(f"Rolling back {self.operation_id}...", severity="warning")
            # TODO: Implement rollback via orchestrator
            # For now, show CLI command
            self.app.notify(f"Run: yirifi-dq rollback {self.operation_id}", severity="information")
        else:
            self.app.notify("No backup available for rollback", severity="error")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
