"""
Suboperation Screen

Shows sub-operations of a parent operation and allows selection.
"""

from typing import List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem, ListView, Static

from yirifi_dq.config import Category, CategoryManager, OperationDefinition


class SuboperationScreen(Screen):
    """
    Suboperation screen.

    Shows list of sub-operations for a selected parent operation.
    Allows users to select a sub-operation to configure and execute.
    """

    BINDINGS = [
        Binding("enter", "select_suboperation", "Select", key_display="↵"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    #subop-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .subop-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .breadcrumb {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #subop-list {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    .subop-item {
        padding: 1 2;
    }

    .subop-number {
        text-style: bold;
        color: $primary;
    }

    .subop-name {
        text-style: bold;
        color: $text;
        margin-left: 1;
    }

    .subop-description {
        color: $text-muted;
        margin-left: 4;
        margin-top: 1;
    }

    .empty-state {
        width: 100%;
        height: 100%;
        align: center middle;
        text-align: center;
        color: $text-muted;
    }

    .instructions {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        category: Category,
        parent_operation: OperationDefinition,
        category_manager: CategoryManager,
        **kwargs,
    ):
        """
        Initialize suboperation screen.

        Args:
            category: Category containing the parent operation
            parent_operation: Parent operation
            category_manager: CategoryManager instance
        """
        super().__init__(**kwargs)
        self.category = category
        self.parent_operation = parent_operation
        self.category_manager = category_manager
        self.sub_operations: List[OperationDefinition] = []
        self.selected_subop: Optional[OperationDefinition] = None

    def compose(self) -> ComposeResult:
        """Compose screen widgets."""
        yield Header()

        with Container(id="subop-container"):
            # Title
            title_text = Text(self.parent_operation.name, style="bold cyan")
            yield Static(title_text, classes="subop-title")

            # Breadcrumb navigation
            breadcrumb = Text()
            breadcrumb.append(self.category.name, style="dim")
            breadcrumb.append(" > ", style="dim")
            breadcrumb.append(self.parent_operation.name, style="cyan")
            yield Static(breadcrumb, classes="breadcrumb")

            # Instructions
            inst_text = Text("Select a reset operation to configure:", style="dim italic")
            yield Static(inst_text, classes="instructions")

            # Suboperation list
            yield ListView(id="subop-list")

        yield Footer()

    def on_mount(self) -> None:
        """Load and display sub-operations when screen mounts."""
        self.load_sub_operations()

    def load_sub_operations(self) -> None:
        """Load sub-operations from category manager."""
        self.sub_operations = self.category_manager.get_sub_operations(self.parent_operation.id)

        list_view = self.query_one("#subop-list", ListView)

        if not self.sub_operations:
            # No sub-operations found
            empty_text = Text("No sub-operations found.", style="dim")
            list_view.append(ListItem(Static(empty_text)))
            return

        # Add sub-operations to list
        for idx, sub_op in enumerate(self.sub_operations, start=1):
            Vertical(classes="subop-item")

            # Build the list item content
            content = Text()
            content.append(f"[{idx}]", style="bold cyan")
            content.append(f" {sub_op.name}", style="bold")

            # Description on next line with indentation
            desc_line = Text()
            desc_line.append(f"    └─ {sub_op.description}", style="dim")

            list_item = ListItem(Static(content), Static(desc_line))
            list_view.append(list_item)

    def action_select_suboperation(self) -> None:
        """Handle sub-operation selection (keyboard)."""
        list_view = self.query_one("#subop-list", ListView)

        if list_view.index is not None and list_view.index < len(self.sub_operations):
            self.selected_subop = self.sub_operations[list_view.index]

            # Navigate to operation configuration screen
            from yirifi_dq.tui.screens.operation_config_screen import OperationConfigScreen

            config_screen = OperationConfigScreen(operation=self.selected_subop)
            self.app.push_screen(config_screen)

    def on_list_view_selected(self, _event: ListView.Selected) -> None:
        """Handle sub-operation selection (mouse click)."""
        list_view = self.query_one("#subop-list", ListView)

        if list_view.index is not None and list_view.index < len(self.sub_operations):
            self.selected_subop = self.sub_operations[list_view.index]

            # Navigate to operation configuration screen
            from yirifi_dq.tui.screens.operation_config_screen import OperationConfigScreen

            config_screen = OperationConfigScreen(operation=self.selected_subop)
            self.app.push_screen(config_screen)

    def action_back(self) -> None:
        """Go back to operation list."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
