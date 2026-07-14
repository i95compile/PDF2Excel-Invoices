"""Generic filesystem / parsing helpers for the processor."""

from __future__ import annotations

import re
from pathlib import Path


def list_pdf_files(directory: str | Path) -> list[Path]:
    """Return sorted PDF paths in ``directory`` (non-recursive)."""
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"Input directory not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {path}")
    return sorted(path.glob("*.pdf"))


def parse_money(value: str) -> float | None:
    """Parse a currency-like string into a float."""
    if not value:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", value.replace(",", ""))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def first_match(pattern: str, text: str, flags: int = re.IGNORECASE) -> str | None:
    """Return the first regex group match, or None."""
    match = re.search(pattern, text, flags)
    if not match:
        return None
    if match.lastindex:
        return match.group(1).strip()
    return match.group(0).strip()
