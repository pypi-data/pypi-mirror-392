import typer
from pkg_guard.core.installer import handle_install_command
from pkg_guard.ui.console import console

app = typer.Typer(help="pkg-guard: safer pip installs with typo detection")

@app.command("install")
def install_command(
    packages: list[str] = typer.Argument(..., help="Package names to install"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-confirm suggested install"),
):
    """Detects typos, suggests alternatives, and safely installs packages."""
    if not packages:
        console.print("[red]Error:[/red] No packages provided.")
        raise typer.Exit(code=1)

    # Clean up noisy tokens (pip, install)
    noise = {"pip", "install"}
    while packages and packages[0].lower() in noise:
        packages = packages[1:]

    if not packages:
        console.print("[yellow]Nothing to install after filtering 'pip/install' tokens.[/yellow]")
        raise typer.Exit()

    handle_install_command(packages, yes)
