# pdfstrip

A fast CLI tool to remove passwords from PDF files. Handles single files or entire directories, with a progress bar for batch jobs and colored output.

You know the password but the PDF asks for it every time you open it? `pdfstrip` strips the encryption and gives you a clean, password-free copy.

## Install

```bash
pipx install pdfstrip
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install pdfstrip
```

## Usage

```bash
# Unlock a single file (writes secret_unlocked.pdf)
pdfstrip secret.pdf -p mypassword

# Unlock to a specific path
pdfstrip secret.pdf -p mypassword -o unlocked.pdf

# Unlock in place (overwrites the original)
pdfstrip secret.pdf -p mypassword --in-place

# Batch unlock all PDFs in a directory
pdfstrip ./pdfs/ -p mypassword --skip-unprotected

# Preview what would happen without writing anything
pdfstrip secret.pdf -p mypassword --dry-run
```

If you omit `-p`, pdfstrip will prompt for the password interactively (hidden input).

## Options

| Flag | Short | Description |
|------|-------|-------------|
| `--password` | `-p` | PDF password |
| `--output` | `-o` | Output file path (single file only) |
| `--output-dir` | `-d` | Output directory for unlocked files |
| `--in-place` | `-i` | Overwrite original files |
| `--force` | `-f` | Overwrite existing output files |
| `--skip-unprotected` | `-s` | Skip files that are not encrypted |
| `--dry-run` | `-n` | Show what would be done without writing |

## Development

```bash
git clone https://github.com/mwalterskirchen/pdfstrip.git
cd pdfstrip
uv sync
uv run pytest
```

## License

MIT
