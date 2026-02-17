from __future__ import annotations

from pathlib import Path

from pdfstrip.core import (
    UnlockStatus,
    collect_pdf_files,
    is_encrypted,
    resolve_output_path,
    unlock_pdf,
)


class TestIsEncrypted:
    def test_encrypted(self, protected_pdf: Path) -> None:
        assert is_encrypted(protected_pdf) is True

    def test_not_encrypted(self, unprotected_pdf: Path) -> None:
        assert is_encrypted(unprotected_pdf) is False


class TestCollectPdfFiles:
    def test_directory_expansion(self, batch_dir: Path) -> None:
        files = collect_pdf_files([batch_dir])
        assert len(files) == 4
        assert all(f.suffix == ".pdf" for f in files)

    def test_single_file(self, protected_pdf: Path) -> None:
        files = collect_pdf_files([protected_pdf])
        assert files == [protected_pdf]

    def test_mixed(self, protected_pdf: Path, batch_dir: Path) -> None:
        files = collect_pdf_files([protected_pdf, batch_dir])
        assert len(files) == 5


class TestResolveOutputPath:
    def test_default(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.pdf"
        dest = resolve_output_path(src)
        assert dest == tmp_path / "doc_unlocked.pdf"

    def test_explicit_output(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.pdf"
        out = tmp_path / "out.pdf"
        assert resolve_output_path(src, output=out) == out

    def test_output_dir(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.pdf"
        d = tmp_path / "outdir"
        assert resolve_output_path(src, output_dir=d) == d / "doc.pdf"

    def test_in_place(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.pdf"
        assert resolve_output_path(src, in_place=True) == src


class TestUnlockPdf:
    def test_success(self, protected_pdf: Path) -> None:
        result = unlock_pdf(protected_pdf, "pass123")
        assert result.status == UnlockStatus.SUCCESS
        assert result.destination is not None
        assert result.destination.exists()

    def test_wrong_password(self, protected_pdf: Path) -> None:
        result = unlock_pdf(protected_pdf, "wrong")
        assert result.status == UnlockStatus.WRONG_PASSWORD

    def test_already_unlocked(self, unprotected_pdf: Path) -> None:
        result = unlock_pdf(unprotected_pdf, "pass123")
        assert result.status == UnlockStatus.ALREADY_UNLOCKED

    def test_file_not_found(self, tmp_path: Path) -> None:
        result = unlock_pdf(tmp_path / "missing.pdf", "pass123")
        assert result.status == UnlockStatus.FILE_NOT_FOUND

    def test_in_place(self, protected_pdf: Path) -> None:
        result = unlock_pdf(protected_pdf, "pass123", in_place=True)
        assert result.status == UnlockStatus.SUCCESS
        assert result.destination == protected_pdf
        assert not is_encrypted(protected_pdf)

    def test_dry_run(self, protected_pdf: Path) -> None:
        result = unlock_pdf(protected_pdf, "pass123", dry_run=True)
        assert result.status == UnlockStatus.SUCCESS
        assert "dry run" in result.message
        # Original file should still be encrypted
        assert is_encrypted(protected_pdf)

    def test_output_exists_no_force(self, protected_pdf: Path) -> None:
        dest = protected_pdf.with_stem(f"{protected_pdf.stem}_unlocked")
        dest.write_bytes(b"existing")
        result = unlock_pdf(protected_pdf, "pass123")
        assert result.status == UnlockStatus.OUTPUT_EXISTS

    def test_output_exists_force(self, protected_pdf: Path) -> None:
        dest = protected_pdf.with_stem(f"{protected_pdf.stem}_unlocked")
        dest.write_bytes(b"existing")
        result = unlock_pdf(protected_pdf, "pass123", force=True)
        assert result.status == UnlockStatus.SUCCESS

    def test_skip_unprotected(self, unprotected_pdf: Path) -> None:
        result = unlock_pdf(unprotected_pdf, "pass123", skip_unprotected=True)
        assert result.status == UnlockStatus.ALREADY_UNLOCKED
        assert "Skipped" in result.message

    def test_output_dir(self, protected_pdf: Path, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        result = unlock_pdf(protected_pdf, "pass123", output_dir=out_dir)
        assert result.status == UnlockStatus.SUCCESS
        assert result.destination == out_dir / protected_pdf.name

    def test_explicit_output(self, protected_pdf: Path, tmp_path: Path) -> None:
        out = tmp_path / "result.pdf"
        result = unlock_pdf(protected_pdf, "pass123", output=out)
        assert result.status == UnlockStatus.SUCCESS
        assert result.destination == out
        assert out.exists()
