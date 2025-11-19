"""
Scripts command - Manage plugin scripts.

This module implements the 'yirifi-dq scripts' command group for discovering,
inspecting, and validating plugin scripts.
"""

import json
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from yirifi_dq.plugins.orchestrator import ScriptOrchestrator
from yirifi_dq.plugins.registry import get_registry
from yirifi_dq.plugins.exceptions import ScriptLoadError

console = Console()


def execute_scripts_list_command(
    domain: Optional[str],
    tag: Optional[str],
    output_json: bool,
) -> None:
    """
    List all available plugin scripts.

    Args:
        domain: Filter by domain
        tag: Filter by tag
        output_json: Output as JSON
    """
    try:
        orchestrator = ScriptOrchestrator()

        # Get scripts
        scripts = orchestrator.list_available_scripts(domain=domain, tag=tag)

        if output_json:
            # JSON output
            output = []
            for script in scripts:
                output.append({
                    "id": script.id,
                    "name": script.name,
                    "domain": script.domain,
                    "tags": script.tags,
                    "script_type": script.script_type,
                    "description": script.description,
                })
            console.print_json(data=output)
            return

        # Rich table output
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]Available Plugin Scripts[/bold cyan]\n\n"
            f"Total: [yellow]{len(scripts)}[/yellow] scripts"
            + (f"\nDomain: [green]{domain}[/green]" if domain else "")
            + (f"\nTag: [magenta]{tag}[/magenta]" if tag else ""),
            title="📜 Script Registry",
            border_style="cyan"
        ))
        console.print()

        if not scripts:
            console.print("[yellow]No scripts found matching the criteria.[/yellow]")
            console.print("\nUse 'yirifi-dq scripts list' to see all scripts.")
            return

        # Group by domain
        scripts_by_domain = {}
        for script in scripts:
            if script.domain not in scripts_by_domain:
                scripts_by_domain[script.domain] = []
            scripts_by_domain[script.domain].append(script)

        # Display by domain
        for domain_name in sorted(scripts_by_domain.keys()):
            domain_scripts = scripts_by_domain[domain_name]

            console.print(f"[bold cyan]■ {domain_name}[/bold cyan] ({len(domain_scripts)} scripts)")
            console.print()

            table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
            table.add_column("ID", style="yellow", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Type", style="cyan")
            table.add_column("Tags", style="dim")

            for script in domain_scripts:
                tags_str = ", ".join(script.tags[:3])
                if len(script.tags) > 3:
                    tags_str += f" +{len(script.tags) - 3}"

                table.add_row(
                    script.id,
                    script.name,
                    script.script_type,
                    tags_str
                )

            console.print(table)
            console.print()

        console.print("[dim]Use 'yirifi-dq scripts info <script-id>' for more details.[/dim]")
        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


def execute_scripts_info_command(script_id: str, output_json: bool) -> None:
    """
    Show detailed information about a script.

    Args:
        script_id: Script identifier
        output_json: Output as JSON
    """
    try:
        orchestrator = ScriptOrchestrator()
        info = orchestrator.get_script_info(script_id)

        if not info:
            console.print(f"[bold red]Error:[/bold red] Script not found: {script_id}")
            console.print("\nUse 'yirifi-dq scripts list' to see available scripts.")
            return

        if output_json:
            console.print_json(data=info)
            return

        # Rich formatted output
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{info['name']}[/bold cyan]\n\n"
            f"ID: [yellow]{info['id']}[/yellow]\n"
            f"Domain: [green]{info['domain']}[/green]\n"
            f"Type: [magenta]{info['script_type']}[/magenta]\n"
            f"Tags: [dim]{', '.join(info['tags'])}[/dim]",
            title="📄 Script Information",
            border_style="cyan"
        ))

        # Description
        console.print()
        console.print("[bold]Description:[/bold]")
        console.print(f"  {info['description']}")

        # Parameters
        console.print()
        console.print("[bold]Parameters:[/bold]")

        if not info['parameters']:
            console.print("  [dim]No parameters required[/dim]")
        else:
            params_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
            params_table.add_column("Name", style="yellow")
            params_table.add_column("Type", style="cyan")
            params_table.add_column("Required", style="white")
            params_table.add_column("Default", style="green")
            params_table.add_column("Description", style="dim")

            for param in info['parameters']:
                required = "✓" if param['required'] else ""
                default = str(param.get('default', '')) if param.get('default') is not None else ""

                params_table.add_row(
                    param['name'],
                    param['type'],
                    required,
                    default,
                    param.get('help', '')
                )

            console.print(params_table)

        # Safety features
        console.print()
        console.print("[bold]Safety Features:[/bold]")
        safety = info['safety']

        safety_table = Table(show_header=False, box=None)
        safety_table.add_row(
            "Backup Required:",
            "[green]Yes[/green]" if safety['requires_backup'] else "[yellow]No[/yellow]"
        )
        safety_table.add_row(
            "Verification Required:",
            "[green]Yes[/green]" if safety['requires_verification'] else "[yellow]No[/yellow]"
        )
        safety_table.add_row(
            "Test Mode Supported:",
            "[green]Yes[/green]" if safety['supports_test_mode'] else "[yellow]No[/yellow]"
        )
        console.print(safety_table)

        # Examples
        if info.get('examples'):
            console.print()
            console.print("[bold]Usage Examples:[/bold]")
            console.print()

            for i, example in enumerate(info['examples'], 1):
                console.print(f"  [bold cyan]{i}. {example['description']}[/bold cyan]")
                console.print()

                # Format CLI example
                cli_lines = example['cli'].strip().split('\n')
                for line in cli_lines:
                    console.print(f"     [dim]{line}[/dim]")
                console.print()

        console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


def execute_scripts_validate_command(script_id: str) -> None:
    """
    Validate a script configuration.

    Args:
        script_id: Script identifier
    """
    try:
        console.print()
        console.print(f"[bold cyan]Validating script:[/bold cyan] {script_id}")
        console.print()

        registry = get_registry()

        # Check 1: Script config exists
        console.print("  [cyan]1.[/cyan] Checking script config... ", end="")
        config = registry.get_script_config(script_id)
        if not config:
            console.print("[bold red]✗ Not found[/bold red]")
            console.print("\n[bold red]Error:[/bold red] Script config not found in registry")
            console.print("\nUse 'yirifi-dq scripts list' to see available scripts.")
            return
        console.print("[green]✓[/green]")

        # Check 2: Required fields present
        console.print("  [cyan]2.[/cyan] Checking required fields... ", end="")
        required_fields = ['id', 'name', 'domain', 'script_type']
        missing = [f for f in required_fields if not hasattr(config, f)]
        if missing:
            console.print(f"[bold red]✗ Missing: {', '.join(missing)}[/bold red]")
            return
        console.print("[green]✓[/green]")

        # Check 3: Parameters valid
        console.print("  [cyan]3.[/cyan] Checking parameters... ", end="")
        param_errors = []
        for param in config.parameters:
            # Check enum parameters have options
            if param.type == "enum" and not param.enum:
                param_errors.append(f"{param.name}: enum type but no options defined")

            # Check required parameters don't have contradictory settings
            if param.required and param.default is None:
                # This is OK - required params can be without defaults
                pass

        if param_errors:
            console.print(f"[bold red]✗[/bold red]")
            for error in param_errors:
                console.print(f"     [red]• {error}[/red]")
            return
        console.print(f"[green]✓[/green] ({len(config.parameters)} parameters)")

        # Check 4: Script type specific checks
        if config.script_type == "custom":
            # Check Python file exists
            console.print("  [cyan]4.[/cyan] Checking Python script... ", end="")

            if not config.script_path:
                console.print("[bold red]✗ No script_path defined[/bold red]")
                return

            from pathlib import Path
            script_path = Path(config.script_path)
            if not script_path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                script_path = project_root / script_path

            if not script_path.exists():
                console.print(f"[bold red]✗ File not found: {script_path}[/bold red]")
                return
            console.print("[green]✓[/green]")

            # Check script class exists
            console.print("  [cyan]5.[/cyan] Checking script class... ", end="")
            try:
                script_instance = registry.get_script_instance(script_id)
                console.print(f"[green]✓[/green] ({script_instance.__class__.__name__})")
            except ScriptLoadError as e:
                console.print(f"[bold red]✗[/bold red]")
                console.print(f"     [red]{e}[/red]")
                return

        elif config.script_type == "built-in":
            # Check operation is defined
            console.print("  [cyan]4.[/cyan] Checking built-in operation... ", end="")

            if not config.operation:
                console.print("[bold red]✗ No operation defined[/bold red]")
                return

            valid_operations = ["duplicate-cleanup", "orphan-cleanup", "field-update", "slug-generation"]
            if config.operation not in valid_operations:
                console.print(f"[bold red]✗ Unknown operation: {config.operation}[/bold red]")
                console.print(f"     [dim]Valid operations: {', '.join(valid_operations)}[/dim]")
                return

            console.print(f"[green]✓[/green] ({config.operation})")

        # Check 5: Safety configuration
        console.print(f"  [cyan]{'5' if config.script_type == 'custom' else '6'}.[/cyan] Checking safety config... ", end="")
        if config.safety:
            console.print("[green]✓[/green]")
        else:
            console.print("[yellow]⚠ No safety config[/yellow]")

        # All checks passed
        console.print()
        console.print(Panel.fit(
            f"[bold green]✓ Validation passed[/bold green]\n\n"
            f"Script: [cyan]{config.name}[/cyan]\n"
            f"Type: [yellow]{config.script_type}[/yellow]\n"
            f"Parameters: [blue]{len(config.parameters)}[/blue]",
            title="✓ Valid Script",
            border_style="green"
        ))
        console.print()

    except Exception as e:
        console.print(f"[bold red]✗[/bold red]")
        console.print()
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        import traceback
        console.print("\n[dim]")
        console.print(traceback.format_exc())
        console.print("[/dim]")
