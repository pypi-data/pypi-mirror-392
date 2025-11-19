"""
Category Selection Screen

Allows users to browse and select operation categories based on flexible
multi-dimensional organization (domain, workflow, functionality, data quality).
"""

import re
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ListItem, ListView, Static

from yirifi_dq.config import Category, CategoryManager


def sanitize_id(text: str) -> str:
    """
    Sanitize text for use as a Textual widget ID.

    IDs must contain only letters, numbers, underscores, or hyphens,
    and must not begin with a number.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized ID string
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with underscores
    text = text.replace(" ", "_")
    # Remove all characters except letters, numbers, underscores, and hyphens
    text = re.sub(r"[^a-z0-9_-]", "", text)
    # Ensure it doesn't start with a number
    if text and text[0].isdigit():
        text = f"id_{text}"
    return text


class CategoryScreen(Screen):
    """
    Category selection screen.

    Shows categorized groups of operations organized by:
    - Domain (which collections/data)
    - Workflow (what stage)
    - Functionality (what it does)
    - Data Quality Concern (what problem it solves)
    """

    BINDINGS = [
        Binding("enter", "select_category", "Select", key_display="↵"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
        Binding("/", "search", "Search", key_display="/"),
    ]

    CSS = """
    #category-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .category-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .category-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #category-list {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    .category-item {
        padding: 1 2;
        margin: 0;
    }

    .category-icon {
        color: $accent;
        padding-right: 1;
    }

    .category-name {
        text-style: bold;
        color: $text;
    }

    .category-description {
        color: $text-muted;
        margin-left: 4;
    }

    .category-count {
        color: $primary;
        margin-left: 1;
    }

    .quick-access {
        height: auto;
        border: solid $secondary;
        padding: 1;
        margin-bottom: 1;
    }

    .quick-access-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .button-group {
        height: 3;
        align: center middle;
    }
    """

    def __init__(self):
        super().__init__()
        self.category_manager = CategoryManager()
        self.selected_category: Optional[Category] = None

    def compose(self) -> ComposeResult:
        """Compose the category selection screen."""
        yield Header()

        with Container(id="category-container"):
            yield Static("📂 Select Operation Category", classes="category-title")
            yield Static("Choose a category to browse available operations", classes="category-subtitle")

            # Quick access section (if available)
            quick_access = self.category_manager.get_quick_access_groups()
            if quick_access:
                with Container(classes="quick-access"):
                    yield Static("⚡ Quick Access", classes="quick-access-title")
                    for group in quick_access:
                        yield Button(
                            f"  {group.name}",
                            id=f"quick-{sanitize_id(group.name)}",
                            variant="primary",
                        )

            # Category list
            yield self._build_category_list()

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")
                yield Button("Search Operations", id="search-btn", variant="primary")

        yield Footer()

    def _build_category_list(self) -> ListView:
        """Build the scrollable category list."""
        categories = self.category_manager.get_categories()
        operation_counts = self.category_manager.get_operation_count_by_category()

        # Build all list items first
        list_items = []

        for category in categories:
            op_count = operation_counts.get(category.id, 0)
            count_text = f"({op_count} operation{'s' if op_count != 1 else ''})"

            # Build rich text for category item
            item_text = Text()
            if category.icon:
                item_text.append(f"{category.icon}  ", style="bold cyan")
            item_text.append(category.name, style="bold white")
            item_text.append(f"  {count_text}", style="dim")
            item_text.append(f"\n    {category.description}", style="dim")

            list_items.append(ListItem(Static(item_text), id=f"cat-{category.id}", classes="category-item"))

        # Create ListView with all children at once
        return ListView(*list_items, id="category-list")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle category selection."""
        category_id = event.item.id.replace("cat-", "")
        category = self.category_manager.get_category(category_id)

        if category:
            self.selected_category = category
            self._navigate_to_operations(category)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-btn":
            self.app.pop_screen()

        elif button_id == "search-btn":
            self._show_search()

        elif button_id and button_id.startswith("quick-"):
            # Quick access button pressed
            self._handle_quick_access(button_id)

    def _navigate_to_operations(self, category: Category) -> None:
        """
        Navigate to operation list screen for selected category.

        Args:
            category: Selected category
        """
        from yirifi_dq.tui.screens.operation_list_screen import OperationListScreen

        # Store category in app's wizard data
        self.app.wizard_data["selected_category"] = category

        # Push operation list screen
        self.app.push_screen(OperationListScreen(category))

    def _show_search(self) -> None:
        """Show operation search screen."""
        # TODO: Implement search screen
        pass

    def _handle_quick_access(self, button_id: str) -> None:
        """
        Handle quick access button press.

        Args:
            button_id: Button ID
        """
        # TODO: Implement quick access handling
        pass

    def action_select_category(self) -> None:
        """Select highlighted category."""
        list_view = self.query_one("#category-list", ListView)
        if list_view.highlighted_child:
            list_view.action_select_cursor()

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_search(self) -> None:
        """Show search screen."""
        self._show_search()
