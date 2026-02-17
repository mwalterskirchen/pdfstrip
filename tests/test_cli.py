from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from pdfstrip.cli import app

runner = CliRunner()


class TestCliSingleFile:
    def test_unlock(self, protected_pdf: Path) -> None:
        result = runner.invoke(app, [str(protected_pdf), "-p", "pass123"])
        assert result.exit_code == 0
        assert "Unlocked" in result.output

    def test_wrong_password(self, protected_pdf: Path) -> None:
        result = runner.invoke(app, [str(protected_pdf), "-p", "wrong"])
        assert result.exit_code == 1
        assert "Wrong password" in result.output

    def test_unprotected(self, unprotected_pdf: Path) -> None:
        result = runner.invoke(app, [str(unprotected_pdf), "-p", "pass123"])
        assert result.exit_code == 0
        assert "not encrypted" in result.output

    def test_dry_run(self, protected_pdf: Path) -> None:
        result = runner.invoke(app, [str(protected_pdf), "-p", "pass123", "--dry-run"])
        assert result.exit_code == 0
        assert "dry run" in result.output

    def test_in_place(self, protected_pdf: Path) -> None:
        result = runner.invoke(app, [str(protected_pdf), "-p", "pass123", "--in-place"], input="y\n")
        assert result.exit_code == 0
        assert "Unlocked" in result.output


class TestCliBatch:
    def test_directory(self, batch_dir: Path) -> None:
        result = runner.invoke(app, [str(batch_dir), "-p", "pass123", "--skip-unprotected"])
        assert result.exit_code == 0
        assert "Summary" in result.output

    def test_dry_run(self, batch_dir: Path) -> None:
        result = runner.invoke(app, [str(batch_dir), "-p", "pass123", "--dry-run"])
        assert result.exit_code == 0
        assert "dry run" in result.output


class TestCliValidation:
    def test_mutually_exclusive(self, protected_pdf: Path) -> None:
        result = runner.invoke(app, [str(protected_pdf), "-p", "pass", "--in-place", "-o", "out.pdf"], input="y\n")
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output

    def test_output_with_multiple_files(self, batch_dir: Path) -> None:
        result = runner.invoke(app, [str(batch_dir), "-p", "pass", "-o", "out.pdf"])
        assert result.exit_code == 1
        assert "single file" in result.output
