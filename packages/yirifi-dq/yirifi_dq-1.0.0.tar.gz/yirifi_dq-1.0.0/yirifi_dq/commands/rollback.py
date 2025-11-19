"""
'rollback' command implementation.

Rollback operations using backup files.
"""

import click
from rich.console import Console
from rich.panel import Panel

from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.engine.safety import SafetyEnforcer
from yirifi_dq.models.operation import OperationStatus

console = Console()


def execute_rollback_command(operation_id, force, dry_run):
    """
    Rollback an operation using its backup.

    Args:
        operation_id: Operation ID
        force: Skip confirmation
        dry_run: Preview only
    """
    console.print(f"\n[bold yellow]⚠️  Rollback Operation {operation_id}[/bold yellow]\n")

    if dry_run:
        console.print("[dim]DRY RUN MODE - No changes will be made[/dim]\n")

    state_manager = get_state_manager()
    safety = SafetyEnforcer(state_manager)

    # Get operation
    operation = state_manager.get_operation(operation_id)
    if not operation:
        console.print(f"[red]Error:[/red] Operation {operation_id} not found")
        return

    # Check if backup exists
    if not operation.backup_file:
        console.print("[red]Error:[/red] No backup file found for this operation")
        console.print("[yellow]Rollback not possible without backup[/yellow]")
        return

    # Display operation info
    console.print(f"Operation Type: {operation.operation_type.value}")
    console.print(f"Database: {operation.database}")
    console.print(f"Collection: {operation.collection}")
    console.print(f"Environment: {operation.environment.value}")
    console.print(f"Status: {operation.status.value}")
    console.print(f"\nBackup File: [cyan]{operation.backup_file}[/cyan]")
    console.print(f"Records to restore: [yellow]{operation.records_deleted}[/yellow]")

    # Verify backup
    if not safety.verify_backup(operation.backup_file):
        console.print("\n[red]Error:[/red] Backup file is invalid or corrupted")
        return

    console.print("[green]✓[/green] Backup file verified")

    # Confirm rollback
    if not force and not dry_run:
        console.print()
        if not click.confirm("Do you want to proceed with rollback?"):
            console.print("[yellow]Rollback cancelled.[/yellow]")
            return

    # Execute rollback
    console.print()
    with console.status("[bold yellow]Rolling back operation..."):
        result = safety.rollback_from_backup(
            operation_id=operation_id,
            backup_file=operation.backup_file,
            database=operation.database,
            collection_name=operation.collection,
            environment=operation.environment.value,
            dry_run=dry_run,
        )

    # Display results
    if result["success"]:
        if dry_run:
            console.print(
                Panel.fit(
                    f"[bold green]✓ Dry run successful[/bold green]\n\nWould restore {result['documents_to_restore']} documents",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    f"[bold green]✓ Rollback completed successfully![/bold green]\n\nRestored {result['restored_count']}/{result['total_documents']} documents",
                    border_style="green",
                )
            )

            # Update operation status
            state_manager.update_operation(operation_id, status=OperationStatus.ROLLED_BACK.value)
            state_manager.add_log(
                operation_id,
                "INFO",
                f"Operation rolled back successfully ({result['restored_count']} documents restored)",
            )

    else:
        console.print(
            Panel.fit(
                f"[bold red]✗ Rollback failed[/bold red]\n\nRestored {result.get('restored_count', 0)}/{result.get('total_documents', 0)} documents\nErrors: {len(result.get('errors', []))}",
                border_style="red",
            )
        )

        if result.get("errors"):
            console.print("\n[bold]First few errors:[/bold]")
            for error in result["errors"][:5]:
                console.print(f"  [red]•[/red] {error}")
