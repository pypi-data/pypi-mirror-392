#!/usr/bin/env python3
"""
Yirifi Data Quality CLI - Main Entry Point

Usage:
    yirifi-dq new                    # Launch interactive wizard
    yirifi-dq list                   # List all operations
    yirifi-dq verify <operation-id>  # Verify an operation
    yirifi-dq rollback <operation-id># Rollback an operation
    yirifi-dq stats                  # Show framework statistics
"""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="yirifi-dq")
@click.pass_context
def cli(ctx):
    """
    Yirifi Data Quality CLI

    A terminal-based system for managing MongoDB data quality operations.

    Use --help on any command for more information.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


# NOTE: The 'new' command has been removed.
# Use 'yirifi-dq run <script-id>' to execute scripts.
# Use 'yirifi-dq scripts list' to see available scripts.


@cli.command()
@click.option(
    "--status",
    type=click.Choice(["planning", "ready", "executing", "verifying", "completed", "failed", "rolled_back"]),
    help="Filter by status",
)
@click.option("--database", help="Filter by database")
@click.option("--collection", help="Filter by collection")
@click.option("--limit", type=int, default=20, help="Number of operations to show (default: 20)")
def list(status, database, collection, limit):
    """
    List all data quality operations.

    Examples:

        yirifi-dq list
        yirifi-dq list --status completed
        yirifi-dq list --database regdb --collection links
    """
    from yirifi_dq.commands.list import execute_list_command

    execute_list_command(status, database, collection, limit)


@cli.command()
@click.argument("operation_id")
@click.option("--auto-rollback", is_flag=True, help="Automatically rollback if verification fails")
def verify(operation_id, auto_rollback):
    """
    Verify the results of an operation.

    Runs verification checks:
    - Count validation
    - Duplicate detection
    - Orphan detection
    - Referential integrity

    Examples:

        yirifi-dq verify 001
        yirifi-dq verify 001 --auto-rollback
    """
    from yirifi_dq.commands.verify import execute_verify_command

    execute_verify_command(operation_id, auto_rollback)


@cli.command()
@click.argument("operation_id")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.option("--dry-run", is_flag=True, help="Preview rollback without executing")
def rollback(operation_id, force, dry_run):
    """
    Rollback an operation using its backup.

    This will restore all records from the backup file and verify the restoration.

    Examples:

        yirifi-dq rollback 001
        yirifi-dq rollback 001 --dry-run
        yirifi-dq rollback 001 --force
    """
    from yirifi_dq.commands.rollback import execute_rollback_command

    execute_rollback_command(operation_id, force, dry_run)


@cli.command()
@click.option("--database", help="Show statistics for specific database")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def stats(database, output_json):
    """
    Show framework statistics.

    Displays:
    - Total operations completed
    - Records affected
    - Operations by type
    - Recent activity

    Examples:

        yirifi-dq stats
        yirifi-dq stats --database regdb
        yirifi-dq stats --json
    """
    from yirifi_dq.commands.stats import execute_stats_command

    execute_stats_command(database, output_json)


@cli.command()
@click.argument("operation_id")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def execute(operation_id, force):
    """
    Execute a previously created operation.

    Use this to execute operations that were created but not yet executed.

    Examples:

        yirifi-dq execute <operation-id>
        yirifi-dq execute <operation-id> --force
    """
    from yirifi_dq.commands.execute import execute_execute_command

    execute_execute_command(operation_id, force)


@cli.command()
@click.argument("operation_id")
@click.option("--level", type=click.Choice(["INFO", "WARNING", "ERROR", "DEBUG"]), help="Filter by log level")
@click.option("--limit", type=int, default=100, help="Number of log entries to show (default: 100)")
@click.option("--follow", is_flag=True, help="Follow logs in real-time (not implemented)")
def logs(operation_id, level, limit, follow):
    """
    View operation logs.

    Shows detailed execution logs for debugging and audit trail.

    Examples:

        yirifi-dq logs <operation-id>
        yirifi-dq logs <operation-id> --level ERROR
        yirifi-dq logs <operation-id> --limit 50
    """
    from yirifi_dq.commands.logs import execute_logs_command

    execute_logs_command(operation_id, level, limit, follow)


# NOTE: The old template/operation systems have been deprecated.
# All scripts are now defined in yirifi_dq/script_configs/
# Use 'yirifi-dq run <script-id>' to execute scripts
# Use 'yirifi-dq scripts list' to see available scripts


@cli.command()
@click.argument("operation_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def info(operation_id, output_json):
    """
    Show detailed information about an operation.

    Examples:

        yirifi-dq info <operation-id>
        yirifi-dq info <operation-id> --json
    """
    from yirifi_dq.commands.show import execute_show_command

    execute_show_command(operation_id, output_json)


@cli.command()
@click.option(
    "--mode",
    type=click.Choice(["dashboard", "wizard"], case_sensitive=False),
    default="dashboard",
    help="TUI mode: dashboard (Bloomberg-style) or wizard (classic)",
)
def tui(mode):
    """
    Launch the interactive TUI (Terminal User Interface).

    The TUI provides a rich, keyboard-driven interface for managing operations.

    Modes:
    - dashboard (default): Bloomberg-style power terminal with multi-pane layout,
      live updates, command palette (Ctrl+P), and vim-style navigation
    - wizard: Classic step-by-step wizard for creating operations

    Examples:

        # Launch Bloomberg-style dashboard (default)
        yirifi-dq tui

        # Launch dashboard explicitly
        yirifi-dq tui --mode dashboard

        # Launch classic wizard
        yirifi-dq tui --mode wizard

    Keyboard Shortcuts (Dashboard Mode):
        1-5       - Navigate between screens
        Ctrl+P    - Command palette (fuzzy search)
        D/O/P     - Quick operation creation
        j/k       - Vim-style navigation
        /         - Search
        ?         - Help
        Q         - Quit
    """
    from yirifi_dq.tui.app import run_terminal

    console.print(f"\n[bold cyan]Launching {mode.upper()} mode...[/bold cyan]\n")
    run_terminal(mode=mode.lower())


# ========== Plugin System Commands ==========


@cli.command()
@click.argument("script_id")
@click.option("--database", required=True, help="Database name")
@click.option("--collection", required=True, help="Collection name")
@click.option(
    "--env",
    type=click.Choice(["PRD", "DEV", "UAT"], case_sensitive=False),
    default="DEV",
    help="Environment (default: DEV)",
)
@click.option("--test-mode/--no-test-mode", default=True, help="Run in test mode (default: True)")
@click.option("--dry-run", is_flag=True, help="Preview changes without executing")
@click.option("--auto-backup/--no-auto-backup", default=True, help="Create automatic backup (default: True)")
@click.option("--auto-verify/--no-auto-verify", default=True, help="Run automatic verification (default: True)")
@click.option("--param", "-p", multiple=True, help="Script parameters (format: key=value)")
def run(script_id, database, collection, env, test_mode, dry_run, auto_backup, auto_verify, param):
    """
    Run a plugin script.

    This command executes a registered plugin script with the specified parameters.
    Scripts are auto-discovered from yirifi_dq/script_configs/.

    Parameters are passed using -p/--param flag in key=value format.
    You can specify multiple parameters by repeating the flag.

    Examples:

        # Run built-in duplicate cleanup
        yirifi-dq run links/simple-duplicate-cleanup \\
            --database regdb \\
            --collection links \\
            -p field=url \\
            -p keep_strategy=oldest \\
            --test-mode

        # Run custom script with multiple parameters
        yirifi-dq run links/example-cleanup \\
            --database regdb \\
            --collection links \\
            -p field=url \\
            -p age_threshold_days=90 \\
            -p keep_strategy=oldest \\
            -p archive_orphans=false \\
            --test-mode

        # Production run (no test mode, auto-backup enabled)
        yirifi-dq run links/simple-duplicate-cleanup \\
            --database regdb \\
            --collection links \\
            -p field=url \\
            --env PRD \\
            --no-test-mode

        # Dry run (preview without changes)
        yirifi-dq run links/example-cleanup \\
            --database regdb \\
            --collection links \\
            -p field=url \\
            --dry-run

    Use 'yirifi-dq scripts list' to see all available scripts.
    Use 'yirifi-dq scripts info <script-id>' to see required parameters.
    """
    from yirifi_dq.commands.run import execute_run_command

    # Parse parameters from key=value format
    parameters = {}
    for p in param:
        if "=" not in p:
            console.print(f"[bold red]Error:[/bold red] Invalid parameter format: {p}")
            console.print("Use format: -p key=value")
            return

        key, value = p.split("=", 1)

        # Try to convert to appropriate type
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "", 1).isdigit():
            value = float(value)

        parameters[key] = value

    execute_run_command(
        script_id=script_id,
        database=database,
        collection=collection,
        parameters=parameters,
        env=env,
        test_mode=test_mode,
        dry_run=dry_run,
        auto_backup=auto_backup,
        auto_verify=auto_verify,
    )


@cli.group()
def scripts():
    """
    Manage plugin scripts.

    This command group provides utilities for discovering, inspecting,
    and validating plugin scripts.

    Scripts are auto-discovered from:
    - yirifi_dq/script_configs/*.yaml (YAML configurations)
    - yirifi_dq/scripts/*.py (Custom Python scripts)

    Examples:

        yirifi-dq scripts list
        yirifi-dq scripts info links/simple-duplicate-cleanup
        yirifi-dq scripts validate links/example-cleanup
    """
    pass


@scripts.command("list")
@click.option("--domain", help="Filter by domain (links, articles, pipeline, etc.)")
@click.option("--tag", help="Filter by tag (duplicates, cleanup, etc.)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def scripts_list(domain, tag, output_json):
    """
    List all available plugin scripts.

    Shows all scripts discovered from yirifi_dq/script_configs/.

    Examples:

        # List all scripts
        yirifi-dq scripts list

        # List scripts in 'links' domain
        yirifi-dq scripts list --domain links

        # List scripts tagged 'duplicates'
        yirifi-dq scripts list --tag duplicates

        # Get JSON output
        yirifi-dq scripts list --json
    """
    from yirifi_dq.commands.scripts import execute_scripts_list_command

    execute_scripts_list_command(domain, tag, output_json)


@scripts.command("info")
@click.argument("script_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def scripts_info(script_id, output_json):
    """
    Show detailed information about a script.

    Displays:
    - Script name and description
    - Required and optional parameters
    - Safety configuration
    - Usage examples

    Examples:

        yirifi-dq scripts info links/simple-duplicate-cleanup
        yirifi-dq scripts info links/example-cleanup --json
    """
    from yirifi_dq.commands.scripts import execute_scripts_info_command

    execute_scripts_info_command(script_id, output_json)


@scripts.command("validate")
@click.argument("script_id")
def scripts_validate(script_id):
    """
    Validate a script configuration.

    Checks:
    - YAML syntax and structure
    - Required fields present
    - Parameter definitions valid
    - Python script exists (for custom scripts)
    - Script class exists and inherits from BaseScript

    Examples:

        yirifi-dq scripts validate links/simple-duplicate-cleanup
        yirifi-dq scripts validate links/example-cleanup
    """
    from yirifi_dq.commands.scripts import execute_scripts_validate_command

    execute_scripts_validate_command(script_id)


def main():
    """Main entry point for the CLI."""
    import sys

    try:
        cli(obj={})
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
