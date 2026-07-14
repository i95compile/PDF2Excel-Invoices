"""
Root-level configuration for InvoiceFlow.

Loads settings from environment variables and an optional ``.env`` file.
Processor-specific settings live under ``src.processor.config``.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Resolve project root (directory containing this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent

# Load .env if present (does not override existing env vars)
load_dotenv(PROJECT_ROOT / ".env")


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = _env("LOG_LEVEL", "INFO")
LOG_DIR: Path = PROJECT_ROOT / _env("LOG_DIR", "logs")
LOG_MAX_BYTES: int = _env_int("LOG_MAX_BYTES", 1_048_576)
LOG_BACKUP_COUNT: int = _env_int("LOG_BACKUP_COUNT", 5)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_INPUT_DIR: Path = PROJECT_ROOT / _env("DEFAULT_INPUT_DIR", "invoices")
DEFAULT_OUTPUT_DIR: Path = PROJECT_ROOT / _env("DEFAULT_OUTPUT_DIR", "output")
DEFAULT_OUTPUT_FILE: Path = PROJECT_ROOT / _env(
    "DEFAULT_OUTPUT_FILE", "output/invoices.xlsx"
)
BENCHMARK_DIR: Path = PROJECT_ROOT / _env("BENCHMARK_DIR", "benchmarks")

# ---------------------------------------------------------------------------
# Processor defaults
# ---------------------------------------------------------------------------
WORKERS: str = _env("WORKERS", "auto")
PROCESSING_MODE: str = _env("PROCESSING_MODE", "multiprocessing")

EXCEL_SHEET_INVOICES: str = _env("EXCEL_SHEET_INVOICES", "Invoices")
EXCEL_SHEET_LINE_ITEMS: str = _env("EXCEL_SHEET_LINE_ITEMS", "LineItems")


def ensure_runtime_directories() -> None:
    """Create standard runtime directories if they do not exist."""
    for directory in (
        LOG_DIR,
        DEFAULT_INPUT_DIR,
        DEFAULT_OUTPUT_DIR,
        BENCHMARK_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
