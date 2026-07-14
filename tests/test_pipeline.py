"""
Integration-style tests for the processing pipeline.

These generate a tiny invoice set then extract + export.
"""

from __future__ import annotations

from pathlib import Path

from src.invoice_generator import generate_invoices
from src.processor.excel_writer import write_excel
from src.processor.extractor import TextExtractor
from src.processor.pipeline import process_invoices


def test_extract_generated_invoice(tmp_path: Path) -> None:
    generate_invoices(tmp_path, count=1, show_progress=False, start_index=42)
    pdf = next(tmp_path.glob("*.pdf"))
    invoice = TextExtractor().extract(pdf)

    assert invoice.invoice_number is not None
    assert invoice.date is not None
    assert invoice.from_party is not None
    assert invoice.bill_to is not None
    assert invoice.subtotal is not None
    assert len(invoice.line_items) >= 1


def test_process_invoices_end_to_end(tmp_path: Path) -> None:
    invoices_dir = tmp_path / "invoices"
    output = tmp_path / "out" / "result.xlsx"
    generate_invoices(invoices_dir, count=3, show_progress=False)

    results = process_invoices(
        input_dir=invoices_dir,
        output_file=output,
        workers=1,
        mode="sequential",
        show_progress=False,
    )

    assert len(results) == 3
    assert output.exists()


def test_write_excel_empty(tmp_path: Path) -> None:
    path = write_excel([], tmp_path / "empty.xlsx")
    assert path.exists()
