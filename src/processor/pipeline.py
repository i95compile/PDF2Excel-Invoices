"""
High-level processing pipeline.

Orchestrates discovery → workers → Excel export. CLI and benchmarks
should call ``process_invoices`` rather than wiring pieces manually.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.processor.config import ProcessorConfig
from src.processor.excel_writer import write_excel
from src.processor.logger import get_logger
from src.processor.models import InvoiceData
from src.processor.utils import list_pdf_files
from src.processor.worker import run_workers

logger = get_logger(__name__)


def process_invoices(
    input_dir: str | Path,
    output_file: str | Path,
    *,
    workers: str | int = "auto",
    mode: str | None = None,
    show_progress: bool = True,
) -> list[InvoiceData]:
    """
    Process every PDF in ``input_dir`` and write an Excel workbook.

    Args:
        input_dir: Folder containing invoice PDFs.
        output_file: Destination ``.xlsx`` path.
        workers: ``auto`` or an integer worker count.
        mode: ``sequential`` or ``multiprocessing`` (auto-selected when None).
        show_progress: Whether to show tqdm progress bars.

    Returns:
        List of ``InvoiceData`` results (including partial failures).
    """
    cfg = ProcessorConfig.from_cli(
        input_dir=input_dir,
        output_file=output_file,
        workers=workers,
        mode=mode,
        show_progress=show_progress,
    )

    pdf_files = list_pdf_files(cfg.input_dir)
    logger.info(
        "Found %s PDF(s) in %s | mode=%s workers=%s",
        len(pdf_files),
        cfg.input_dir,
        cfg.mode,
        cfg.workers,
    )

    if not pdf_files:
        logger.warning("No PDF files found — writing empty workbook")
        write_excel([], cfg.output_file)
        return []

    invoices = run_workers(
        pdf_files,
        workers=cfg.workers,
        mode=cfg.mode,
        show_progress=cfg.show_progress,
    )

    write_excel(invoices, cfg.output_file)
    _log_summary(invoices, cfg.output_file)
    return invoices


def _log_summary(invoices: Sequence[InvoiceData], output_file: Path) -> None:
    failures = sum(1 for inv in invoices if inv.errors)
    logger.info(
        "Completed: %s invoice(s), %s with errors → %s",
        len(invoices),
        failures,
        output_file,
    )
