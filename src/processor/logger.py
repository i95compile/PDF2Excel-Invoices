"""
Logging utilities for InvoiceFlow.

Provides console + rotating file handlers under ``logs/``.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import config as root_config

_CONFIGURED = False


def setup_logging(
    name: str = "invoiceflow",
    level: str | None = None,
    log_dir: Path | None = None,
) -> logging.Logger:
    """
    Configure and return the application logger.

    Safe to call multiple times; subsequent calls return the existing logger.
    """
    global _CONFIGURED

    logger = logging.getLogger(name)
    if _CONFIGURED:
        return logger

    resolved_level = getattr(
        logging, (level or root_config.LOG_LEVEL).upper(), logging.INFO
    )
    logger.setLevel(resolved_level)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(resolved_level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    directory = Path(log_dir or root_config.LOG_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        directory / "invoiceflow.log",
        maxBytes=root_config.LOG_MAX_BYTES,
        backupCount=root_config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(resolved_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _CONFIGURED = True
    return logger


def get_logger(name: str = "invoiceflow") -> logging.Logger:
    """Return a named logger, ensuring setup has run."""
    if not _CONFIGURED:
        return setup_logging(name=name)
    return logging.getLogger(name)
