"""
Progress indicators for long-running operations.

Provides simple, reusable progress bars and status indicators using Rich library.
Optimized for solo operator use - no over-engineering.
"""

import logging
from contextlib import contextmanager
from typing import Callable, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

logger = logging.getLogger(__name__)
console = Console()


@contextmanager
def operation_progress(description: str, total: Optional[int] = None):
    """
    Context manager for showing progress during operations.

    Args:
        description: Description of the operation
        total: Total number of items (if known). If None, shows spinner only.

    Yields:
        progress_callback: Function to call with current count

    Example:
        >>> with operation_progress("Finding duplicates", total=1000) as update:
        ...     for i, doc in enumerate(collection.find()):
        ...         # Process document
        ...         if i % 10 == 0:
        ...             update(i)
        >>>
        >>> # For unknown total (spinner only)
        >>> with operation_progress("Analyzing data") as update:
        ...     for doc in collection.find():
        ...         # Process document
        ...         update()
    """
    if total is None:
        # Spinner-only mode for unknown total
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=False,  # Keep visible after completion
        ) as progress:
            task_id = progress.add_task(description, total=None)
            count = [0]  # Use list for mutable closure

            def update_spinner():
                count[0] += 1
                progress.update(task_id, description=f"{description} ({count[0]:,} processed)")

            try:
                yield update_spinner
            finally:
                progress.update(task_id, description=f"{description} - Complete ({count[0]:,} processed)")
    else:
        # Progress bar mode for known total
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,  # Keep visible after completion
        ) as progress:
            task_id = progress.add_task(description, total=total)

            def update_progress(current: int):
                progress.update(task_id, completed=current)

            try:
                yield update_progress
            finally:
                progress.update(task_id, completed=total)


@contextmanager
def multi_step_progress(steps: list[str]):
    """
    Context manager for multi-step operations with progress tracking.

    Args:
        steps: List of step descriptions

    Yields:
        next_step: Function to call when advancing to next step

    Example:
        >>> steps = [
        ...     "Finding duplicates",
        ...     "Creating backup",
        ...     "Deleting duplicates",
        ...     "Verifying results"
        ... ]
        >>> with multi_step_progress(steps) as next_step:
        ...     # Step 1
        ...     duplicates = find_duplicates(collection, 'url')
        ...     next_step()
        ...
        ...     # Step 2
        ...     backup_file = backup_documents(collection, filter_query)
        ...     next_step()
        ...
        ...     # ... etc
    """
    total = len(steps)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=False,
    ) as progress:
        task_id = progress.add_task("Operation Progress", total=total)
        current_step = [0]  # Use list for mutable closure

        def next_step():
            if current_step[0] < total:
                progress.console.print(f"  ✓ {steps[current_step[0]]}")
                current_step[0] += 1
                progress.update(task_id, completed=current_step[0])

                if current_step[0] < total:
                    progress.update(
                        task_id,
                        description=f"Step {current_step[0] + 1}/{total}: {steps[current_step[0]]}",
                    )

        # Start with first step
        if steps:
            progress.update(task_id, description=f"Step 1/{total}: {steps[0]}")

        try:
            yield next_step
        finally:
            # Mark final step complete if not already
            if current_step[0] < total:
                progress.console.print(f"  ✓ {steps[current_step[0]]}")
                progress.update(task_id, completed=total)


def show_status(message: str, status: str = "info"):
    """
    Show a simple status message with emoji indicator.

    Args:
        message: Message to display
        status: Status type ('info', 'success', 'warning', 'error')

    Example:
        >>> show_status("Finding duplicates...", "info")
        >>> show_status("Found 150 duplicates", "success")
        >>> show_status("Backup recommended", "warning")
        >>> show_status("Operation failed", "error")
    """
    status_icons = {"info": "ℹ️", "success": "✓", "warning": "⚠️", "error": "❌"}

    status_colors = {"info": "blue", "success": "green", "warning": "yellow", "error": "red"}

    icon = status_icons.get(status, "•")
    color = status_colors.get(status, "white")

    console.print(f"[{color}]{icon}[/{color}] {message}")


def batch_progress(items: list, process_fn: Callable, description: str = "Processing", batch_size: int = 10):
    """
    Process items in batches with progress indicator.

    Args:
        items: List of items to process
        process_fn: Function to call for each item
        description: Description for progress bar
        batch_size: How often to update progress (default: every 10 items)

    Returns:
        List of results from process_fn

    Example:
        >>> def process_duplicate(duplicate_group):
        ...     # Process the duplicate
        ...     return select_keeper(duplicate_group)
        >>>
        >>> keepers = batch_progress(
        ...     items=duplicate_groups,
        ...     process_fn=process_duplicate,
        ...     description="Analyzing duplicates",
        ...     batch_size=5
        ... )
    """
    total = len(items)
    results = []

    with operation_progress(description, total=total) as update:
        for i, item in enumerate(items):
            result = process_fn(item)
            results.append(result)

            # Update progress every batch_size items
            if i % batch_size == 0 or i == total - 1:
                update(i + 1)

    return results


if __name__ == "__main__":
    import time

    console.print("\n[bold]Progress Utilities Demo[/bold]\n")

    # Demo 1: Known total
    console.print("[bold cyan]Demo 1: Processing with known total[/bold cyan]")
    with operation_progress("Finding duplicates", total=100) as update:
        for i in range(100):
            time.sleep(0.01)  # Simulate work
            if i % 5 == 0:
                update(i)
        update(100)

    console.print()

    # Demo 2: Unknown total (spinner)
    console.print("[bold cyan]Demo 2: Processing with unknown total[/bold cyan]")
    with operation_progress("Scanning collection") as update:
        for i in range(50):
            time.sleep(0.02)  # Simulate work
            if i % 10 == 0:
                update()

    console.print()

    # Demo 3: Multi-step
    console.print("[bold cyan]Demo 3: Multi-step operation[/bold cyan]")
    steps = ["Finding duplicates", "Creating backup", "Deleting duplicates", "Verifying results"]
    with multi_step_progress(steps) as next_step:
        time.sleep(0.5)
        next_step()
        time.sleep(0.5)
        next_step()
        time.sleep(0.5)
        next_step()
        time.sleep(0.5)
        next_step()

    console.print()

    # Demo 4: Status messages
    console.print("[bold cyan]Demo 4: Status messages[/bold cyan]")
    show_status("Starting operation", "info")
    time.sleep(0.3)
    show_status("Found 150 duplicates", "success")
    time.sleep(0.3)
    show_status("Backup recommended before deletion", "warning")
    time.sleep(0.3)
    show_status("All checks passed", "success")

    console.print("\n[bold green]✓ Demo complete![/bold green]\n")
