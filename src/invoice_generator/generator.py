"""
Public API for generating demo invoice PDFs.
"""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from src.invoice_generator.templates import render_invoice_pdf
from src.invoice_generator.utils import (
    compute_subtotal,
    random_company,
    random_invoice_date,
    random_invoice_number,
    random_line_items,
)


def _build_invoice_payload(seq: int) -> dict:
    """Assemble structured invoice data used by the PDF template."""
    line_items = random_line_items()
    return {
        "invoice_number": random_invoice_number(seq),
        "date": random_invoice_date().isoformat(),
        "from": random_company(),
        "bill_to": random_company(),
        "line_items": line_items,
        "subtotal": compute_subtotal(line_items),
    }


def generate_invoices(
    output_folder: str | Path,
    count: int,
    *,
    show_progress: bool = True,
    start_index: int = 1,
) -> list[Path]:
    """
    Generate ``count`` realistic invoice PDFs into ``output_folder``.

    Args:
        output_folder: Destination directory for PDF files.
        count: Number of invoices to generate.
        show_progress: Whether to display a tqdm progress bar.
        start_index: Starting sequence number for invoice IDs / filenames.

    Returns:
        List of paths to the generated PDF files.
    """
    if count < 1:
        raise ValueError("count must be >= 1")

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    iterator = range(start_index, start_index + count)
    if show_progress:
        iterator = tqdm(iterator, desc="Generating invoices", unit="pdf")

    for seq in iterator:
        invoice = _build_invoice_payload(seq)
        filename = f"{invoice['invoice_number']}.pdf"
        pdf_path = output_path / filename
        render_invoice_pdf(pdf_path, invoice)
        generated.append(pdf_path)

    return generated
