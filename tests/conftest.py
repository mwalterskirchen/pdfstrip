from __future__ import annotations

from pathlib import Path

import pikepdf
import pytest


def _make_pdf(path: Path, *, password: str | None = None) -> Path:
    """Create a minimal PDF, optionally password-protected."""
    pdf = pikepdf.new()
    pdf.add_blank_page(page_size=(200, 200))
    encryption = pikepdf.Encryption(owner=password, user=password) if password else None
    pdf.save(path, encryption=encryption)
    pdf.close()
    return path


@pytest.fixture()
def protected_pdf(tmp_path: Path) -> Path:
    return _make_pdf(tmp_path / "secret.pdf", password="pass123")


@pytest.fixture()
def unprotected_pdf(tmp_path: Path) -> Path:
    return _make_pdf(tmp_path / "open.pdf")


@pytest.fixture()
def batch_dir(tmp_path: Path) -> Path:
    d = tmp_path / "batch"
    d.mkdir()
    _make_pdf(d / "a.pdf", password="pass123")
    _make_pdf(d / "b.pdf", password="pass123")
    _make_pdf(d / "c.pdf", password="pass123")
    _make_pdf(d / "open.pdf")
    return d
