"""
'list' command implementation.

Lists operations from state database with filtering.
"""

from rich.console import Console
from rich.table import Table

from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.models.operation import OperationStatus

console = Console()


def execute_list_command(status, database, collection, limit):
    """
    List operations with optional filters.

    Args:
        status: Filter by status
        database: Filter by database
        collection: Filter by collection
        limit: Maximum results
    """
    console.print("\n[bold cyan]Data Quality Operations[/bold cyan]\n")

    state_manager = get_state_manager()

    # Convert status string to enum if provided
    status_enum = OperationStatus(status) if status else None

    # Get operations
    operations = state_manager.list_operations(status=status_enum, database=database, collection=collection, limit=limit)

    if not operations:
        console.print("[yellow]No operations found matching criteria.[/yellow]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=30)
    table.add_column("Type", width=20)
    table.add_column("Database", width=15)
    table.add_column("Collection", width=20)
    table.add_column("Status", width=12)
    table.add_column("Records", justify="right", width=10)
    table.add_column("Date", width=12)

    # Add rows
    for op in operations:
        # Helper to get value (handles both enum and string due to use_enum_values)
        def get_value(field):
            return field.value if hasattr(field, "value") else field

        # Status color coding
        status_value = get_value(op.status)
        status_display = status_value
        if status_value == "completed":
            status_display = f"[green]{status_display}[/green]"
        elif status_value == "failed":
            status_display = f"[red]{status_display}[/red]"
        elif status_value == "executing":
            status_display = f"[yellow]{status_display}[/yellow]"

        table.add_row(
            op.operation_id[:28] + "..." if len(op.operation_id) > 28 else op.operation_id,
            get_value(op.operation_type),
            op.database,
            op.collection,
            status_display,
            str(op.records_affected),
            op.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print(f"\n[dim]Showing {len(operations)} operation(s)[/dim]")

    if len(operations) == limit:
        console.print("[dim]Tip: Use --limit to show more results[/dim]")
