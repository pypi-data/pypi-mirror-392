from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from contextlib import contextmanager

console = Console()

@contextmanager
def spinner(message: str):
    """Context manager for consistent spinners."""
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{message}[/cyan]"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("", total=None)
        yield
        progress.remove_task(task)
