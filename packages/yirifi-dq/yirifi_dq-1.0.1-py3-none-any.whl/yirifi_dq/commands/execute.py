"""
'execute' command implementation.

Executes operations that were created but not yet executed.
"""

from rich.console import Console
from rich.panel import Panel

from yirifi_dq.db.state_manager import get_state_manager
from yirifi_dq.engine.orchestrator import OperationOrchestrator
from yirifi_dq.models.operation import OperationStatus

console = Console()


def execute_execute_command(operation_id, force):
    """
    Execute a previously created operation.

    Args:
        operation_id: Operation ID
        force: Skip confirmation
    """
    console.print(f"\n[bold cyan]Executing operation {operation_id}...[/bold cyan]\n")

    state_manager = get_state_manager()

    # Get operation
    operation = state_manager.get_operation(operation_id)
    if not operation:
        console.print(f"[red]Error:[/red] Operation {operation_id} not found")
        return

    # Check if already executed
    if operation.status == OperationStatus.COMPLETED:
        console.print("[yellow]Warning:[/yellow] Operation already completed")
        console.print(f"Records affected: {operation.records_affected}")
        console.print("\nTo run again, create a new operation or use replay functionality")
        return

    if operation.status == OperationStatus.FAILED:
        console.print("[yellow]Warning:[/yellow] Operation previously failed")
        console.print(f"Error: {operation.error_message}\n")
        if not force:
            import click

            if not click.confirm("Do you want to retry execution?"):
                console.print("[yellow]Execution cancelled.[/yellow]")
                return

    # Display operation info
    console.print(f"Type: {operation.operation_type.value}")
    console.print(f"Database: {operation.database}")
    console.print(f"Collection: {operation.collection}")
    console.print(f"Environment: {operation.environment.value}")
    console.print(f"Test Mode: {operation.test_mode}\n")

    # Confirm execution
    if not force:
        import click

        if not click.confirm("Execute this operation?"):
            console.print("[yellow]Execution cancelled.[/yellow]")
            return

    # Execute
    console.print("\n[bold]Executing operation...[/bold]\n")

    orchestrator = OperationOrchestrator(state_manager)

    with console.status("[bold green]Running operation..."):
        result = orchestrator.execute_operation(operation_id)

    # Display results
    if result.status.value == "completed":
        console.print(
            Panel.fit(
                f"[bold green]✓ Operation completed successfully![/bold green]\n\n"
                f"Records Affected: {result.records_affected}\n"
                f"Records Deleted: {result.records_deleted}\n"
                f"Records Updated: {result.records_updated}\n"
                f"Duration: {result.duration_seconds:.2f}s",
                border_style="green",
            )
        )

        if result.backup_file:
            console.print(f"\n[dim]Backup: {result.backup_file}[/dim]")
        if result.report_file:
            console.print(f"[dim]Report: {result.report_file}[/dim]")

    else:
        console.print(
            Panel.fit(
                f"[bold red]✗ Operation failed[/bold red]\n\nError: {result.error_message}",
                border_style="red",
            )
        )

        console.print("\n[yellow]Check logs for details:[/yellow]")
        console.print(f"  yirifi-dq logs {operation_id}")
