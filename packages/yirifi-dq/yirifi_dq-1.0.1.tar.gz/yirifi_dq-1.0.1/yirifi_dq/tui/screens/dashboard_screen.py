"""
Bloomberg-style dashboard screen for power users.

Features:
- Multi-pane layout (operations list | details + logs | stats)
- Live auto-refresh (every 5 seconds)
- Keyboard-first navigation (vim bindings: j/k)
- Real-time operation monitoring
- Quick actions (D/O/P for new operations)
"""

from datetime import datetime
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from yirifi_dq.config.category_manager import CategoryManager
from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.models.state import OperationStatus
from yirifi_dq.tui.screens import OperationConfigScreen


class DashboardScreen(Screen):
    """
    Power-user dashboard with live updates and split panes.

    Layout:
    ┌─────────────────────────────────────────┐
    │ Header                                  │
    ├───────────────────┬─────────────────────┤
    │ Operations List   │ Operation Details   │
    │ (DataTable)       │                     │
    │                   ├─────────────────────┤
    │                   │ Live Logs           │
    ├───────────────────┴─────────────────────┤
    │ Stats Bar                               │
    ├─────────────────────────────────────────┤
    │ Footer (keyboard shortcuts)             │
    └─────────────────────────────────────────┘

    Keyboard Shortcuts:
    - j/k: Move cursor down/up (vim-style)
    - Enter: Show operation details
    - D: New duplicate cleanup
    - O: New orphan cleanup
    - P: New pipeline operation
    - R: Refresh data
    - /: Search (future)
    - Q: Quit
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_operation", "Details", key_display="↵"),
        Binding("d", "new_duplicate_cleanup", "Duplicates", key_display="D"),
        Binding("o", "new_orphan_cleanup", "Orphans", key_display="O"),
        Binding("p", "new_pipeline", "Pipeline", key_display="P"),
        Binding("r", "refresh", "Refresh", key_display="R"),
        Binding("/", "search", "Search", key_display="/"),
        Binding("q", "quit_app", "Quit", key_display="Q"),
    ]

    # CSS is loaded from PowerTerminalApp, no need to load it again here
    # CSS_PATH = str(Path(__file__).parent.parent / "themes" / "bloomberg.tcss")

    # Reactive properties
    auto_refresh_interval = reactive(5.0)  # seconds
    selected_operation_id: Optional[str] = None
    last_log_timestamp: Optional[datetime] = None

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Header()

        with Container(id="main-container"):
            with Horizontal():
                # Left pane: Operation list
                with Vertical(id="left-pane"):
                    yield Static("OPERATION LIST", classes="pane-title")
                    yield DataTable(id="operations-table", zebra_stripes=True)

                # Right pane: Details + Logs
                with Vertical(id="right-pane"):
                    with Container(id="operation-details"):
                        yield Static("OPERATION DETAILS", classes="pane-title")
                        yield Static("Select an operation to view details", id="details-content")

                    with Container(id="live-logs"):
                        yield Static("LIVE LOGS", classes="pane-title")
                        yield Static("Select an operation to view logs", id="logs-content")

            # Bottom stats bar
            with Container(id="bottom-stats"):
                yield Static("Loading stats...", id="stats-bar")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize dashboard on mount."""
        self._setup_operations_table()
        self._load_operations()
        self._update_stats()

        # Start auto-refresh timer
        self.set_interval(self.auto_refresh_interval, self._refresh_data)

    def _setup_operations_table(self) -> None:
        """Setup DataTable columns."""
        table = self.query_one("#operations-table", DataTable)
        table.add_columns(
            "●",  # Status indicator
            "ID",
            "Operation",
            "Collection",
            "Status",
            "Progress",
            "Duration",
        )
        table.cursor_type = "row"

    def _load_operations(self) -> None:
        """Load recent operations from state.db."""
        state_manager = get_state_manager()
        operations = state_manager.list_operations(limit=50)

        table = self.query_one("#operations-table", DataTable)
        table.clear()

        for op in operations:
            status_icon = self._get_status_icon(op.status)
            progress_bar = self._render_progress(op.progress_percent)
            duration = self._format_duration(op.started_at, op.completed_at)

            # Truncate operation name to fit
            op_name = (op.operation_name[:25] + "...") if len(op.operation_name) > 28 else op.operation_name

            # Handle both enum and string status values
            status_str = op.status.value if isinstance(op.status, OperationStatus) else str(op.status)

            table.add_row(
                status_icon,
                op.operation_id[:12],  # Truncate ID
                op_name,
                (op.collection or "N/A")[:15],
                status_str,
                progress_bar,
                duration,
                key=op.operation_id,  # Store full ID as key
            )

        # Auto-select first operation if none selected
        if not self.selected_operation_id and operations:
            self.selected_operation_id = operations[0].operation_id
            self._show_operation_details(operations[0].operation_id)

    def _get_status_icon(self, status) -> Text:
        """Get status indicator icon with color."""
        # Handle both enum and string status values
        status_str = status.value if isinstance(status, OperationStatus) else str(status)

        icons = {
            "executing": ("■", "yellow"),
            "completed": ("●", "green"),
            "failed": ("✗", "red"),
            "planning": ("○", "dim"),
            "ready": ("◉", "cyan"),
            "verifying": ("◐", "yellow"),
            "rolled_back": ("↶", "yellow"),
        }
        icon, color = icons.get(status_str, ("?", "white"))
        return Text(icon, style=color)

    def _render_progress(self, percent: Optional[int]) -> str:
        """Render ASCII progress bar."""
        if percent is None:
            return "─────────"

        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"{bar} {percent}%"

    def _format_duration(self, started_at: Optional[datetime], completed_at: Optional[datetime]) -> str:
        """Format operation duration."""
        if not started_at:
            return "N/A"

        end_time = completed_at or datetime.utcnow()
        delta = end_time - started_at

        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def _refresh_data(self) -> None:
        """Auto-refresh dashboard data."""
        self._load_operations()
        self._update_stats()

        # Refresh details of currently selected operation
        if self.selected_operation_id:
            self._show_operation_details(self.selected_operation_id)

    def _update_stats(self) -> None:
        """Update framework stats bar."""
        state_manager = get_state_manager()
        stats = state_manager.get_stats()

        if not stats:
            stats_text = "No statistics available"
        else:
            stats_text = Text()
            stats_text.append("Total: ", style="dim")
            stats_text.append(f"{stats.total_operations}", style="bold cyan")
            stats_text.append("  Completed: ", style="dim")
            stats_text.append(f"{stats.operations_completed}", style="bold green")
            stats_text.append("  Failed: ", style="dim")
            stats_text.append(f"{stats.operations_failed}", style="bold red")
            stats_text.append("  Deleted: ", style="dim")
            stats_text.append(f"{stats.total_records_deleted:,}", style="bold yellow")

        stats_bar = self.query_one("#stats-bar", Static)
        stats_bar.update(stats_text)

    def action_cursor_down(self) -> None:
        """Move cursor down (vim j)."""
        table = self.query_one("#operations-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up (vim k)."""
        table = self.query_one("#operations-table", DataTable)
        table.action_cursor_up()

    def action_select_operation(self) -> None:
        """Show selected operation details."""
        table = self.query_one("#operations-table", DataTable)

        if table.cursor_row is not None:
            # Get operation ID from row key
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                # The key is the operation_id we stored
                str(row_key[0])  # First element is the key

                # Extract the actual operation ID from the table (column 1)
                actual_op_id = table.get_cell_at(table.cursor_coordinate)

                # Try to get the full operation ID from state_manager
                state_manager = get_state_manager()
                operations = state_manager.list_operations(limit=50)

                for op in operations:
                    if op.operation_id.startswith(actual_op_id):
                        self.selected_operation_id = op.operation_id
                        self._show_operation_details(op.operation_id)
                        break

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in operations table."""
        table = self.query_one("#operations-table", DataTable)

        if event.row_key:
            # Get the operation ID from the row
            row = table.get_row(event.row_key.value)
            if row and len(row) > 1:
                op_id_truncated = row[1]  # ID column

                # Find full operation ID
                state_manager = get_state_manager()
                operations = state_manager.list_operations(limit=50)

                for op in operations:
                    if op.operation_id.startswith(op_id_truncated):
                        self.selected_operation_id = op.operation_id
                        self._show_operation_details(op.operation_id)
                        break

    def _show_operation_details(self, operation_id: str) -> None:
        """Show operation details in right pane."""
        state_manager = get_state_manager()
        operation = state_manager.get_operation(operation_id)

        if not operation:
            details = self.query_one("#details-content", Static)
            details.update("Operation not found")
            return

        # Build details text
        details_text = Text()

        # Operation type and status
        details_text.append("Type:       ", style="dim")
        details_text.append(f"{operation.operation_name}\n", style="bold")

        details_text.append("Status:     ", style="dim")
        # Handle both enum and string status values
        status_str = operation.status.value if isinstance(operation.status, OperationStatus) else str(operation.status)
        status_color = {
            "executing": "yellow",
            "completed": "green",
            "failed": "red",
            "verifying": "yellow",
            "planning": "dim",
        }.get(status_str, "white")
        details_text.append(f"{status_str.upper()}", style=f"bold {status_color}")

        if operation.progress_percent is not None:
            details_text.append(f" ({operation.progress_percent}%)", style="dim")
        details_text.append("\n")

        # Database and collection
        details_text.append("Database:   ", style="dim")
        details_text.append(f"{operation.database or 'N/A'}\n")

        details_text.append("Collection: ", style="dim")
        details_text.append(f"{operation.collection or 'N/A'}\n")

        # Parameters
        if operation.field:
            details_text.append("Field:      ", style="dim")
            details_text.append(f"{operation.field}\n")

        # Keep strategy (only for duplicate cleanup operations)
        keep_strategy = getattr(operation, "keep_strategy", None)
        if keep_strategy:
            details_text.append("Strategy:   ", style="dim")
            details_text.append(f"{keep_strategy}\n")

        # Test mode
        details_text.append("Test Mode:  ", style="dim")
        test_mode_text = "ON (10 records max)" if operation.test_mode else "OFF (all records)"
        test_mode_color = "yellow" if operation.test_mode else "green"
        details_text.append(f"{test_mode_text}\n", style=test_mode_color)

        # Timestamps
        if operation.started_at:
            details_text.append("Started:    ", style="dim")
            details_text.append(f"{operation.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        if operation.completed_at:
            details_text.append("Completed:  ", style="dim")
            details_text.append(f"{operation.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Duration
        if operation.started_at:
            duration = self._format_duration(operation.started_at, operation.completed_at)
            details_text.append("Duration:   ", style="dim")
            details_text.append(f"{duration}\n")

        # Records
        details_text.append("\nRecords:    ", style="dim")
        if operation.records_affected is not None:
            details_text.append(f"{operation.records_affected:,} affected\n")
        if operation.records_deleted is not None:
            details_text.append("            ", style="dim")
            details_text.append(f"{operation.records_deleted:,} deleted\n", style="red")

        # Backup info
        if operation.backup_file:
            details_text.append("\nBackup:     ", style="dim")
            # Truncate long paths
            backup_path = operation.backup_file
            if len(backup_path) > 40:
                backup_path = "..." + backup_path[-37:]
            details_text.append(f"{backup_path}\n", style="cyan")

        # Update details pane
        details = self.query_one("#details-content", Static)
        details.update(details_text)

        # Update logs pane
        self._update_logs(operation_id)

    def _update_logs(self, operation_id: str) -> None:
        """Update logs pane with recent logs."""
        state_manager = get_state_manager()
        logs = state_manager.get_logs(operation_id, limit=20)

        logs_content = self.query_one("#logs-content", Static)

        if not logs:
            logs_content.update("No logs available")
            return

        # Build logs text
        logs_text = Text()

        # Show last 10 logs
        for log in reversed(logs[-10:]):
            # Timestamp
            logs_text.append(log.timestamp.strftime("%H:%M:%S"), style="dim")
            logs_text.append(" ")

            # Level with color
            level_color = {
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "DEBUG": "cyan",
            }.get(log.level, "white")

            logs_text.append(f"{log.level:5s}", style=level_color)
            logs_text.append("  ")

            # Message (truncate if too long)
            message = log.message
            if len(message) > 60:
                message = message[:57] + "..."
            logs_text.append(f"{message}\n")

        logs_content.update(logs_text)

        # Update last log timestamp for future live updates
        if logs:
            self.last_log_timestamp = logs[-1].timestamp

    def action_new_duplicate_cleanup(self) -> None:
        """Quick action: New duplicate cleanup operation."""
        self._launch_operation_wizard("duplicate_cleanup")

    def action_new_orphan_cleanup(self) -> None:
        """Quick action: New orphan cleanup operation."""
        self._launch_operation_wizard("orphan_cleanup")

    def action_new_pipeline(self) -> None:
        """Quick action: New pipeline operation."""
        # Show available pipeline operations
        category_manager = CategoryManager()
        pipeline_ops = category_manager.get_operations_by_category("pipeline_management")

        if pipeline_ops:
            # For now, launch the first pipeline operation
            # TODO: Add a selection screen if multiple pipeline ops exist
            self._launch_operation_wizard(pipeline_ops[0].id)
        else:
            self.app.notify("No pipeline operations configured", severity="warning")

    def _launch_operation_wizard(self, operation_id: str) -> None:
        """Launch operation configuration wizard for given operation ID."""
        category_manager = CategoryManager()
        operation = category_manager.get_operation(operation_id)

        if operation:
            # Push the operation config screen
            config_screen = OperationConfigScreen(operation)
            self.app.push_screen(config_screen, callback=self._on_wizard_dismissed)
        else:
            self.app.notify(f"Operation '{operation_id}' not found", severity="error")

    def _on_wizard_dismissed(self, _result=None) -> None:
        """Called when wizard is dismissed - refresh dashboard."""
        # Refresh operations list to show any newly created operations
        self._load_operations()
        self._update_stats()

    def action_search(self) -> None:
        """Open search modal."""
        self.app.notify("Search coming soon!", severity="information")
        # TODO: Open search modal

    def action_refresh(self) -> None:
        """Manually refresh dashboard data."""
        self._refresh_data()
        self.app.notify("Dashboard refreshed", severity="information")

    def action_quit_app(self) -> None:
        """Quit the application."""
        self.app.exit()
