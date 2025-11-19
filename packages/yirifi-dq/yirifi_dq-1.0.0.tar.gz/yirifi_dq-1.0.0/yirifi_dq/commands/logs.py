"""
'logs' command implementation.

View operation logs for debugging and audit trail.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from yirifi_dq.db.state_manager import get_state_manager

console = Console()


def execute_logs_command(operation_id, level, limit, _follow):
    """
    View logs for an operation.

    Args:
        operation_id: Operation ID
        level: Filter by log level (INFO, WARNING, ERROR, DEBUG)
        limit: Maximum number of logs to show
        _follow: Follow logs in real-time (not implemented yet)
    """
    console.print(f"\n[bold cyan]Logs for operation {operation_id}[/bold cyan]\n")

    state_manager = get_state_manager()

    # Get operation
    operation = state_manager.get_operation(operation_id)
    if not operation:
        console.print(f"[red]Error:[/red] Operation {operation_id} not found")
        return

    # Display operation info
    console.print(f"Operation: {operation.operation_type.value}")
    console.print(f"Status: {operation.status.value}")
    console.print(f"Database: {operation.database}.{operation.collection}\n")

    # Get logs
    logs = state_manager.get_logs(operation_id, level=level, limit=limit)

    if not logs:
        console.print("[yellow]No logs found for this operation.[/yellow]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Time", style="dim", width=20)
    table.add_column("Level", width=8)
    table.add_column("Message")

    # Level color mapping
    level_colors = {"INFO": "blue", "WARNING": "yellow", "ERROR": "red", "DEBUG": "dim"}

    # Add rows
    for log in reversed(logs):  # Show newest first
        level_style = level_colors.get(log.level, "white")
        table.add_row(
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            f"[{level_style}]{log.level}[/{level_style}]",
            log.message,
        )

    console.print(table)
    console.print(f"\n[dim]Showing {len(logs)} log entries[/dim]")

    if len(logs) == limit:
        console.print("[dim]Tip: Use --limit to show more entries[/dim]")

    # Show error details if operation failed
    if operation.status.value == "failed" and operation.error_stack_trace:
        console.print("\n[bold red]Error Stack Trace:[/bold red]")
        console.print(Panel(operation.error_stack_trace, border_style="red"))
