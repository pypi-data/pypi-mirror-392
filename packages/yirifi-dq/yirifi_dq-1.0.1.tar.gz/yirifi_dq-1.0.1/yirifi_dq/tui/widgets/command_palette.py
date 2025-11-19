"""
Command palette for fuzzy search across operations, scripts, and commands.

Inspired by VS Code's command palette (Ctrl+P) and Bloomberg terminal search.

Features:
- Fuzzy search across all scripts, operations, commands, shortcuts
- System commands (screenshot, theme, settings, help)
- Plugin script quick-launch
- Instant execution from search results
- Recent commands history
- Keyboard-only navigation
"""

import webbrowser
from datetime import datetime
from typing import Callable, List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, ListItem, ListView, Static

from yirifi_dq.config.category_manager import CategoryManager
from yirifi_dq.plugins.registry import get_registry


class Command:
    """Represents a searchable command."""

    def __init__(
        self,
        name: str,
        description: str,
        shortcut: str = "",
        action: Optional[Callable] = None,
        category: str = "",
    ):
        self.name = name
        self.description = description
        self.shortcut = shortcut
        self.action = action
        self.category = category

    def matches(self, query: str) -> bool:
        """Check if command matches the search query."""
        query_lower = query.lower()
        return query_lower in self.name.lower() or query_lower in self.description.lower() or query_lower in self.category.lower() or query_lower in self.shortcut.lower()


class CommandPalette(ModalScreen):
    """
    Command palette modal for fuzzy search.

    Usage:
        app.push_screen(CommandPalette())

    Keyboard:
    - Type to search
    - Up/Down or j/k to navigate
    - Enter to execute
    - Esc to close
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", key_display="ESC"),
        Binding("enter", "execute", "Execute", key_display="↵"),
        Binding("down", "cursor_down", show=False),
        Binding("up", "cursor_up", show=False),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
    ]

    # CSS removed to avoid conflicts - using default Textual modal styling
    # Will add custom styling later
    # CSS = """
    # CommandPalette {
    #     align: center middle;
    # }
    #
    # #palette-container {
    #     width: 80;
    #     height: 30;
    #     border: thick $primary;
    #     background: $panel;
    #     padding: 1;
    # }
    #
    # #palette-title {
    #     color: $accent;
    #     text-style: bold;
    #     margin-bottom: 1;
    # }
    #
    # #search-input {
    #     width: 100%;
    #     margin-bottom: 1;
    # }
    #
    # #results-list {
    #     height: 1fr;
    #     border: solid $border;
    # }
    #
    # .result-item {
    #     padding: 0 1;
    #     height: auto;
    # }
    #
    # .result-name {
    #     text-style: bold;
    #     color: $accent;
    # }
    #
    # .result-description {
    #     color: $text-muted;
    # }
    #
    # .result-shortcut {
    #     color: $primary;
    # }
    #
    # .result-category {
    #     color: $text-muted;
    #     text-style: italic;
    # }
    #
    # #no-results {
    #     color: $text-muted;
    #     text-align: center;
    #     margin: 2;
    # }
    # """

    def __init__(self):
        super().__init__()
        self.all_commands: List[Command] = []
        self.filtered_commands: List[Command] = []

    def compose(self) -> ComposeResult:
        """Compose the command palette layout."""
        with Vertical(id="palette-container"):
            yield Static("⚡ COMMAND PALETTE", id="palette-title")
            yield Input(placeholder="Search operations, commands, shortcuts...", id="search-input")
            yield ListView(id="results-list")

    def on_mount(self) -> None:
        """Focus search input on mount and load commands."""
        self.query_one("#search-input", Input).focus()
        self._load_all_commands()
        self._render_results(self.all_commands)

    def _load_all_commands(self) -> None:
        """Load all available commands from category manager and registry."""
        category_manager = CategoryManager()

        # Add operation commands
        for category in category_manager.get_categories():
            operations = category_manager.get_operations_by_category(category.id)

            for op in operations:
                shortcut = self._get_operation_shortcut(op.id)

                # Use a lambda with default argument to capture the operation
                command = Command(
                    name=op.name,
                    description=op.description,
                    shortcut=shortcut,
                    action=lambda operation_id=op.id: self._execute_operation(operation_id),
                    category=category.name,
                )
                self.all_commands.append(command)

        # Add plugin script commands
        try:
            registry = get_registry()
            scripts = registry.list_scripts()
            for script in scripts:
                command = Command(
                    name=f"Run: {script.name}",
                    description=script.description.split("\n")[0][:80],
                    shortcut="",
                    action=lambda s=script: self._launch_script(s),
                    category="Scripts",
                )
                self.all_commands.append(command)
        except Exception:
            pass  # Registry not available

        # Add quick creation commands
        self.all_commands.extend(
            [
                Command(
                    name="New Duplicate Cleanup",
                    description="Create new duplicate cleanup operation",
                    shortcut="D",
                    action=lambda: self._create_operation("duplicate_cleanup"),
                    category="Create",
                ),
                Command(
                    name="New Orphan Cleanup",
                    description="Create new orphan cleanup operation",
                    shortcut="O",
                    action=lambda: self._create_operation("orphan_cleanup"),
                    category="Create",
                ),
                Command(
                    name="New Pipeline Operation",
                    description="Create new pipeline operation",
                    shortcut="P",
                    action=lambda: self._create_pipeline_operation(),
                    category="Create",
                ),
            ]
        )

        # Add navigation commands
        self.all_commands.extend(
            [
                Command(
                    name="View Dashboard",
                    description="Show main dashboard with operations overview",
                    shortcut="1",
                    action=lambda: self._switch_screen("dashboard"),
                    category="Navigation",
                ),
                Command(
                    name="View Operation List",
                    description="Show list of all operations",
                    shortcut="2",
                    action=lambda: self._switch_screen("operations"),
                    category="Navigation",
                ),
                Command(
                    name="View Logs",
                    description="Show operation logs",
                    shortcut="3",
                    action=lambda: self._switch_screen("logs"),
                    category="Navigation",
                ),
                Command(
                    name="View Stats",
                    description="Show framework statistics",
                    shortcut="4",
                    action=lambda: self._switch_screen("stats"),
                    category="Navigation",
                ),
                Command(
                    name="Browse Scripts",
                    description="Open plugin scripts browser",
                    shortcut="6",
                    action=lambda: self._show_scripts(),
                    category="Navigation",
                ),
            ]
        )

        # Add system commands
        self.all_commands.extend(
            [
                Command(
                    name="Take Screenshot",
                    description="Save current screen as SVG file",
                    shortcut="Ctrl+Shift+S",
                    action=lambda: self._take_screenshot(),
                    category="System",
                ),
                Command(
                    name="Cycle Theme",
                    description="Cycle through available themes",
                    shortcut="Ctrl+T",
                    action=lambda: self._toggle_theme(),
                    category="System",
                ),
            ]
        )

        self.all_commands.extend(
            [
                Command(
                    name="Refresh Data",
                    description="Refresh all data from state.db",
                    shortcut="R",
                    action=lambda: self._refresh_data(),
                    category="System",
                ),
                Command(
                    name="Clear Notifications",
                    description="Clear all notification messages",
                    shortcut="",
                    action=lambda: self._clear_notifications(),
                    category="System",
                ),
                Command(
                    name="Export Operations",
                    description="Export operations history to JSON file",
                    shortcut="",
                    action=lambda: self._export_operations(),
                    category="System",
                ),
                Command(
                    name="Quit Application",
                    description="Exit yirifi-dq TUI",
                    shortcut="Q",
                    action=lambda: self.app.exit(),
                    category="System",
                ),
            ]
        )

        # Add help and documentation commands
        self.all_commands.extend(
            [
                Command(
                    name="Show Help",
                    description="Show keyboard shortcuts and help",
                    shortcut="?",
                    action=lambda: self._show_help(),
                    category="Help",
                ),
                Command(
                    name="Open Documentation",
                    description="Open documentation in web browser",
                    shortcut="",
                    action=lambda: self._open_docs(),
                    category="Help",
                ),
                Command(
                    name="Show About",
                    description="Show version and system information",
                    shortcut="",
                    action=lambda: self._show_about(),
                    category="Help",
                ),
            ]
        )

    def _get_operation_shortcut(self, operation_id: str) -> str:
        """Get keyboard shortcut for operation."""
        shortcuts = {
            "duplicate_cleanup": "D",
            "orphan_cleanup": "O",
            "framework_stats": "S",
            "pipeline_reset": "P",
        }
        return shortcuts.get(operation_id, "")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter results as user types."""
        query = event.value.strip()

        if not query:
            self.filtered_commands = self.all_commands
        else:
            # Fuzzy search - case insensitive
            self.filtered_commands = [cmd for cmd in self.all_commands if cmd.matches(query)]

        self._render_results(self.filtered_commands)

    def _render_results(self, commands: List[Command]) -> None:
        """Render search results in the list view."""
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()

        if not commands:
            # Show "no results" message
            no_results = Static("No matching commands found", id="no-results")
            results_list.append(ListItem(no_results))
            return

        # Limit to top 20 results
        for cmd in commands[:20]:
            item_text = Text()

            # Command name (bold cyan)
            item_text.append(cmd.name, style="bold cyan")

            # Shortcut (if available)
            if cmd.shortcut:
                item_text.append(f"  [{cmd.shortcut}]", style="yellow")

            # Category
            if cmd.category:
                item_text.append(f"  ({cmd.category})", style="dim italic")

            item_text.append("\n")

            # Description (dim)
            item_text.append(f"  {cmd.description}", style="dim")

            list_item = ListItem(Static(item_text), classes="result-item")
            list_item.command = cmd  # Store command reference for click handling
            results_list.append(list_item)

    def action_cursor_down(self) -> None:
        """Move cursor down in results list."""
        results_list = self.query_one("#results-list", ListView)
        results_list.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in results list."""
        results_list = self.query_one("#results-list", ListView)
        results_list.action_cursor_up()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle click selection from list view."""
        if hasattr(event.item, "command"):
            command = event.item.command
            # Dismiss the palette first
            self.dismiss()
            # Execute the command action
            if command.action:
                command.action()

    def action_execute(self) -> None:
        """Execute selected command."""
        results_list = self.query_one("#results-list", ListView)

        if results_list.index is not None and self.filtered_commands:
            # Get the selected command
            selected_index = results_list.index
            if 0 <= selected_index < len(self.filtered_commands):
                command = self.filtered_commands[selected_index]

                # Dismiss the palette first
                self.dismiss()

                # Execute the command action
                if command.action:
                    command.action()

    def action_cancel(self) -> None:
        """Close command palette without executing."""
        self.dismiss()

    def _execute_operation(self, operation_id: str) -> None:
        """Execute an operation by ID."""
        # TODO: Navigate to operation config screen or execute directly
        self.app.notify(f"Executing operation: {operation_id}", severity="information")

    def _create_operation(self, operation_id: str) -> None:
        """Create a new operation via wizard."""
        from yirifi_dq.config.category_manager import CategoryManager
        from yirifi_dq.tui.screens import OperationConfigScreen

        category_manager = CategoryManager()
        operation = category_manager.get_operation(operation_id)

        if operation:
            config_screen = OperationConfigScreen(operation)
            self.app.push_screen(config_screen)
        else:
            self.app.notify(f"Operation '{operation_id}' not found", severity="error")

    def _create_pipeline_operation(self) -> None:
        """Create a new pipeline operation."""
        from yirifi_dq.config.category_manager import CategoryManager

        category_manager = CategoryManager()
        pipeline_ops = category_manager.get_operations_by_category("pipeline_management")

        if pipeline_ops:
            # For now, launch the first pipeline operation
            self._create_operation(pipeline_ops[0].id)
        else:
            self.app.notify("No pipeline operations configured", severity="warning")

    def _switch_screen(self, screen_name: str) -> None:
        """Switch to a different screen."""
        # TODO: Implement screen switching
        self.app.notify(f"Switching to {screen_name} screen", severity="information")

    def _refresh_data(self) -> None:
        """Refresh dashboard data."""
        # Try to refresh the current screen if it has a refresh method
        if hasattr(self.app.screen, "_load_operations"):
            self.app.screen._load_operations()
        if hasattr(self.app.screen, "_update_stats"):
            self.app.screen._update_stats()
        self.app.notify("Data refreshed", severity="information")

    def _show_scripts(self) -> None:
        """Show the scripts browser."""
        from yirifi_dq.tui.screens.scripts_list_screen import ScriptsListScreen
        self.app.push_screen(ScriptsListScreen())

    def _launch_script(self, script) -> None:
        """Launch a script's parameter screen."""
        from yirifi_dq.tui.screens.script_parameters_screen import ScriptParametersScreen
        self.app.push_screen(ScriptParametersScreen(script))

    def _take_screenshot(self) -> None:
        """Take a screenshot and save to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.svg"

        try:
            # Textual's save_screenshot saves to the current directory
            self.app.save_screenshot(filename)
            self.app.notify(f"Screenshot saved: {filename}", severity="information")
        except Exception as e:
            self.app.notify(f"Screenshot failed: {e}", severity="error")

    def _toggle_theme(self) -> None:
        """Cycle through available themes."""
        # Built-in Textual themes (no registration required)
        themes = [
            "textual-dark",
            "textual-light",
            "nord",
            "gruvbox",
            "tokyo-night",
            "monokai",
            "dracula",
        ]

        # Find current theme index and cycle to next
        try:
            current_index = themes.index(self.app.theme)
            next_index = (current_index + 1) % len(themes)
        except ValueError:
            next_index = 0

        self.app.theme = themes[next_index]
        self.app.notify(f"Theme: {self.app.theme}", severity="information")

    def _clear_notifications(self) -> None:
        """Clear all notifications."""
        # Clear the notification area
        self.app.clear_notifications()
        self.app.notify("Notifications cleared", severity="information")

    def _export_operations(self) -> None:
        """Export operations history to JSON file."""
        import json
        from pathlib import Path

        try:
            from yirifi_dq.state.manager import StateManager

            state_manager = StateManager()
            operations = state_manager.list_operations(limit=1000)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/operations_export_{timestamp}.json"

            # Ensure output directory exists
            Path("output").mkdir(exist_ok=True)

            # Convert to dict for JSON serialization
            export_data = {
                "exported_at": timestamp,
                "total_operations": len(operations),
                "operations": [
                    {
                        "id": op.id,
                        "type": op.operation_type,
                        "database": op.database,
                        "collection": op.collection,
                        "status": op.status,
                        "created_at": str(op.created_at),
                        "records_affected": op.records_affected,
                    }
                    for op in operations
                ]
            }

            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)

            self.app.notify(f"Exported {len(operations)} operations to {filename}", severity="information")
        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")

    def _show_help(self) -> None:
        """Show help screen with keyboard shortcuts."""
        help_text = """
YIRIFI-DQ Power Terminal - Keyboard Shortcuts

Navigation:
  1          - Dashboard
  2          - Operations list
  3          - Logs viewer
  4          - Framework stats
  5          - Execute view
  6 / S      - Scripts browser

Quick Actions:
  D          - New duplicate cleanup
  O          - New orphan cleanup
  P          - New pipeline operation
  Ctrl+P     - Command palette

System:
  Ctrl+Shift+S  - Take screenshot
  Ctrl+T        - Toggle theme
  Ctrl+V        - Toggle view mode (in scripts)
  R             - Refresh data
  ?             - Show this help
  Q             - Quit

Scripts Browser:
  1/2/3     - Switch view modes (Cards/Tree/Tabs)
  C         - Clear filters
  /         - Search
        """
        self.app.notify(help_text, severity="information", timeout=30)

    def _open_docs(self) -> None:
        """Open documentation in web browser."""
        try:
            # Try to open local docs
            docs_path = "docs/README.md"
            webbrowser.open(f"file://{docs_path}")
            self.app.notify("Opening documentation...", severity="information")
        except Exception as e:
            self.app.notify(f"Could not open docs: {e}", severity="error")

    def _show_about(self) -> None:
        """Show version and system information."""
        import platform

        about_text = f"""
YIRIFI Data Quality CLI

Version: 2.0.0
Python: {platform.python_version()}
Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}

Framework for repeatable MongoDB data quality operations.
CLI + TUI for duplicate cleanup, orphan detection, and more.

GitHub: https://github.com/yirifi/yirifi-dq
        """
        self.app.notify(about_text, severity="information", timeout=20)
