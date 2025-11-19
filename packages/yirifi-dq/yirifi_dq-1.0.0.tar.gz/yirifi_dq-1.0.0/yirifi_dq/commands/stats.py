"""
'stats' command implementation.

Shows framework statistics from state database.
"""

import json

from rich.console import Console
from rich.table import Table

from yirifi_dq.db.state_manager import get_state_manager

console = Console()


def execute_stats_command(database, output_json):
    """
    Show framework statistics.

    Args:
        database: Filter by database
        output_json: Output as JSON
    """
    state_manager = get_state_manager()
    stats = state_manager.get_stats()

    if output_json:
        stats_dict = {
            "total_operations": stats.total_operations,
            "operations_completed": stats.operations_completed,
            "operations_failed": stats.operations_failed,
            "operations_rolled_back": stats.operations_rolled_back,
            "total_records_affected": stats.total_records_affected,
            "total_records_deleted": stats.total_records_deleted,
            "total_records_updated": stats.total_records_updated,
            "total_records_inserted": stats.total_records_inserted,
            "total_backups_created": stats.total_backups_created,
            "last_operation_at": stats.last_operation_at.isoformat() if stats.last_operation_at else None,
        }
        console.print(json.dumps(stats_dict, indent=2))
        return

    console.print("\n[bold cyan]Framework Statistics[/bold cyan]\n")

    # Overall stats table
    table = Table(show_header=True, header_style="bold magenta", title="Overall Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Operations", f"{stats.total_operations:,}")
    table.add_row("Completed", f"{stats.operations_completed:,}")
    table.add_row("Failed", f"{stats.operations_failed:,}")
    table.add_row("Rolled Back", f"{stats.operations_rolled_back:,}")
    table.add_row("", "")  # Separator
    table.add_row("Records Affected", f"{stats.total_records_affected:,}")
    table.add_row("Records Deleted", f"{stats.total_records_deleted:,}")
    table.add_row("Records Updated", f"{stats.total_records_updated:,}")
    table.add_row("Records Inserted", f"{stats.total_records_inserted:,}")
    table.add_row("", "")  # Separator
    table.add_row("Backups Created", f"{stats.total_backups_created:,}")

    if stats.last_operation_at:
        table.add_row("Last Operation", stats.last_operation_at.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)

    # Database-specific stats if filtering
    if database:
        console.print(f"\n[bold]Operations for database: {database}[/bold]\n")
        operations = state_manager.list_operations(database=database, limit=100)

        db_table = Table(show_header=True, header_style="bold magenta")
        db_table.add_column("Collection")
        db_table.add_column("Operations", justify="right")
        db_table.add_column("Records Affected", justify="right")

        # Group by collection
        collection_stats = {}
        for op in operations:
            coll = op.collection
            if coll not in collection_stats:
                collection_stats[coll] = {"count": 0, "records": 0}
            collection_stats[coll]["count"] += 1
            collection_stats[coll]["records"] += op.records_affected

        for coll, stats_data in collection_stats.items():
            db_table.add_row(coll, str(stats_data["count"]), f"{stats_data['records']:,}")

        console.print(db_table)

    console.print(f"\n[dim]Statistics last updated: {stats.last_updated_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
