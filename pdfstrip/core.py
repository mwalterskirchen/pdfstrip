from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pikepdf


class UnlockStatus(Enum):
    SUCCESS = "success"
    ALREADY_UNLOCKED = "already_unlocked"
    WRONG_PASSWORD = "wrong_password"
    FILE_NOT_FOUND = "file_not_found"
    OUTPUT_EXISTS = "output_exists"
    ERROR = "error"


@dataclass(frozen=True)
class UnlockResult:
    source: Path
    destination: Path | None
    status: UnlockStatus
    message: str


def is_encrypted(path: Path) -> bool:
    """Check if a PDF file is password-protected."""
    try:
        with pikepdf.open(path):
            return False
    except pikepdf.PasswordError:
        return True


def collect_pdf_files(paths: list[Path]) -> list[Path]:
    """Expand directories to *.pdf (non-recursive), pass files through."""
    result: list[Path] = []
    for p in paths:
        if p.is_dir():
            result.extend(sorted(p.glob("*.pdf")))
        else:
            result.append(p)
    return result


def resolve_output_path(
    source: Path,
    *,
    output: Path | None = None,
    output_dir: Path | None = None,
    in_place: bool = False,
) -> Path:
    """Determine the destination path for an unlocked PDF."""
    if output is not None:
        return output
    if output_dir is not None:
        return output_dir / source.name
    if in_place:
        return source
    # Default: <name>_unlocked.pdf in the same directory
    return source.with_stem(f"{source.stem}_unlocked")


def unlock_pdf(
    source: Path,
    password: str,
    *,
    output: Path | None = None,
    output_dir: Path | None = None,
    in_place: bool = False,
    dry_run: bool = False,
    force: bool = False,
    skip_unprotected: bool = False,
) -> UnlockResult:
    """Unlock a single PDF file. Returns a structured result."""
    if not source.exists():
        return UnlockResult(source, None, UnlockStatus.FILE_NOT_FOUND, "File not found")

    if not is_encrypted(source):
        if skip_unprotected:
            return UnlockResult(source, None, UnlockStatus.ALREADY_UNLOCKED, "Skipped (not encrypted)")
        return UnlockResult(source, None, UnlockStatus.ALREADY_UNLOCKED, "File is not encrypted")

    dest = resolve_output_path(source, output=output, output_dir=output_dir, in_place=in_place)

    if not in_place and dest.exists() and not force:
        return UnlockResult(source, dest, UnlockStatus.OUTPUT_EXISTS, f"Output already exists: {dest}")

    if dry_run:
        return UnlockResult(source, dest, UnlockStatus.SUCCESS, "Would unlock (dry run)")

    try:
        with pikepdf.open(source, password=password) as pdf:
            # Write to a temp file in the same directory, then move into place.
            # pikepdf cannot overwrite its own input while the handle is open.
            fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=dest.parent)
            try:
                pdf.save(tmp)
            except Exception:
                Path(tmp).unlink(missing_ok=True)
                raise
        # Handle is closed — safe to move now.
        shutil.move(tmp, dest)
    except pikepdf.PasswordError:
        return UnlockResult(source, dest, UnlockStatus.WRONG_PASSWORD, "Wrong password")
    except Exception as exc:
        return UnlockResult(source, dest, UnlockStatus.ERROR, str(exc))

    return UnlockResult(source, dest, UnlockStatus.SUCCESS, f"Unlocked → {dest}")
