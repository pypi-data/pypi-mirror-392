import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pkg_guard.core.pypi_utils import pypi_exists, load_popular, suggest_names
from pkg_guard.ui.console import console, spinner
from pkg_guard.ui.prompts import choose_package
from InquirerPy import inquirer

POPULAR_PATH = Path(__file__).parent.parent / "popular_packages.txt"


def check_packages_concurrently(packages):
    """Concurrent check for existence on PyPI."""
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(pypi_exists, pkg): pkg for pkg in packages}
        for future in as_completed(futures):
            pkg = futures[future]
            results[pkg] = future.result()
    return results


def safe_install(package: str):
    """Runs pip install safely."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        console.print(f"[green]✔ Successfully installed:[/green] {package}")
    except subprocess.CalledProcessError:
        console.print(f"[red]✖ Installation failed for:[/red] {package}")
    except Exception as e:
        console.print(f"[red]Unexpected error installing {package}:[/red] {e}")


def handle_install_command(packages: list[str], yes: bool):
    """Main logic for install command."""
    with spinner("Checking PyPI for packages..."):
        results = check_packages_concurrently(packages)

    population = None  # Lazy-load for efficiency

    for pkg, exists in results.items():
        console.rule(f"[bold cyan]Processing {pkg}[/bold cyan]", style="dim")

        if exists:
            console.print(f"[green]✔ Found on PyPI:[/green] [bold]{pkg}[/bold]")
            console.print(f"[dim]Safe to run: pip install {pkg}[/dim]")

            if not yes:
                try:
                    confirm = inquirer.confirm(
                        message=f"Install '{pkg}' now?",
                        default=True,
                        qmark="✔",
                    ).execute()
                except KeyboardInterrupt:
                    console.print("\n[yellow]Cancelled by user.[/yellow]")
                    return

                if not confirm:
                    console.print("[yellow]Skipped.[/yellow]\n")
                    continue

            console.print(f"[bold]Running:[/bold] pip install {pkg}")
            safe_install(pkg)
            console.print()
            continue

        # Package not found
        console.print(f"[red]✖ Not found on PyPI:[/red] [bold]{pkg}[/bold]")

        if population is None:
            population = load_popular(POPULAR_PATH)

        suggestions = suggest_names(pkg, population, limit=6)

        if yes and suggestions:
            best = suggestions[0][0]
            console.print(f"[green]Auto-installing best match:[/green] {best}")
            safe_install(best)
            continue
        elif yes:
            console.print("[yellow]No suggestions found to auto-install.[/yellow]")
            continue

        choice = choose_package(pkg, suggestions)
        if not choice:
            console.print("[yellow]Skipped.[/yellow]\n")
            continue

        with spinner(f"Verifying {choice} on PyPI..."):
            if not pypi_exists(choice):
                console.print(f"[red]The chosen package '{choice}' not found on PyPI. Skipping.[/red]")
                continue

        safe_install(choice)

    console.print("\n[green] All requested packages processed.[/green]")
