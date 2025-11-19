"""
Scripts List Screen - Browse and select plugin scripts with multiple view modes.

This screen shows all available plugin scripts from the registry,
organized by domain/category with search and filter capabilities.
Supports multiple view modes: Card Grid, Tree, and Tabs+List.
"""

from enum import Enum
from typing import Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets.tree import TreeNode

from yirifi_dq.plugins.registry import get_registry
from yirifi_dq.plugins.models import ScriptConfig
from yirifi_dq.config import CategoryManager


class ViewMode(str, Enum):
    """Available view modes for script browsing."""
    CARD_GRID = "card_grid"
    TREE = "tree"
    TABS_LIST = "tabs_list"


class ScriptsListScreen(Screen):
    """
    Plugin scripts list screen with multiple view modes.

    Shows all available plugin scripts from the registry,
    allows filtering by domain/tag/category, and selection for execution.

    View Modes:
    - Card Grid: Category cards, click to filter (like CategoryScreen)
    - Tree: Collapsible Category -> Domain -> Scripts hierarchy
    - Tabs + List: Top tabs for categories, list below

    Keyboard Shortcuts:
    - Enter: Select script and configure parameters
    - Ctrl+V: Toggle view mode
    - /: Focus search box
    - ESC: Back to previous screen
    - Q: Quit
    """

    BINDINGS = [
        Binding("enter", "select_script", "Select", key_display="Enter"),
        Binding("escape", "back", "Back", key_display="ESC"),
        Binding("q", "quit", "Quit"),
        Binding("/", "focus_search", "Search", key_display="/"),
        Binding("ctrl+v", "toggle_view", "Toggle View", key_display="^V"),
        Binding("d", "filter_domain", "Filter Domain", key_display="D", show=False),
        Binding("t", "filter_tag", "Filter Tag", key_display="T", show=False),
        Binding("c", "clear_filters", "Clear Filters", key_display="C", show=False),
        Binding("1", "set_view_cards", "Card View", show=False),
        Binding("2", "set_view_tree", "Tree View", show=False),
        Binding("3", "set_view_tabs", "Tabs View", show=False),
    ]

    CSS = """
    #scripts-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    .scripts-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .scripts-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    .view-mode-bar {
        height: 3;
        align: center middle;
        margin-bottom: 1;
    }

    .view-mode-btn {
        margin: 0 1;
    }

    .view-mode-btn-active {
        background: $primary;
    }

    .filter-info {
        text-align: center;
        color: $primary;
        margin-bottom: 1;
    }

    .search-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #search-input {
        width: 100%;
    }

    /* Card Grid View Styles */
    .cards-grid {
        width: 100%;
        height: 1fr;
        grid-size: 2 4;
        grid-gutter: 1;
        padding: 1;
    }

    .category-card {
        width: 100%;
        height: auto;
        border: solid $primary;
        padding: 1;
        background: $surface;
    }

    .category-card:hover {
        border: solid $accent;
        background: $panel;
    }

    .category-card:focus {
        border: double $accent;
    }

    .card-icon {
        text-style: bold;
        color: $accent;
    }

    .card-name {
        text-style: bold;
        color: $text;
    }

    .card-count {
        color: $primary;
    }

    .card-description {
        color: $text-muted;
    }

    /* Tree View Styles */
    .scripts-tree {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    /* Tabs + List View Styles */
    .scripts-tabs {
        width: 100%;
        height: 1fr;
    }

    /* Common List Styles */
    .scripts-list {
        width: 100%;
        height: 1fr;
        border: solid $primary;
    }

    .script-item {
        padding: 1 2;
    }

    .script-header {
        text-style: bold;
        color: $text;
    }

    .script-id {
        color: $primary;
        margin-left: 2;
    }

    .script-description {
        color: $text-muted;
        margin-left: 2;
    }

    .script-meta {
        color: $accent;
        margin-left: 2;
    }

    .script-tags {
        color: $success;
        margin-left: 2;
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
        margin-top: 1;
    }
    """

    def __init__(
        self,
        domain_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ):
        """
        Initialize scripts list screen.

        Args:
            domain_filter: Filter scripts by domain (links, articles, etc.)
            tag_filter: Filter scripts by tag (duplicates, cleanup, etc.)
            category_filter: Filter scripts by category ID (data_quality, relationships, etc.)
        """
        super().__init__()
        self.registry = get_registry()
        self.category_manager = CategoryManager()
        self.domain_filter = domain_filter
        self.tag_filter = tag_filter
        self.category_filter = category_filter
        self.search_query = ""
        self.all_scripts = self.registry.list_scripts()
        self.filtered_scripts = self._apply_filters()
        self.selected_script: Optional[ScriptConfig] = None
        self.view_mode = ViewMode.CARD_GRID  # Default to card grid view

    def compose(self) -> ComposeResult:
        """Compose the scripts list screen."""
        yield Header()

        with Container(id="scripts-container"):
            # Title
            yield Static("📜 Plugin Scripts", classes="scripts-title")

            # Subtitle with count
            subtitle = f"Total: {len(self.all_scripts)} scripts"
            if len(self.filtered_scripts) != len(self.all_scripts):
                subtitle += f" (showing {len(self.filtered_scripts)})"
            yield Static(subtitle, classes="scripts-subtitle", id="scripts-subtitle")

            # View mode selector
            with Horizontal(classes="view-mode-bar"):
                yield Button(
                    "Cards",
                    id="view-cards-btn",
                    classes="view-mode-btn view-mode-btn-active" if self.view_mode == ViewMode.CARD_GRID else "view-mode-btn",
                    variant="primary" if self.view_mode == ViewMode.CARD_GRID else "default",
                )
                yield Button(
                    "Tree",
                    id="view-tree-btn",
                    classes="view-mode-btn view-mode-btn-active" if self.view_mode == ViewMode.TREE else "view-mode-btn",
                    variant="primary" if self.view_mode == ViewMode.TREE else "default",
                )
                yield Button(
                    "Tabs",
                    id="view-tabs-btn",
                    classes="view-mode-btn view-mode-btn-active" if self.view_mode == ViewMode.TABS_LIST else "view-mode-btn",
                    variant="primary" if self.view_mode == ViewMode.TABS_LIST else "default",
                )

            # Filter info
            if self.domain_filter or self.tag_filter or self.category_filter:
                filter_text = "Filters: "
                if self.category_filter:
                    filter_text += f"category={self.category_filter} "
                if self.domain_filter:
                    filter_text += f"domain={self.domain_filter} "
                if self.tag_filter:
                    filter_text += f"tag={self.tag_filter}"
                yield Static(filter_text, classes="filter-info", id="filter-info")

            # Search box
            with Container(classes="search-container"):
                yield Input(
                    placeholder="Search by name, ID, or description...",
                    id="search-input"
                )

            # Content area - will be replaced based on view mode
            yield Container(id="content-area")

            # Button group
            with Horizontal(classes="button-group"):
                yield Button("Back", id="back-btn", variant="default")
                if self.domain_filter or self.tag_filter or self.category_filter:
                    yield Button("Clear Filters", id="clear-filters-btn", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the view after mounting."""
        self._render_view()

    def _apply_filters(self) -> list[ScriptConfig]:
        """Apply domain/tag/category filters and search query."""
        scripts = self.all_scripts

        # Apply category filter
        if self.category_filter:
            scripts = [s for s in scripts if getattr(s, 'category', None) == self.category_filter]

        # Apply domain filter
        if self.domain_filter:
            scripts = [s for s in scripts if s.domain == self.domain_filter]

        # Apply tag filter
        if self.tag_filter:
            scripts = [s for s in scripts if self.tag_filter in s.tags]

        # Apply search query
        if self.search_query:
            query_lower = self.search_query.lower()
            scripts = [
                s for s in scripts
                if query_lower in s.name.lower()
                or query_lower in s.id.lower()
                or query_lower in s.description.lower()
            ]

        return sorted(scripts, key=lambda s: (s.domain, s.name))

    def _render_view(self) -> None:
        """Render the current view mode."""
        content_area = self.query_one("#content-area")
        content_area.remove_children()

        if self.view_mode == ViewMode.CARD_GRID:
            content_area.mount(self._build_card_grid_view())
        elif self.view_mode == ViewMode.TREE:
            content_area.mount(self._build_tree_view())
        elif self.view_mode == ViewMode.TABS_LIST:
            content_area.mount(self._build_tabs_list_view())

    def _build_card_grid_view(self) -> Container:
        """Build the card grid view showing categories."""
        categories = self.category_manager.get_categories()

        # Count scripts per category
        category_counts = {}
        for script in self.all_scripts:
            cat = getattr(script, 'category', 'uncategorized')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Build cards list
        cards = []
        for category in categories:
            count = category_counts.get(category.id, 0)
            if count == 0:
                continue  # Skip empty categories

            card_text = Text()
            if category.icon:
                card_text.append(f"{category.icon}  ", style="bold cyan")
            card_text.append(f"{category.name}\n", style="bold white")
            card_text.append(f"({count} scripts)\n", style="dim blue")
            card_text.append(f"{category.description[:50]}...", style="dim")

            card = Button(
                str(card_text),
                id=f"card-{category.id}",
                classes="category-card",
            )
            cards.append(card)

        # Create grid with all cards passed to constructor
        # Note: Don't use fixed ID to avoid duplicate ID errors when switching views
        return Grid(*cards, classes="cards-grid")

    def _build_tree_view(self) -> Tree:
        """Build the tree view showing Category -> Domain -> Scripts."""
        # Note: Don't use fixed ID to avoid duplicate ID errors when switching views
        tree = Tree("Scripts", classes="scripts-tree")
        tree.root.expand()

        # Group scripts by category, then by domain
        by_category: dict[str, dict[str, list[ScriptConfig]]] = {}

        for script in self.filtered_scripts:
            cat = getattr(script, 'category', 'uncategorized')
            domain = script.domain

            if cat not in by_category:
                by_category[cat] = {}
            if domain not in by_category[cat]:
                by_category[cat][domain] = []
            by_category[cat][domain].append(script)

        # Build tree structure
        categories = self.category_manager.get_categories()
        cat_lookup = {c.id: c for c in categories}

        for cat_id, domains in sorted(by_category.items()):
            cat_info = cat_lookup.get(cat_id)
            cat_label = f"{cat_info.icon} {cat_info.name}" if cat_info else cat_id
            cat_count = sum(len(scripts) for scripts in domains.values())
            cat_node = tree.root.add(f"{cat_label} ({cat_count})", expand=True)

            for domain, scripts in sorted(domains.items()):
                domain_node = cat_node.add(f"▶ {domain.upper()} ({len(scripts)})", expand=False)

                for script in scripts:
                    script_label = f"{script.name} [{script.id}]"
                    script_node = domain_node.add_leaf(script_label)
                    script_node.data = script  # Store script reference

        return tree

    def _build_tabs_list_view(self) -> TabbedContent:
        """Build the tabs + list view with category tabs."""
        categories = self.category_manager.get_categories()

        # Group scripts by category
        by_category: dict[str, list[ScriptConfig]] = {}
        for script in self.filtered_scripts:
            cat = getattr(script, 'category', 'uncategorized')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(script)

        # Note: Don't use fixed ID to avoid duplicate ID errors when switching views
        tabs = TabbedContent(classes="scripts-tabs")

        # Add "All" tab first
        all_pane = TabPane("All")
        all_pane.compose_add_child(self._build_scripts_list(self.filtered_scripts))
        tabs.compose_add_child(all_pane)

        # Add category tabs
        for category in categories:
            scripts = by_category.get(category.id, [])
            if not scripts:
                continue

            tab_label = f"{category.icon} {category.name}" if category.icon else category.name
            pane = TabPane(tab_label)
            pane.compose_add_child(self._build_scripts_list(scripts))
            tabs.compose_add_child(pane)

        return tabs

    def _build_scripts_list(self, scripts: list[ScriptConfig]) -> ListView:
        """Build a scrollable scripts list."""
        list_items = []

        if not scripts:
            no_scripts = Static("No scripts found", classes="empty-state")
            list_items.append(ListItem(no_scripts))
            # Note: Don't use fixed ID to avoid duplicate ID errors
            return ListView(*list_items, classes="scripts-list")

        # Group by domain for better organization
        current_domain = None

        for script in scripts:
            # Add domain header if new domain
            if script.domain != current_domain:
                current_domain = script.domain
                domain_header = Text()
                domain_header.append(f"\n▶ {current_domain.upper()}", style="bold cyan")
                list_items.append(ListItem(Static(domain_header)))

            # Add script item
            item_text = self._format_script_item(script)
            list_item = ListItem(Static(item_text), classes="script-item")
            list_item.script_config = script  # Store reference
            list_items.append(list_item)

        # Note: Don't use fixed ID to avoid duplicate ID errors
        return ListView(*list_items, classes="scripts-list")

    def _format_script_item(self, script: ScriptConfig) -> Text:
        """Format a script as rich text."""
        text = Text()

        # Script name and type
        text.append(f"{script.name}", style="bold white")
        text.append(f" [{script.script_type}]", style="cyan")
        text.append("\n")

        # Script ID
        text.append(f"  ID: ", style="dim")
        text.append(f"{script.id}", style="yellow")
        text.append("\n")

        # Description (truncated)
        desc = script.description.split("\n")[0][:80]
        if len(script.description) > 80:
            desc += "..."
        text.append(f"  {desc}", style="dim")
        text.append("\n")

        # Parameters count
        param_count = len(script.parameters)
        required_count = sum(1 for p in script.parameters if p.required)
        text.append(f"  Parameters: ", style="dim")
        text.append(f"{param_count} total, {required_count} required", style="blue")
        text.append(" | ")

        # Tags
        tags_str = ", ".join(script.tags[:3])
        if len(script.tags) > 3:
            tags_str += f" +{len(script.tags) - 3}"
        text.append(f"Tags: {tags_str}", style="green")

        return text

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value
            self.filtered_scripts = self._apply_filters()
            self._render_view()
            self._update_subtitle()

    def _update_subtitle(self) -> None:
        """Update the subtitle with current count."""
        subtitle = self.query_one("#scripts-subtitle", Static)
        text = f"Total: {len(self.all_scripts)} scripts"
        if len(self.filtered_scripts) != len(self.all_scripts):
            text += f" (showing {len(self.filtered_scripts)})"
        subtitle.update(text)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle script selection from list."""
        if hasattr(event.item, "script_config"):
            self.selected_script = event.item.script_config
            self.action_select_script()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle script selection from tree."""
        if event.node.data and isinstance(event.node.data, ScriptConfig):
            self.selected_script = event.node.data
            self.action_select_script()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-btn":
            self.action_back()
        elif button_id == "clear-filters-btn":
            self.action_clear_filters()
        elif button_id == "view-cards-btn":
            self.action_set_view_cards()
        elif button_id == "view-tree-btn":
            self.action_set_view_tree()
        elif button_id == "view-tabs-btn":
            self.action_set_view_tabs()
        elif button_id and button_id.startswith("card-"):
            # Category card clicked - filter by category
            category_id = button_id.replace("card-", "")
            self.category_filter = category_id
            self.filtered_scripts = self._apply_filters()
            self.view_mode = ViewMode.TREE  # Switch to tree to show filtered scripts
            self._render_view()
            self._update_subtitle()
            self._update_filter_info()

    def _update_filter_info(self) -> None:
        """Update or create the filter info display."""
        try:
            filter_info = self.query_one("#filter-info", Static)
            if self.domain_filter or self.tag_filter or self.category_filter:
                filter_text = "Filters: "
                if self.category_filter:
                    filter_text += f"category={self.category_filter} "
                if self.domain_filter:
                    filter_text += f"domain={self.domain_filter} "
                if self.tag_filter:
                    filter_text += f"tag={self.tag_filter}"
                filter_info.update(filter_text)
            else:
                filter_info.update("")
        except Exception:
            pass  # Filter info widget doesn't exist yet

    def action_select_script(self) -> None:
        """Select a script and go to parameters screen."""
        if self.selected_script:
            from yirifi_dq.tui.screens.script_parameters_screen import ScriptParametersScreen
            self.app.push_screen(ScriptParametersScreen(self.selected_script))
        else:
            self.notify("Please select a script first", severity="warning")

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_toggle_view(self) -> None:
        """Toggle through view modes."""
        modes = list(ViewMode)
        current_index = modes.index(self.view_mode)
        next_index = (current_index + 1) % len(modes)
        self.view_mode = modes[next_index]
        self._render_view()
        self._update_view_buttons()
        self.notify(f"View: {self.view_mode.value.replace('_', ' ').title()}", severity="information")

    def action_set_view_cards(self) -> None:
        """Set view mode to card grid."""
        self.view_mode = ViewMode.CARD_GRID
        self._render_view()
        self._update_view_buttons()

    def action_set_view_tree(self) -> None:
        """Set view mode to tree."""
        self.view_mode = ViewMode.TREE
        self._render_view()
        self._update_view_buttons()

    def action_set_view_tabs(self) -> None:
        """Set view mode to tabs + list."""
        self.view_mode = ViewMode.TABS_LIST
        self._render_view()
        self._update_view_buttons()

    def _update_view_buttons(self) -> None:
        """Update view mode button styles."""
        for mode in ViewMode:
            btn_id = f"view-{mode.value.split('_')[0]}-btn"
            try:
                btn = self.query_one(f"#{btn_id}", Button)
                if mode == self.view_mode:
                    btn.variant = "primary"
                    btn.add_class("view-mode-btn-active")
                else:
                    btn.variant = "default"
                    btn.remove_class("view-mode-btn-active")
            except Exception:
                pass

    def action_filter_domain(self) -> None:
        """Filter by domain (interactive prompt)."""
        self.notify("Domain filter: Press 1-5 for domain", severity="information")
        # TODO: Show domain selection modal

    def action_filter_tag(self) -> None:
        """Filter by tag (interactive prompt)."""
        self.notify("Tag filter: Type tag name", severity="information")
        # TODO: Show tag selection modal

    def action_clear_filters(self) -> None:
        """Clear all filters and show all scripts."""
        self.domain_filter = None
        self.tag_filter = None
        self.category_filter = None
        self.search_query = ""
        self.query_one("#search-input", Input).value = ""
        self.filtered_scripts = self._apply_filters()
        self._render_view()
        self._update_subtitle()
        self._update_filter_info()
        self.notify("Filters cleared", severity="information")
