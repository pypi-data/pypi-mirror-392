from InquirerPy import inquirer
from pkg_guard.ui.console import console

def choose_package(original: str, suggestions: list[tuple]) -> str | None:
    """Interactive fuzzy prompt for choosing suggested packages."""
    if not suggestions:
        choice = inquirer.text(
            message=f"No suggestions for '{original}'. Enter a package name (or blank to skip):"
        ).execute()
        return choice.strip() or None

    suggestion_names = [match for match, _, _ in suggestions]
    suggestion_names.append("Other (type manually)")
    suggestion_names.append("Skip")

    choice = inquirer.select(
        message=f"Select package to install instead of '{original}':",
        choices=suggestion_names,
        default=suggestion_names[0],
        pointer="▸",
        qmark="?",
    ).execute()

    if choice == "Other (type manually)":
        choice = inquirer.text(
            message="Enter package name manually:",
            validate=lambda result: len(result.strip()) > 0 or "Package name cannot be empty",
        ).execute()
        return choice.strip()

    if choice == "Skip":
        console.print("[yellow]Skipped this package.[/yellow]")
        return None

    return choice.strip()
