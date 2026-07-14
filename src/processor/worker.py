"""
Worker pool for sequential and multiprocessing invoice extraction.

``process_single_invoice`` is module-level so it can be pickled by
``ProcessPoolExecutor`` on all platforms (including Windows spawn).
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable, Optional

from tqdm import tqdm

from src.processor.extractor import BaseExtractor, get_default_extractor
from src.processor.logger import get_logger
from src.processor.models import InvoiceData

logger = get_logger(__name__)


def process_single_invoice(pdf_path: str) -> dict:
    """
    Worker entrypoint: extract one PDF and return a serializable dict.

    Uses the default text extractor. Kept free of non-picklable state.
    """
    extractor = get_default_extractor()
    invoice = extractor.extract(pdf_path)
    return {
        "header": invoice.to_flat_dict(),
        "line_items": invoice.line_items_as_rows(),
        "raw": {
            "source_file": invoice.source_file,
            "invoice_number": invoice.invoice_number,
            "date": invoice.date,
            "bill_to": invoice.bill_to,
            "from_party": invoice.from_party,
            "subtotal": invoice.subtotal,
            "extraction_method": invoice.extraction_method,
            "confidence": invoice.confidence,
            "errors": invoice.errors,
            "line_items": [li.to_dict() for li in invoice.line_items],
        },
    }


def run_sequential(
    pdf_files: Iterable[Path],
    *,
    show_progress: bool = True,
) -> list[InvoiceData]:
    """Process PDFs one-by-one in the current process."""
    results: list[InvoiceData] = []
    files = list(pdf_files)
    iterator = tqdm(files, desc="Processing (sequential)", unit="pdf") if show_progress else files

    for pdf in iterator:
        payload = process_single_invoice(str(pdf))
        results.append(_dict_to_invoice(payload["raw"]))

    return results


def run_multiprocessing(
    pdf_files: Iterable[Path],
    workers: int,
    *,
    show_progress: bool = True,
) -> list[InvoiceData]:
    """
    Process PDFs with ``ProcessPoolExecutor``.

    Args:
        pdf_files: Paths to process.
        workers: Number of worker processes.
        show_progress: Display a tqdm progress bar.
    """
    files = [str(p) for p in pdf_files]
    results: list[InvoiceData] = []

    if not files:
        return results

    logger.info("Starting ProcessPoolExecutor with %s workers", workers)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_single_invoice, path): path for path in files
        }
        iterator = as_completed(futures)
        if show_progress:
            iterator = tqdm(
                iterator,
                total=len(futures),
                desc=f"Processing ({workers} workers)",
                unit="pdf",
            )

        for future in iterator:
            path = futures[future]
            try:
                payload = future.result()
                results.append(_dict_to_invoice(payload["raw"]))
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed processing %s: %s", path, exc)
                results.append(
                    InvoiceData(
                        source_file=Path(path).name,
                        errors=[f"worker_failed: {exc}"],
                    )
                )

    return results


def run_workers(
    pdf_files: list[Path],
    *,
    workers: int = 1,
    mode: str = "sequential",
    show_progress: bool = True,
    extractor_factory: Optional[Callable[[], BaseExtractor]] = None,
) -> list[InvoiceData]:
    """
    Dispatch to sequential or multiprocessing backends.

    ``extractor_factory`` is reserved for future custom extractors in
    sequential mode; multiprocessing continues to use the default picklable
    worker until a remote/custom registry is added.

    TODO: Support injecting custom extractors into worker processes via
          import-path strings for OCR/AI backends.
    """
    _ = extractor_factory  # reserved

    if mode == "multiprocessing" and workers > 1:
        return run_multiprocessing(
            pdf_files, workers=workers, show_progress=show_progress
        )
    return run_sequential(pdf_files, show_progress=show_progress)


def _dict_to_invoice(raw: dict) -> InvoiceData:
    from src.processor.models import LineItem

    return InvoiceData(
        source_file=raw["source_file"],
        invoice_number=raw.get("invoice_number"),
        date=raw.get("date"),
        bill_to=raw.get("bill_to"),
        from_party=raw.get("from_party"),
        subtotal=raw.get("subtotal"),
        line_items=[LineItem(**li) for li in raw.get("line_items", [])],
        extraction_method=raw.get("extraction_method", "text"),
        confidence=raw.get("confidence"),
        errors=list(raw.get("errors") or []),
    )
