"""
Interactive TUI Wizard for Data Quality Operations

Built with Textual framework for a modern terminal UI experience.
Guides users through creating operations step-by-step.
"""

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    RadioButton,
    RadioSet,
    Static,
)

from yirifi_dq.engine.safety import check_mongodb_connection, get_collection_stats
from yirifi_dq.models.operation import Environment, KeepStrategy
from yirifi_dq.tui.screens import CategoryScreen


class WizardApp(App):
    """
    Main TUI Wizard Application

    New Navigation Flow (Functionality-First):
    1. Welcome Screen
    2. Environment Selection
    3. Category Selection (browse by domain/workflow/functionality)
    4. Operation List (filtered by category)
    5. Operation Configuration (context-aware, skips unnecessary steps)
    6. Preview/Confirmation
    7. Execution Screen
    8. Results Screen
    """

    CSS = """
    Screen {
        align: center middle;
    }

    #wizard-container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }

    .title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .section {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .input-group {
        margin: 1 0;
    }

    .input-label {
        margin-bottom: 1;
        color: $text;
    }

    .button-group {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .warning {
        background: $warning;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .success {
        background: $success;
        color: $text;
        padding: 1;
        margin: 1 0;
    }

    .error {
        background: $error;
        color: $text;
        padding: 1;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.wizard_data = {}

    def on_mount(self) -> None:
        """Initialize app on mount"""
        self.title = "Yirifi Data Quality Wizard"
        self.sub_title = "Interactive Operation Creator"
        self.push_screen(WelcomeScreen())

    def action_back(self) -> None:
        """Go back to previous screen"""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


class WelcomeScreen(Screen):
    """Welcome screen with operation overview"""

    BINDINGS = [
        Binding("enter", "continue", "Continue", priority=True),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("🧙 Welcome to Data Quality Wizard", classes="title")
            yield Static(
                """
This wizard will guide you through creating a data quality operation.

Operation Categories:
  🧹 Data Quality & Cleanup  - Duplicates, inconsistencies, data quality issues
  🔗 Relationship Management - Foreign keys, orphans, referential integrity
  🚀 Data Migration          - Field migrations, data transformations
  🔍 Discovery & Analysis    - Data analysis, pattern discovery, reporting
  ⚙️  Framework Management    - Verify operations, generate statistics

New Functionality-First Flow:
  1. Browse operations by category (domain, workflow, functionality)
  2. Smart configuration (only asks what's needed)
  3. Auto-run operations skip unnecessary steps

Safety Features:
  ✓ Auto-backup before destructive operations
  ✓ Auto-verification after execution
  ✓ Test mode (limited records) by default
  ✓ Rollback capability from backups

Press Enter to continue or Q to quit
            """,
                classes="section",
            )
        yield Footer()

    def action_continue(self) -> None:
        """Move to environment selection"""
        self.app.push_screen(EnvironmentScreen())

    def action_quit(self) -> None:
        """Quit the wizard"""
        self.app.exit()


class EnvironmentScreen(Screen):
    """Select MongoDB environment"""

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("⚙️  Select Environment", classes="title")

            with Vertical(classes="section"):
                yield Static("MongoDB Environment:", classes="section-title")
                yield Static("Choose which MongoDB instance to connect to:", classes="input-label")

                with RadioSet(id="environment-select"):
                    yield RadioButton("DEV - Development (Recommended for testing)", id="env-dev", value=True)
                    yield RadioButton("UAT - User Acceptance Testing", id="env-uat")
                    yield RadioButton("PRD - Production (Use with caution!)", id="env-prd")

            with Vertical(classes="section"):
                yield Static("Test Mode:", classes="section-title")
                with RadioSet(id="test-mode-select"):
                    yield RadioButton("Test Mode ON - Limit to 10 records (Recommended)", id="test-on", value=True)
                    yield RadioButton("Test Mode OFF - Process all matching records", id="test-off")

            yield Static("", id="connection-status")

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Check Connection & Continue", variant="primary", id="continue-btn")
        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    async def on_continue(self) -> None:
        """Check MongoDB connection and continue"""
        # Get selected environment
        env_radio = self.query_one("#environment-select", RadioSet)
        env_value = env_radio.pressed_button.id if env_radio.pressed_button else "env-dev"
        env = env_value.replace("env-", "").upper()

        # Get test mode
        test_radio = self.query_one("#test-mode-select", RadioSet)
        test_value = test_radio.pressed_button.id if test_radio.pressed_button else "test-on"
        test_mode = test_value == "test-on"

        # Store selections
        self.app.wizard_data["environment"] = env
        self.app.wizard_data["test_mode"] = test_mode

        # Check connection
        status = self.query_one("#connection-status", Static)
        status.update("⏳ Checking MongoDB connection...")

        if check_mongodb_connection(env):
            status.update("✓ Connected to MongoDB successfully!")
            status.set_classes("success")
            await self.app.push_screen(CategoryScreen())
        else:
            status.update("✗ Failed to connect to MongoDB. Check your .env file.")
            status.set_classes("error")

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class DatabaseSelectionScreen(Screen):
    """Select database and collection"""

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("📊 Select Database & Collection", classes="title")

            with Vertical(classes="section"):
                yield Static("Database Name:", classes="input-label")
                yield Input(placeholder="e.g., regdb", id="database-input")

                yield Static("Collection Name:", classes="input-label")
                yield Input(placeholder="e.g., links", id="collection-input")

            yield Static("", id="collection-stats")

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Fetch Stats & Continue", variant="primary", id="continue-btn")
        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    async def on_continue(self) -> None:
        """Validate database/collection and fetch stats"""
        database = self.query_one("#database-input", Input).value
        collection = self.query_one("#collection-input", Input).value

        if not database or not collection:
            stats = self.query_one("#collection-stats", Static)
            stats.update("Please enter both database and collection name")
            stats.set_classes("error")
            return

        # Store selections
        self.app.wizard_data["database"] = database
        self.app.wizard_data["collection"] = collection

        # Fetch stats
        stats = self.query_one("#collection-stats", Static)
        stats.update("⏳ Fetching collection statistics...")

        env = self.app.wizard_data["environment"]
        collection_stats = get_collection_stats(database, collection, env)

        if collection_stats:
            self.app.wizard_data["collection_stats"] = collection_stats
            stats.update(f"✓ Collection found: {collection_stats['total_documents']:,} documents")
            stats.set_classes("success")
            await self.app.push_screen(OperationTypeScreen())
        else:
            stats.update("✗ Collection not found or error fetching stats")
            stats.set_classes("error")

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class OperationTypeScreen(Screen):
    """Select operation type"""

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("🔧 Select Operation Type", classes="title")

            with Vertical(classes="section"):
                yield Static("What operation do you want to perform?", classes="section-title")

                with RadioSet(id="operation-type-select"):
                    yield RadioButton(
                        "Duplicate Cleanup - Remove duplicate records by field",
                        id="op-duplicate-cleanup",
                        value=True,
                    )
                    yield RadioButton(
                        "Orphan Cleanup - Remove orphaned foreign key records",
                        id="op-orphan-cleanup",
                    )
                    yield RadioButton(
                        "Data Normalization - Normalize URLs, text, case (Coming Soon)",
                        id="op-normalization",
                        disabled=True,
                    )
                    yield RadioButton(
                        "Field Migration - Migrate data between fields (Coming Soon)",
                        id="op-migration",
                        disabled=True,
                    )

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Continue", variant="primary", id="continue-btn")
        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    async def on_continue(self) -> None:
        """Store operation type and move to configuration"""
        op_radio = self.query_one("#operation-type-select", RadioSet)
        op_value = op_radio.pressed_button.id if op_radio.pressed_button else "op-duplicate-cleanup"

        operation_type = op_value.replace("op-", "")
        self.app.wizard_data["operation_type"] = operation_type

        # Navigate to appropriate configuration screen
        if operation_type == "duplicate-cleanup":
            await self.app.push_screen(DuplicateConfigScreen())
        elif operation_type == "orphan-cleanup":
            await self.app.push_screen(OrphanConfigScreen())

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class DuplicateConfigScreen(Screen):
    """Configuration for duplicate cleanup"""

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("⚙️  Duplicate Cleanup Configuration", classes="title")

            with Vertical(classes="section"):
                yield Static("Field to Check for Duplicates:", classes="input-label")
                yield Input(placeholder="e.g., url, email, slug", id="field-input")

                yield Static("\nWhich duplicate record to keep?", classes="section-title")
                with RadioSet(id="keep-strategy-select"):
                    yield RadioButton("Oldest - Keep the oldest record (by _id)", id="keep-oldest", value=True)
                    yield RadioButton("Newest - Keep the newest record", id="keep-newest")
                    yield RadioButton("Most Complete - Keep record with most non-null fields", id="keep-complete")

                with Vertical(classes="section"):
                    yield Static("⚠️  Warning", classes="section-title")
                    yield Static(
                        "This operation will DELETE duplicate records.\nBackups are created automatically before deletion.",
                        classes="warning",
                    )

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Preview Configuration", variant="primary", id="continue-btn")
        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    async def on_continue(self) -> None:
        """Store configuration and move to preview"""
        field = self.query_one("#field-input", Input).value

        if not field:
            # Could add validation message
            return

        keep_radio = self.query_one("#keep-strategy-select", RadioSet)
        keep_value = keep_radio.pressed_button.id if keep_radio.pressed_button else "keep-oldest"

        strategy_map = {
            "keep-oldest": "oldest",
            "keep-newest": "newest",
            "keep-complete": "most_complete",
        }

        self.app.wizard_data["field"] = field
        self.app.wizard_data["keep_strategy"] = strategy_map[keep_value]

        await self.app.push_screen(PreviewScreen())

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class OrphanConfigScreen(Screen):
    """Configuration for orphan cleanup"""

    BINDINGS = [
        Binding("enter", "continue", "Continue"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("⚙️  Orphan Cleanup Configuration", classes="title")

            with Vertical(classes="section"):
                yield Static("Foreign Key Field:", classes="input-label")
                yield Static("Field in current collection that references parent", classes="input-label")
                yield Input(placeholder="e.g., articleYid, link_id", id="foreign-key-input")

                yield Static("\nParent Collection:", classes="input-label")
                yield Static("Collection that contains the parent records", classes="input-label")
                yield Input(placeholder="e.g., links", id="parent-collection-input")

                yield Static("\nParent Key Field:", classes="input-label")
                yield Input(placeholder="Default: _id", value="_id", id="parent-key-input")

                with Vertical(classes="section"):
                    yield Static("⚠️  Warning", classes="section-title")
                    yield Static(
                        "This operation will DELETE orphaned records.\nBackups are created automatically before deletion.",
                        classes="warning",
                    )

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Preview Configuration", variant="primary", id="continue-btn")
        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    async def on_continue(self) -> None:
        """Store configuration and move to preview"""
        foreign_key = self.query_one("#foreign-key-input", Input).value
        parent_collection = self.query_one("#parent-collection-input", Input).value
        parent_key = self.query_one("#parent-key-input", Input).value or "_id"

        if not foreign_key or not parent_collection:
            return

        self.app.wizard_data["foreign_key_field"] = foreign_key
        self.app.wizard_data["parent_collection"] = parent_collection
        self.app.wizard_data["parent_key_field"] = parent_key

        await self.app.push_screen(PreviewScreen())

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class PreviewScreen(Screen):
    """Preview and confirm configuration"""

    BINDINGS = [
        Binding("enter", "execute", "Execute"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("📋 Preview & Confirm", classes="title")

            yield Static(self._build_preview(), id="preview-content", classes="section")

            with Vertical(classes="section"):
                yield Static("Ready to Execute?", classes="section-title")
                yield Static(
                    "✓ Auto-backup will be created before any changes\n✓ Auto-verification will run after execution\n✓ You can rollback using the backup if needed",
                    classes="success",
                )

            with Horizontal(classes="button-group"):
                yield Button("Back", variant="default", id="back-btn")
                yield Button("Execute Operation", variant="success", id="execute-btn")
        yield Footer()

    def _build_preview(self) -> str:
        """Build preview text from wizard data"""
        data = self.app.wizard_data

        preview = f"""
Operation Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type:           {data["operation_type"]}
Database:       {data["database"]}
Collection:     {data["collection"]}
Environment:    {data["environment"]}
Test Mode:      {"ON (10 records max)" if data["test_mode"] else "OFF (all records)"}
"""

        if data["operation_type"] == "duplicate-cleanup":
            preview += f"""
Field:          {data["field"]}
Keep Strategy:  {data["keep_strategy"]}
"""
        elif data["operation_type"] == "orphan-cleanup":
            preview += f"""
Foreign Key:    {data["foreign_key_field"]}
Parent Coll:    {data["parent_collection"]}
Parent Key:     {data["parent_key_field"]}
"""

        if "collection_stats" in data:
            preview += f"""
Total Records:  {data["collection_stats"]["total_documents"]:,}
"""

        return preview

    @on(Button.Pressed, "#execute-btn")
    async def on_execute(self) -> None:
        """Execute the operation"""
        await self.app.push_screen(ExecutionScreen())

    @on(Button.Pressed, "#back-btn")
    def on_back(self) -> None:
        self.app.pop_screen()


class ExecutionScreen(Screen):
    """Execute operation and show progress"""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("⚡ Executing Operation", classes="title")

            yield Static("", id="execution-status", classes="section")
            yield Static("", id="execution-log")

            with Horizontal(classes="button-group"):
                yield Button("View Results", variant="primary", id="results-btn", disabled=True)
        yield Footer()

    async def on_mount(self) -> None:
        """Execute operation when screen mounts"""
        from yirifi_dq.engine.orchestrator import OperationOrchestrator
        from yirifi_dq.models.operation import DuplicateCleanupConfig, OrphanCleanupConfig

        data = self.app.wizard_data
        status = self.query_one("#execution-status", Static)
        log = self.query_one("#execution-log", Static)

        try:
            # Create configuration
            status.update("Creating operation configuration...")

            if data["operation_type"] == "duplicate-cleanup":
                config = DuplicateCleanupConfig(
                    database=data["database"],
                    collection=data["collection"],
                    field=data["field"],
                    environment=Environment(data["environment"]),
                    test_mode=data["test_mode"],
                    keep_strategy=KeepStrategy(data["keep_strategy"]),
                )
            elif data["operation_type"] == "orphan-cleanup":
                config = OrphanCleanupConfig(
                    database=data["database"],
                    collection=data["collection"],
                    environment=Environment(data["environment"]),
                    test_mode=data["test_mode"],
                    foreign_key_field=data["foreign_key_field"],
                    parent_collection=data["parent_collection"],
                    parent_key_field=data["parent_key_field"],
                )

            # Create operation
            orchestrator = OperationOrchestrator()
            status.update("✓ Configuration created\n⏳ Creating operation...")

            operation_id = orchestrator.create_operation(config)
            self.app.wizard_data["operation_id"] = operation_id

            status.update(f"✓ Operation created: {operation_id}\n⏳ Executing...")

            # Execute operation
            result = orchestrator.execute_operation(operation_id)

            self.app.wizard_data["result"] = result

            if result.status.value == "completed":
                status.update(f"✓ Operation completed successfully!\nRecords affected: {result.records_affected}\nDuration: {result.duration_seconds:.2f}s")
                status.set_classes("success")
            else:
                status.update(f"✗ Operation failed\n{result.error_message}")
                status.set_classes("error")

            # Enable results button
            self.query_one("#results-btn", Button).disabled = False

        except Exception as e:
            status.update(f"✗ Error: {e!s}")
            status.set_classes("error")
            log.update(f"Stack trace:\n{e}")

    @on(Button.Pressed, "#results-btn")
    async def on_results(self) -> None:
        """Show results screen"""
        await self.app.push_screen(ResultsScreen())


class ResultsScreen(Screen):
    """Show operation results and next steps"""

    BINDINGS = [
        Binding("enter", "done", "Done"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="wizard-container"):
            yield Static("📊 Operation Results", classes="title")

            yield Static(self._build_results(), id="results-content", classes="section")

            with Vertical(classes="section"):
                yield Static("Next Steps:", classes="section-title")
                yield Static(self._build_next_steps())

            with Horizontal(classes="button-group"):
                yield Button("Done", variant="primary", id="done-btn")
        yield Footer()

    def _build_results(self) -> str:
        """Build results summary"""
        data = self.app.wizard_data
        result = data.get("result")

        if not result:
            return "No results available"

        summary = f"""
Operation Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Operation ID:      {result.operation_id}
Status:            {result.status.value}
Records Affected:  {result.records_affected}
Records Deleted:   {result.records_deleted}
Records Updated:   {result.records_updated}
Duration:          {result.duration_seconds:.2f}s
"""

        if result.backup_file:
            summary += f"\nBackup File:       {result.backup_file}"

        if result.report_file:
            summary += f"\nReport File:       {result.report_file}"

        if result.error_message:
            summary += f"\n\nError: {result.error_message}"

        return summary

    def _build_next_steps(self) -> str:
        """Build next steps"""
        data = self.app.wizard_data
        operation_id = data.get("operation_id", "N/A")

        return f"""
To verify operation:
  yirifi-dq verify {operation_id}

To view details:
  yirifi-dq info {operation_id}

To rollback (if needed):
  yirifi-dq rollback {operation_id}

To view all operations:
  yirifi-dq list
"""

    @on(Button.Pressed, "#done-btn")
    def on_done(self) -> None:
        """Exit wizard"""
        self.app.exit()

    def action_done(self) -> None:
        """Exit wizard"""
        self.app.exit()

    def action_quit(self) -> None:
        """Quit wizard"""
        self.app.exit()


def launch_wizard():
    """Launch the interactive TUI wizard"""
    app = WizardApp()
    app.run()


if __name__ == "__main__":
    launch_wizard()
