"""
Run command - Execute plugin scripts.

This module implements the 'yirifi-dq run' command for executing plugin scripts.
"""

from typing import Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from yirifi_dq.plugins.orchestrator import ScriptOrchestrator
from yirifi_dq.plugins.exceptions import ScriptLoadError, ScriptValidationError, ScriptExecutionError

console = Console()


def _display_dry_run_preview(result, console: Console) -> None:
    """
    Display dry-run preview results in a formatted panel.

    Args:
        result: ScriptResult with dry_run_preview populated
        console: Rich console for output
    """
    preview = result.dry_run_preview

    # Build preview content
    content_lines = [
        "[bold cyan]🔍 Dry Run Preview[/bold cyan]",
        "",
        f"[bold]Operation:[/bold] {preview.operation_summary}",
        "",
        "[bold]Would affect:[/bold]"
    ]

    # Show affected counts
    if preview.affected_groups_count > 0:
        content_lines.append(f"  • {preview.affected_groups_count} groups found")

    content_lines.append(f"  • {preview.affected_records_count} records would be affected")
    content_lines.append(f"  • Total records in collection: {preview.total_records}")

    # Show estimated impact
    if preview.estimated_impact:
        content_lines.append("")
        content_lines.append(f"[bold]Estimated impact:[/bold]")
        content_lines.append(f"  {preview.estimated_impact}")

    # Show sample records
    if preview.sample_records:
        content_lines.append("")
        content_lines.append(f"[bold]Sample records (first {len(preview.sample_records)}):[/bold]")
        for i, sample in enumerate(preview.sample_records[:5], 1):
            # Format sample based on what fields it has
            if isinstance(sample, dict):
                if 'value' in sample and 'count' in sample:
                    content_lines.append(f"  {i}. [yellow]{sample['value']}[/yellow] ({sample['count']} copies)")
                elif '_id' in sample:
                    content_lines.append(f"  {i}. ID: [yellow]{sample['_id']}[/yellow]")
                else:
                    # Generic display
                    sample_str = ", ".join([f"{k}: {v}" for k, v in list(sample.items())[:3]])
                    content_lines.append(f"  {i}. {sample_str}")
            else:
                content_lines.append(f"  {i}. {sample}")

        if preview.affected_groups_count > len(preview.sample_records):
            remaining = preview.affected_groups_count - len(preview.sample_records)
            content_lines.append(f"  ... ({remaining} more groups)")

    # Show safety features
    if preview.safety_features:
        content_lines.append("")
        content_lines.append("[bold]Safety features:[/bold]")
        for feature in preview.safety_features:
            if "ON" in feature or "enabled" in feature.lower() or "would" in feature:
                content_lines.append(f"  ✓ {feature}")
            else:
                content_lines.append(f"  • {feature}")

    # Show warnings
    if preview.warnings:
        content_lines.append("")
        content_lines.append("[bold yellow]⚠ Warnings:[/bold yellow]")
        for warning in preview.warnings:
            content_lines.append(f"  • {warning}")

    # Display the panel
    console.print(Panel.fit(
        "\n".join(content_lines),
        title="🔍 Dry Run Preview",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Prompt for confirmation
    console.print()
    console.print("[dim]This was a dry-run preview. No changes were made.[/dim]")
    console.print("[dim]To execute for real, remove the --dry-run flag.[/dim]")


def execute_run_command(
    script_id: str,
    database: str,
    collection: str,
    parameters: Dict[str, Any],
    env: str,
    test_mode: bool,
    dry_run: bool,
    auto_backup: bool,
    auto_verify: bool,
) -> None:
    """
    Execute a plugin script.

    Args:
        script_id: Script identifier (e.g., 'links/simple-duplicate-cleanup')
        database: Database name
        collection: Collection name
        parameters: Script parameters from command line
        env: Environment (DEV, UAT, PRD)
        test_mode: Run in test mode (limited records)
        dry_run: Preview changes without executing
        auto_backup: Create automatic backup
        auto_verify: Run automatic verification
    """
    try:
        # Create orchestrator
        orchestrator = ScriptOrchestrator(env=env)

        # Display header
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]Running Plugin Script[/bold cyan]\n\n"
            f"Script: [yellow]{script_id}[/yellow]\n"
            f"Database: [green]{database}.{collection}[/green]\n"
            f"Environment: [magenta]{env}[/magenta]\n"
            f"Test Mode: {'[green]Yes[/green]' if test_mode else '[red]No[/red]'}\n"
            f"Dry Run: {'[green]Yes[/green]' if dry_run else '[red]No[/red]'}",
            title="🚀 Plugin Execution",
            border_style="cyan"
        ))
        console.print()

        # Get script info for validation
        script_info = orchestrator.get_script_info(script_id)
        if not script_info:
            console.print(f"[bold red]Error:[/bold red] Script not found: {script_id}")
            console.print("\nUse 'yirifi-dq scripts list' to see available scripts.")
            return

        # Display script info
        console.print(f"[bold]Script:[/bold] {script_info['name']}")
        console.print(f"[dim]{script_info['description']}[/dim]")
        console.print()

        # Validate required parameters
        missing_params = []
        for param in script_info['parameters']:
            if param['required'] and param['name'] not in parameters:
                # Check if it has a default value
                if param.get('default') is None:
                    missing_params.append(param['name'])

        if missing_params:
            console.print("[bold red]Error:[/bold red] Missing required parameters:")
            for param_name in missing_params:
                param_info = next(p for p in script_info['parameters'] if p['name'] == param_name)
                console.print(f"  -p {param_name}=<value>  # {param_info['help']}")
            console.print()
            console.print(f"Use 'yirifi-dq scripts info {script_id}' for more details.")
            return

        # Fill in default values for missing optional parameters
        for param in script_info['parameters']:
            if param['name'] not in parameters and param.get('default') is not None:
                parameters[param['name']] = param['default']

        # Display parameters
        if parameters:
            console.print("[bold]Parameters:[/bold]")
            for key, value in parameters.items():
                console.print(f"  {key} = [cyan]{value}[/cyan]")
            console.print()

        # Display safety features
        console.print("[bold]Safety Features:[/bold]")
        console.print(f"  Backup: {'[green]Enabled[/green]' if auto_backup else '[yellow]Disabled[/yellow]'}")
        console.print(f"  Verification: {'[green]Enabled[/green]' if auto_verify else '[yellow]Disabled[/yellow]'}")
        console.print(f"  Collection Lock: [green]Enabled[/green]")
        console.print()

        # Display pre-execution summary
        console.print(Panel.fit(
            f"[bold cyan]Pre-Execution Summary[/bold cyan]\n\n"
            f"Script: [yellow]{script_info['name']}[/yellow]\n"
            f"Target: [green]{database}.{collection}[/green]\n"
            f"Environment: [magenta]{env}[/magenta]\n\n"
            f"[bold]Parameters:[/bold]\n" +
            "\n".join([f"  • {k} = [cyan]{v}[/cyan]" for k, v in parameters.items()]) + "\n\n" +
            f"[bold]Safety:[/bold]\n"
            f"  • Test Mode: {'[green]ON (10 records)[/green]' if test_mode else '[red]OFF (full)[/red]'}\n"
            f"  • Dry Run: {'[green]ON[/green]' if dry_run else '[yellow]OFF[/yellow]'}\n"
            f"  • Backup: {'[green]ON[/green]' if auto_backup else '[yellow]OFF[/yellow]'}\n"
            f"  • Verification: {'[green]ON[/green]' if auto_verify else '[yellow]OFF[/yellow]'}",
            title="📋 Review Configuration",
            border_style="cyan"
        ))
        console.print()

        # Execute script
        console.print("[bold cyan]Executing...[/bold cyan]\n")

        result = orchestrator.run_script(
            script_id=script_id,
            parameters=parameters,
            database_name=database,
            collection_name=collection,
            test_mode=test_mode,
            dry_run=dry_run,
            auto_backup=auto_backup,
            auto_verify=auto_verify,
        )

        # Display results
        console.print()

        # Check if this was a dry-run
        if dry_run and result.dry_run_preview:
            _display_dry_run_preview(result, console)
        elif result.success:
            console.print(Panel.fit(
                f"[bold green]✓ Success[/bold green]\n\n"
                f"{result.message}\n\n"
                f"Records processed: [cyan]{result.records_processed}[/cyan]\n"
                f"Records deleted: [yellow]{result.records_deleted}[/yellow]\n"
                f"Records modified: [blue]{result.records_modified}[/blue]\n"
                f"Records created: [green]{result.records_created}[/green]",
                title="📊 Execution Results",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                f"[bold red]✗ Failed[/bold red]\n\n"
                f"{result.message}",
                title="❌ Execution Failed",
                border_style="red"
            ))

        # Display details if available
        if result.details:
            console.print()
            console.print("[bold]Details:[/bold]")
            details_table = Table(show_header=False, box=None)
            for key, value in result.details.items():
                details_table.add_row(f"  {key}:", f"[cyan]{value}[/cyan]")
            console.print(details_table)

        # Display warnings
        if result.warnings:
            console.print()
            console.print("[bold yellow]⚠ Warnings:[/bold yellow]")
            for warning in result.warnings:
                console.print(f"  • {warning}")

        # Display errors
        if result.errors:
            console.print()
            console.print("[bold red]Errors:[/bold red]")
            for error in result.errors:
                console.print(f"  • {error}")

        # Display verification results
        if result.verification_checks:
            console.print()
            console.print("[bold]Verification:[/bold]")
            for check, passed in result.verification_checks.items():
                status = "[green]✓[/green]" if passed else "[red]✗[/red]"
                console.print(f"  {status} {check}")

        console.print()

    except ScriptLoadError as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]Script Not Found[/bold red]\n\n"
            f"{str(e)}\n\n"
            f"[dim]Use 'yirifi-dq scripts list' to see available scripts.[/dim]",
            title="❌ Script Load Error",
            border_style="red"
        ))
        console.print()

    except ScriptValidationError as e:
        console.print()

        # Parse the validation error message
        error_msg = str(e)

        # Enhanced formatting for validation errors
        console.print(Panel.fit(
            f"[bold red]Parameter Validation Failed[/bold red]\n\n"
            f"[yellow]{error_msg}[/yellow]",
            title="❌ Validation Error",
            border_style="red",
            padding=(1, 2)
        ))
        console.print()

    except ScriptExecutionError as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]Execution Failed[/bold red]\n\n"
            f"{str(e)}",
            title="❌ Execution Error",
            border_style="red"
        ))
        console.print()

    except Exception as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]Unexpected Error[/bold red]\n\n"
            f"{str(e)}\n\n"
            f"[dim]This is an unexpected error. Please check logs for details.[/dim]",
            title="❌ Error",
            border_style="red"
        ))

        # Show traceback for debugging
        if console.is_terminal:
            console.print("\n[dim]Stack trace:[/dim]")
            import traceback
            console.print("[dim]")
            console.print(traceback.format_exc())
            console.print("[/dim]")
        console.print()
