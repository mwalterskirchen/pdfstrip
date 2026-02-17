# pdfstrip

Remove passwords from PDF files.

## Install

```bash
pipx install pdfstrip
```

Or with `uv`:

```bash
uv tool install pdfstrip
```

## Usage

```bash
# Unlock a single file
pdfstrip secret.pdf -p mypassword

# Unlock to a specific output
pdfstrip secret.pdf -p mypassword -o unlocked.pdf

# Unlock in place
pdfstrip secret.pdf -p mypassword --in-place

# Batch unlock a directory
pdfstrip ./pdfs/ -p mypassword --skip-unprotected

# Dry run
pdfstrip secret.pdf -p mypassword --dry-run
```

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
