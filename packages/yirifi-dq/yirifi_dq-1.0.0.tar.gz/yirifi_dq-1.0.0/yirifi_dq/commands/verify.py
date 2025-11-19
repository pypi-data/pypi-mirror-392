"""
'verify' command implementation.

Verifies operation results and data integrity.
"""

from rich.console import Console
from rich.panel import Panel

from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.engine.safety import SafetyEnforcer
from yirifi_dq.core.mongodb import get_client, get_collection, get_database

console = Console()


def execute_verify_command(operation_id, auto_rollback):
    """
    Verify an operation's results.

    Args:
        operation_id: Operation ID
        auto_rollback: Automatically rollback if verification fails
    """
    console.print(f"\n[bold cyan]Verifying operation {operation_id}...[/bold cyan]\n")

    state_manager = get_state_manager()
    safety = SafetyEnforcer(state_manager)

    # Get operation
    operation = state_manager.get_operation(operation_id)
    if not operation:
        console.print(f"[red]Error:[/red] Operation {operation_id} not found")
        return

    # Display operation info
    console.print(f"Type: {operation.operation_type.value}")
    console.print(f"Database: {operation.database}")
    console.print(f"Collection: {operation.collection}")
    console.print(f"Status: {operation.status.value}\n")

    # Connect to MongoDB
    client = get_client(env=operation.environment.value)

    try:
        db = get_database(client, operation.database)
        collection = get_collection(db, operation.collection)

        # Run verification checks
        checks_passed = []
        checks_failed = []

        # Check 1: Record counts
        console.print("[dim]Checking record counts...[/dim]")
        count_result = safety.verify_record_counts(operation_id, collection, {"deleted": operation.records_deleted})
        if count_result["passed"]:
            checks_passed.append(f"Record count: {count_result['current_count']:,}")
        else:
            checks_failed.append("Record count verification failed")

        # Check 2: No duplicates (if duplicate cleanup)
        if operation.operation_type.value == "duplicate-cleanup" and operation.field:
            console.print(f"[dim]Checking for remaining duplicates in '{operation.field}'...[/dim]")
            dup_result = safety.verify_no_duplicates(operation_id, collection, operation.field)
            if dup_result["passed"]:
                checks_passed.append(f"No duplicates in '{operation.field}'")
            else:
                checks_failed.append(f"Found {dup_result['duplicate_groups']} duplicate groups")

        # Check 3: Referential integrity (if links collection)
        if operation.collection == "links" and operation.database == "regdb":
            console.print("[dim]Checking referential integrity...[/dim]")
            integrity_result = safety.verify_referential_integrity(operation_id, operation.database, operation.environment.value)
            if integrity_result["passed"]:
                checks_passed.append("Referential integrity intact")
            else:
                checks_failed.append(f"Found {integrity_result['orphaned_articles']} orphaned articles")

        # Check 4: Backup exists (if destructive operation)
        if operation.backup_file:
            console.print("[dim]Verifying backup file...[/dim]")
            if safety.verify_backup(operation.backup_file):
                checks_passed.append("Backup verified")
            else:
                checks_failed.append("Backup file invalid or missing")

        # Display results
        console.print()
        for check in checks_passed:
            console.print(f"[green]✓[/green] {check}")

        for check in checks_failed:
            console.print(f"[red]✗[/red] {check}")

        # Summary
        console.print()
        if len(checks_failed) == 0:
            console.print(
                Panel.fit(
                    "[bold green]✓ All verification checks passed![/bold green]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    f"[bold red]✗ {len(checks_failed)} verification check(s) failed[/bold red]",
                    border_style="red",
                )
            )

            if auto_rollback:
                console.print("\n[yellow]Auto-rollback enabled, initiating rollback...[/yellow]")

                # Import rollback command
                from yirifi_dq.commands.rollback import execute_rollback_command

                # Execute rollback without prompting (force=True) and not as dry run
                try:
                    execute_rollback_command(
                        operation_id=operation_id,
                        force=True,  # Skip confirmation prompt for auto-rollback
                        dry_run=False,
                    )
                    console.print("[green]✓ Auto-rollback completed successfully[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Auto-rollback failed: {e!s}[/red]")
                    console.print("[yellow]Manual rollback may be required[/yellow]")

    finally:
        # Close MongoDB connection
        if client:
            client.close()
