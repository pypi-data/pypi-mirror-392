"""
'show' command implementation (alias for 'info').

Shows detailed information about a specific operation.
"""

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from yirifi_dq.db.state_manager import get_state_manager

console = Console()


def execute_show_command(operation_id, output_json):
    """
    Show detailed operation information.

    Args:
        operation_id: Operation ID to show
        output_json: Output as JSON
    """
    state_manager = get_state_manager()
    operation = state_manager.get_operation(operation_id)

    if not operation:
        console.print(f"[red]Operation not found: {operation_id}[/red]")
        return

    # Helper to get value (handles both enum and string due to use_enum_values)
    def get_value(field):
        return field.value if hasattr(field, "value") else field

    if output_json:
        # Output as JSON
        op_dict = {
            "operation_id": operation.operation_id,
            "operation_name": operation.operation_name,
            "operation_type": get_value(operation.operation_type),
            "database": operation.database,
            "collection": operation.collection,
            "field": operation.field,
            "environment": get_value(operation.environment),
            "test_mode": operation.test_mode,
            "status": get_value(operation.status),
            "operation_folder": operation.operation_folder,
            "backup_file": operation.backup_file,
            "report_file": operation.report_file,
            "script_file": operation.script_file,
            "records_affected": operation.records_affected,
            "records_deleted": operation.records_deleted,
            "records_updated": operation.records_updated,
            "records_inserted": operation.records_inserted,
            "created_at": operation.created_at.isoformat() if operation.created_at else None,
            "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
            "summary": operation.summary,
            "tags": json.loads(operation.tags) if operation.tags else [],
            "learnings": json.loads(operation.learnings) if operation.learnings else [],
        }
        console.print(json.dumps(op_dict, indent=2))
        return

    # Display as rich table
    console.print("\n[bold cyan]Operation Details[/bold cyan]\n")

    # Main info table
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value")

    # Status with color coding
    status_value = get_value(operation.status)
    if status_value == "completed":
        status_display = f"[green]{status_value}[/green]"
    elif status_value == "failed":
        status_display = f"[red]{status_value}[/red]"
    elif status_value == "executing":
        status_display = f"[yellow]{status_value}[/yellow]"
    else:
        status_display = status_value

    table.add_row("Operation ID", operation.operation_id)
    table.add_row("Name", operation.operation_name or "-")
    table.add_row("Type", get_value(operation.operation_type))
    table.add_row("Database", operation.database)
    table.add_row("Collection", operation.collection)
    table.add_row("Field", operation.field or "-")
    table.add_row("Environment", get_value(operation.environment))
    table.add_row("Test Mode", "Yes" if operation.test_mode else "No")
    table.add_row("Status", status_display)
    table.add_row("", "")  # Separator

    table.add_row("Records Affected", f"{operation.records_affected:,}")
    table.add_row("Records Deleted", f"{operation.records_deleted:,}")
    table.add_row("Records Updated", f"{operation.records_updated:,}")
    table.add_row("Records Inserted", f"{operation.records_inserted:,}")
    table.add_row("", "")  # Separator

    if operation.created_at:
        table.add_row("Created", operation.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    if operation.completed_at:
        table.add_row("Completed", operation.completed_at.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("", "")  # Separator

    table.add_row("Operation Folder", operation.operation_folder or "-")
    table.add_row("Backup File", operation.backup_file or "-")
    table.add_row("Report File", operation.report_file or "-")
    table.add_row("Script File", operation.script_file or "-")

    console.print(table)

    # Summary
    if operation.summary:
        console.print("\n[bold]Summary:[/bold]")
        console.print(Panel(operation.summary, border_style="dim"))

    # Tags
    if operation.tags:
        try:
            tags = json.loads(operation.tags)
            if tags:
                console.print(f"\n[bold]Tags:[/bold] {', '.join(tags)}")
        except Exception:
            pass

    # Learnings
    if operation.learnings:
        try:
            learnings = json.loads(operation.learnings)
            if learnings:
                console.print("\n[bold]Learnings:[/bold]")
                for i, learning in enumerate(learnings, 1):
                    console.print(f"  {i}. {learning}")
        except Exception:
            pass

    console.print()
