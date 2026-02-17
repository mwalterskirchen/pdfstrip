# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pdfstrip is a CLI tool that removes passwords from PDF files. Built with pikepdf, Typer, and Rich. Managed with `uv`.

## Commands

- **Run**: `uv run pdfstrip <files> -p <password>`
- **Help**: `uv run pdfstrip --help`
- **Tests**: `uv run pytest`
- **Single test**: `uv run pytest tests/test_core.py::TestUnlockPdf::test_success`
- **Sync deps**: `uv sync`
- **Add dep**: `uv add <package>`
- **Install globally**: `uv tool install -e .`

## Architecture

Three-module split with strict import boundaries:

- **`core.py`** — Pure logic, no CLI or Rich imports. Every `unlock_pdf()` call returns a frozen `UnlockResult` dataclass (never raises). This makes batch processing trivial — collect results, then render.
- **`output.py`** — Rich rendering (progress bar, colored results, summary table, password prompt). Imports from core only.
- **`cli.py`** — Typer app that wires core + output together. Handles argument parsing, validation, single vs batch dispatch.

Key patterns:
- In-place unlock uses tempfile + `shutil.move()` because pikepdf can't overwrite its input while open.
- Directory expansion is non-recursive (`*.pdf` glob, not `**/*.pdf`).
- `--output`, `--output-dir`, and `--in-place` are mutually exclusive; validated before any work starts.
- Password prompt is deferred until after file validation.

## Tests

Test fixtures in `conftest.py` generate real encrypted/unencrypted PDFs with pikepdf. CLI tests use `typer.testing.CliRunner`.
