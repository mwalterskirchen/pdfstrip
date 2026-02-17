from __future__ import annotations

from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn
from rich.table import Table

from pdfstrip.core import UnlockResult, UnlockStatus

console = Console()

STATUS_STYLES: dict[UnlockStatus, tuple[str, str]] = {
    UnlockStatus.SUCCESS: ("green", "Unlocked"),
    UnlockStatus.ALREADY_UNLOCKED: ("yellow", "Already unlocked"),
    UnlockStatus.WRONG_PASSWORD: ("red", "Wrong password"),
    UnlockStatus.FILE_NOT_FOUND: ("red", "Not found"),
    UnlockStatus.OUTPUT_EXISTS: ("red", "Output exists"),
    UnlockStatus.ERROR: ("red", "Error"),
}


def create_progress() -> Progress:
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=console,
    )


def print_result(result: UnlockResult) -> None:
    color, label = STATUS_STYLES[result.status]
    console.print(f"[{color}]{label}[/] {result.source} — {result.message}")


def print_summary(results: list[UnlockResult]) -> None:
    counts: dict[UnlockStatus, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1

    table = Table(title="Summary")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")

    for status, (color, label) in STATUS_STYLES.items():
        count = counts.get(status, 0)
        if count:
            table.add_row(f"[{color}]{label}[/]", str(count))

    console.print(table)


def confirm(message: str) -> bool:
    answer = console.input(f"{message} [y/N] ")
    return answer.strip().lower() == "y"


def prompt_password() -> str:
    return console.input("[bold]Password: [/]", password=True)
