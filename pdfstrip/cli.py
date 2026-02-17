from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from pdfstrip.core import UnlockResult, UnlockStatus, collect_pdf_files, unlock_pdf
from pdfstrip.output import (
    confirm,
    console,
    create_progress,
    print_result,
    print_summary,
    prompt_password,
)

app = typer.Typer(add_completion=False)


def _validate_options(
    output: Path | None,
    output_dir: Path | None,
    in_place: bool,
) -> None:
    set_count = sum([output is not None, output_dir is not None, in_place])
    if set_count > 1:
        console.print("[red]Error:[/] --output, --output-dir, and --in-place are mutually exclusive")
        raise typer.Exit(1)


@app.command()
def main(
    files: Annotated[list[Path], typer.Argument(help="PDF files or directories to unlock")],
    password: Annotated[Optional[str], typer.Option("--password", "-p", help="PDF password")] = None,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path (single file only)")] = None,
    output_dir: Annotated[Optional[Path], typer.Option("--output-dir", "-d", help="Output directory for unlocked files")] = None,
    in_place: Annotated[bool, typer.Option("--in-place", "-i", help="Overwrite original files")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite existing output files")] = False,
    skip_unprotected: Annotated[bool, typer.Option("--skip-unprotected", "-s", help="Skip files that are not encrypted")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n", help="Show what would be done without writing")] = False,
) -> None:
    """Remove passwords from PDF files."""
    _validate_options(output, output_dir, in_place)

    pdf_files = collect_pdf_files(files)
    if not pdf_files:
        console.print("[yellow]No PDF files found.[/]")
        raise typer.Exit(0)

    if output is not None and len(pdf_files) > 1:
        console.print("[red]Error:[/] --output can only be used with a single file")
        raise typer.Exit(1)

    if in_place and not dry_run:
        if not confirm("Overwrite original files?"):
            raise typer.Exit(0)

    if password is None:
        password = prompt_password()

    batch = len(pdf_files) > 1
    results: list[UnlockResult] = []

    if batch:
        progress = create_progress()
        with progress:
            task = progress.add_task("Unlocking", total=len(pdf_files))
            for f in pdf_files:
                result = unlock_pdf(
                    f,
                    password,
                    output=None,
                    output_dir=output_dir,
                    in_place=in_place,
                    dry_run=dry_run,
                    force=force,
                    skip_unprotected=skip_unprotected,
                )
                results.append(result)
                progress.advance(task)
        for r in results:
            print_result(r)
        print_summary(results)
    else:
        result = unlock_pdf(
            pdf_files[0],
            password,
            output=output,
            output_dir=output_dir,
            in_place=in_place,
            dry_run=dry_run,
            force=force,
            skip_unprotected=skip_unprotected,
        )
        results.append(result)
        print_result(result)

    if any(r.status in {UnlockStatus.WRONG_PASSWORD, UnlockStatus.FILE_NOT_FOUND, UnlockStatus.ERROR, UnlockStatus.OUTPUT_EXISTS} for r in results):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
