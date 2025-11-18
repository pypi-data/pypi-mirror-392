import typer
import requests
import json
import time
from pathlib import Path
from rich.progress import Progress
from appdirs import user_cache_dir

from pkg_guard.core.installer import handle_install_command
from pkg_guard.ui.console import console

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
POPULAR_PATH = Path(__file__).parent / "popular_packages.txt"
TOP_PYPI_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.json"

# User-level cache directory (cross-platform safe)
CACHE_DIR = Path(user_cache_dir("pkg-guard"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
META_PATH = CACHE_DIR / "popular_packages.meta.json"

# ---------------------------------------------------------------------
# Typer App
# ---------------------------------------------------------------------
app = typer.Typer(help="pkg-guard: safer pip installs with typo detection")

# ---------------------------------------------------------------------
# install command
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# update-popular command
# ---------------------------------------------------------------------
@app.command("update-popular")
def update_popular(
    limit: int = 200,
    force: bool = typer.Option(False, "--force", "-f", help="Force refresh even if list was updated recently."),
):
    """
    🔄 Update the local 'popular_packages.txt' file with the latest
    top PyPI packages (from https://hugovk.github.io/top-pypi-packages/).

    Example:
      pkg-guard update-popular
      pkg-guard update-popular --force
    """
    console.print("[bold cyan]Fetching latest top PyPI packages...[/bold cyan]")

    try:
        # -----------------------------------------------------------------
        # 1. Check if recently updated (30 days freshness)
        # -----------------------------------------------------------------
        if not force and META_PATH.exists():
            meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            last = meta.get("last_update", 0)
            if time.time() - last < 86400 * 30:  # 30 days
                console.print("[dim]Using cached popular_packages.txt (last updated within 30 days).[/dim]")
                console.print("[dim]Use --force to refresh immediately.[/dim]")
                return

        # -----------------------------------------------------------------
        # 2. Fetch new data from PyPI
        # -----------------------------------------------------------------
        with Progress() as progress:
            task = progress.add_task("[green]Updating list...", total=1)
            response = requests.get(TOP_PYPI_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            progress.advance(task)

        rows = data.get("rows", [])
        top = [row["project"] for row in rows[:limit]]

        # -----------------------------------------------------------------
        # 3. Save updated files
        # -----------------------------------------------------------------
        POPULAR_PATH.write_text("\n".join(top), encoding="utf-8")
        META_PATH.write_text(json.dumps({"last_update": time.time()}))

        console.print(f"[green]✅ Updated {len(top)} popular packages.[/green]")
        console.print(f"[dim]File saved at:[/dim] {POPULAR_PATH}")
        console.print(f"[dim]Metadata stored in:[/dim] {META_PATH}")

    except requests.RequestException as e:
        console.print(f"[red]✖ Failed to fetch top packages:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
