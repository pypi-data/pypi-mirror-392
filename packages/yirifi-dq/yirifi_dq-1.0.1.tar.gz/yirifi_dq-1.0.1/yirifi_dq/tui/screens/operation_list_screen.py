"""
Operation List Screen

Shows operations within a selected category and allows filtering/searching.
"""

from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from yirifi_dq.config import Category, CategoryManager, OperationDefinition


class OperationListScreen(Screen):
    """
    Operation list screen.

    Shows filtered list of operations within a category.
    Allows users to select an operation to configure and execute.
    """

    BINDINGS = [
        Binding("enter", "select_operation", "Select", key_display="↵"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
        Binding("/", "focus_search", "Search", key_display="/"),
    ]

    CSS = """
    #operation-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .operation-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .category-breadcrumb {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .search-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #search-input {
        width: 100%;
    }

    #operation-list {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    .operation-item {
        padding: 1 2;
    }

    .operation-name {
        text-style: bold;
        color: $text;
    }

    .operation-description {
        color: $text-muted;
        margin-left: 2;
    }

    .operation-tags {
        color: $primary;
        margin-left: 2;
    }

    .operation-requirements {
        color: $warning;
        margin-left: 2;
    }

    .auto-run-badge {
        color: $success;
        text-style: bold;
    }

    .empty-state {
        width: 100%;
        height: 100%;
        align: center middle;
        color: $text-muted;
    }

    .button-group {
        height: 3;
        align: center middle;
    }
    """

    def __init__(self, category: Category):
        super().__init__()
        self.category = category
        self.category_manager = CategoryManager()
        self.all_operations = self.category_manager.get_operations_by_category(category.id)
        self.filtered_operations = self.all_operations
        self.selected_operation: Optional[OperationDefinition] = None

    def compose(self) -> ComposeResult:
        """Compose the operation list screen."""
        yield Header()

        with Container(id="operation-container"):
            yield Static(f"📋 Operations: {self.category.name}", classes="operation-title")
            yield Static(f"{self.category.icon} {self.category.description}", classes="category-breadcrumb")

            # Search box
            with Container(classes="search-container"):
                yield Input(placeholder="Search operations...", id="search-input")

            # Operation list
            if self.all_operations:
                yield self._build_operation_list()
            else:
                yield Static(f"No operations found in {self.category.name} category", classes="empty-state")

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")

        yield Footer()

    def _build_operation_list(self) -> ListView:
        """Build the scrollable operation list."""
        # Build all list items first
        list_items = []

        for operation in self.filtered_operations:
            item_text = self._format_operation_item(operation)
            list_items.append(ListItem(Static(item_text), id=f"op-{operation.id}", classes="operation-item"))

        # Create ListView with all children at once
        return ListView(*list_items, id="operation-list")

    def _format_operation_item(self, operation: OperationDefinition) -> Text:
        """
        Format operation for display in list.

        Args:
            operation: Operation definition

        Returns:
            Rich Text object
        """
        text = Text()

        # Parent operation indicator
        if operation.is_parent:
            text.append("▸ ", style="bold cyan")

        # Operation name
        text.append(operation.name, style="bold white")

        # Auto-run badge
        if operation.auto_run:
            text.append("  [AUTO-RUN]", style="bold green")

        # Parent operation badge
        if operation.is_parent and operation.sub_operations:
            sub_count = len(operation.sub_operations)
            text.append(f"  [{sub_count} operations]", style="bold cyan")

        # Description
        text.append(f"\n  {operation.description}", style="dim")

        # Requirements
        requirements = []
        if operation.requires_collection:
            requirements.append("Collection")
        if operation.requires_field:
            requirements.append("Field")
        if operation.requires_environment:
            requirements.append("Environment")

        if requirements:
            text.append(f"\n  Requires: {', '.join(requirements)}", style="yellow")

        # Tags
        if operation.tags:
            tags_str = " ".join([f"#{tag}" for tag in operation.tags[:3]])
            text.append(f"\n  {tags_str}", style="cyan dim")

        return text

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle operation selection."""
        operation_id = event.item.id.replace("op-", "")
        operation = self.category_manager.get_operation(operation_id)

        if operation:
            self.selected_operation = operation
            self._navigate_to_config(operation)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            query = event.value.strip()
            self._filter_operations(query)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.app.pop_screen()

    def _filter_operations(self, query: str) -> None:
        """
        Filter operations by search query.

        Args:
            query: Search query
        """
        if not query:
            self.filtered_operations = self.all_operations
        else:
            query_lower = query.lower()
            self.filtered_operations = [
                op for op in self.all_operations if (query_lower in op.name.lower() or query_lower in op.description.lower() or any(query_lower in tag.lower() for tag in op.tags))
            ]

        # Rebuild list
        list_view = self.query_one("#operation-list", ListView)
        list_view.clear()

        for operation in self.filtered_operations:
            item_text = self._format_operation_item(operation)
            list_view.append(ListItem(Static(item_text), id=f"op-{operation.id}", classes="operation-item"))

    def _navigate_to_config(self, operation: OperationDefinition) -> None:
        """
        Navigate to operation configuration screen or submenu screen.

        Args:
            operation: Selected operation
        """
        # Store operation in app's wizard data
        self.app.wizard_data["selected_operation"] = operation

        # Check if this is a parent operation
        if operation.is_parent and operation.display_as_submenu:
            # Navigate to submenu screen to show sub-operations
            from yirifi_dq.tui.screens.suboperation_screen import SuboperationScreen

            submenu_screen = SuboperationScreen(
                category=self.category,
                parent_operation=operation,
                category_manager=self.category_manager,
            )
            self.app.push_screen(submenu_screen)
        else:
            # Navigate to operation configuration screen
            from yirifi_dq.tui.screens.operation_config_screen import OperationConfigScreen

            self.app.push_screen(OperationConfigScreen(operation))

    def action_select_operation(self) -> None:
        """Select highlighted operation."""
        list_view = self.query_one("#operation-list", ListView)
        if list_view.highlighted_child:
            list_view.action_select_cursor()

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
