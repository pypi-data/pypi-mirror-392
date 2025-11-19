"""
Main TUI Application Router

Routes between Bloomberg-style dashboard and classic wizard modes.

Usage:
    yirifi-dq tui              # Launch Bloomberg dashboard (default)
    yirifi-dq tui --wizard     # Launch classic wizard
    yirifi-dq tui --dashboard  # Explicitly launch dashboard
"""

from textual.app import App
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Container, Vertical

from yirifi_dq.tui.screens.dashboard_screen import DashboardScreen
from yirifi_dq.tui.widgets.command_palette import CommandPalette


class EnvironmentSelectionScreen(ModalScreen):
    """Modal screen for selecting environment on startup."""

    DEFAULT_CSS = """
    EnvironmentSelectionScreen {
        align: center middle;
    }

    EnvironmentSelectionScreen > Container {
        width: 60;
        height: auto;
        border: solid green;
        background: $surface;
        padding: 2;
    }

    EnvironmentSelectionScreen > Container > Static {
        text-align: center;
        margin-bottom: 1;
    }

    EnvironmentSelectionScreen .env-button {
        width: 100%;
        margin: 1;
    }
    """

    def compose(self):
        with Container():
            yield Static("[bold cyan]Select Environment[/bold cyan]")
            yield Static("This will be used as the default for this session")
            yield Static("")
            with Vertical():
                yield Button("DEV - Development", id="dev", classes="env-button")
                yield Button("UAT - User Acceptance", id="uat", classes="env-button")
                yield Button("PRD - Production", id="prd", classes="env-button", variant="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        env = event.button.id.upper()
        self.dismiss(env)


class PowerTerminalApp(App):
    """
    Bloomberg-style Power Terminal for MongoDB Data Quality Operations.

    Features:
    - Multi-pane dashboard with live updates
    - Command palette (Ctrl+P) for fuzzy search
    - Keyboard-first navigation (vim bindings)
    - Real-time operation monitoring
    - Professional Bloomberg theme

    Global Keyboard Shortcuts:
    - 1: Dashboard (default view)
    - 2: Operations list
    - 3: Logs view
    - 4: Stats view
    - 5: Execute view
    - 6: Scripts (plugin scripts)
    - Ctrl+P: Command palette
    - D: New duplicate cleanup
    - O: New orphan cleanup
    - P: New pipeline operation
    - S: Browse plugin scripts
    - /: Search
    - ?: Help
    - Q: Quit
    """

    TITLE = "YIRIFI-DQ Power Terminal"
    SUB_TITLE = "MongoDB Data Quality Operations"

    # Session state
    current_env: str = "DEV"  # Default environment

    BINDINGS = [
        # Screen navigation
        Binding("1", "show_dashboard", "Dashboard", key_display="1"),
        Binding("2", "show_operations", "Operations", key_display="2"),
        Binding("3", "show_logs", "Logs", key_display="3"),
        Binding("4", "show_stats", "Stats", key_display="4"),
        Binding("5", "show_execute", "Execute", key_display="5"),
        Binding("6", "show_scripts", "Scripts", key_display="6"),
        # Quick actions
        Binding("ctrl+p", "command_palette", "Command", key_display="^P"),
        Binding("d", "new_duplicate_cleanup", "Duplicates", key_display="D", show=False),
        Binding("o", "new_orphan_cleanup", "Orphans", key_display="O", show=False),
        Binding("p", "new_pipeline", "Pipeline", key_display="P", show=False),
        Binding("s", "show_scripts", "Scripts", key_display="S", show=False),
        # System features
        Binding("ctrl+shift+s", "screenshot", "Screenshot", key_display="^S", show=False),
        Binding("ctrl+t", "toggle_theme", "Theme", key_display="^T", show=False),
        Binding("/", "search", "Search", key_display="/", show=False),
        Binding("?", "help", "Help", key_display="?"),
        Binding("r", "refresh", "Refresh", key_display="R", show=False),
        Binding("q", "quit", "Quit", key_display="Q"),
    ]

    def on_mount(self) -> None:
        """Initialize app and show environment selection, then dashboard."""
        # Show environment selection first, then dashboard
        self.push_screen(EnvironmentSelectionScreen(), callback=self._on_env_selected)

    def _on_env_selected(self, env: str) -> None:
        """Called when environment is selected."""
        self.current_env = env
        self.sub_title = f"Environment: {env}"
        # Show dashboard as main screen (preserves all existing navigation)
        self.push_screen(DashboardScreen())

    def action_show_dashboard(self) -> None:
        """Show dashboard screen."""
        # Pop all screens and push dashboard
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.push_screen(DashboardScreen())

    def action_show_operations(self) -> None:
        """Show operations list screen."""
        self.notify("Operations list screen coming soon!", severity="information")
        # TODO: Implement OperationsListScreen

    def action_show_logs(self) -> None:
        """Show logs screen."""
        self.notify("Logs screen coming soon!", severity="information")
        # TODO: Implement LogsScreen

    def action_show_stats(self) -> None:
        """Show stats screen."""
        self.notify("Stats screen coming soon!", severity="information")
        # TODO: Implement StatsScreen

    def action_show_execute(self) -> None:
        """Show execute screen."""
        self.notify("Execute screen coming soon!", severity="information")
        # TODO: Implement ExecuteScreen

    def action_show_scripts(self) -> None:
        """Show plugin scripts browser."""
        from yirifi_dq.tui.screens.scripts_list_screen import ScriptsListScreen

        self.push_screen(ScriptsListScreen())

    def action_command_palette(self) -> None:
        """Open command palette for fuzzy search."""
        self.push_screen(CommandPalette())

    def action_new_duplicate_cleanup(self) -> None:
        """Quick action: New duplicate cleanup."""
        self._launch_operation_wizard("duplicate_cleanup")

    def action_new_orphan_cleanup(self) -> None:
        """Quick action: New orphan cleanup."""
        self._launch_operation_wizard("orphan_cleanup")

    def action_new_pipeline(self) -> None:
        """Quick action: New pipeline operation."""
        from yirifi_dq.config.category_manager import CategoryManager

        category_manager = CategoryManager()
        pipeline_ops = category_manager.get_operations_by_category("pipeline_management")

        if pipeline_ops:
            self._launch_operation_wizard(pipeline_ops[0].id)
        else:
            self.notify("No pipeline operations configured", severity="warning")

    def _launch_operation_wizard(self, operation_id: str) -> None:
        """Launch operation configuration wizard for given operation ID."""
        from yirifi_dq.config.category_manager import CategoryManager
        from yirifi_dq.tui.screens import OperationConfigScreen

        category_manager = CategoryManager()
        operation = category_manager.get_operation(operation_id)

        if operation:
            config_screen = OperationConfigScreen(operation)
            self.push_screen(config_screen, callback=self._on_wizard_dismissed)
        else:
            self.notify(f"Operation '{operation_id}' not found", severity="error")

    def _on_wizard_dismissed(self, _result=None) -> None:
        """Called when wizard is dismissed - refresh dashboard if active."""
        # Try to refresh the dashboard if it's the current screen
        if hasattr(self.screen, "_load_operations"):
            self.screen._load_operations()
        if hasattr(self.screen, "_update_stats"):
            self.screen._update_stats()

    def action_search(self) -> None:
        """Open search modal."""
        # Delegate to command palette
        self.action_command_palette()

    def action_help(self) -> None:
        """Show help screen."""
        help_text = """
YIRIFI-DQ Power Terminal - Keyboard Shortcuts

Navigation:
  1          - Dashboard (overview)
  2          - Operations list
  3          - Logs viewer
  4          - Framework stats
  5          - Execute operations
  6 or S     - Plugin scripts browser

Quick Actions:
  D          - New duplicate cleanup
  O          - New orphan cleanup
  P          - New pipeline operation
  Ctrl+P     - Command palette (fuzzy search)
  /          - Search

Dashboard (vim-style):
  j          - Move cursor down
  k          - Move cursor up
  Enter      - Select operation / View details
  R          - Refresh data

System:
  ?          - Show this help
  Q          - Quit application
  Esc        - Go back / Cancel
        """
        self.notify(help_text, severity="information", timeout=30)

    def action_refresh(self) -> None:
        """Refresh current screen data."""
        # Try to refresh the current screen if it has a refresh method
        if hasattr(self.screen, "action_refresh"):
            self.screen.action_refresh()
        else:
            self.notify("Data refreshed", severity="information")

    def action_screenshot(self) -> None:
        """Take a screenshot and save to file."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.svg"

        try:
            self.save_screenshot(filename)
            self.notify(f"Screenshot saved: {filename}", severity="information")
        except Exception as e:
            self.notify(f"Screenshot failed: {e}", severity="error")

    def action_toggle_theme(self) -> None:
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
            current_index = themes.index(self.theme)
            next_index = (current_index + 1) % len(themes)
        except ValueError:
            next_index = 0

        self.theme = themes[next_index]
        self.notify(f"Theme: {self.theme}", severity="information")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def run_terminal(mode: str = "dashboard") -> None:
    """
    Run the TUI in specified mode.

    Args:
        mode: Either "dashboard" (Bloomberg-style) or "wizard" (classic)
    """
    if mode == "wizard":
        # Import and run classic wizard
        from yirifi_dq.tui.wizard import WizardApp

        app = WizardApp()
    else:
        # Run Bloomberg-style power terminal (default)
        app = PowerTerminalApp()

    app.run()


if __name__ == "__main__":
    # Default to dashboard mode
    run_terminal("dashboard")
