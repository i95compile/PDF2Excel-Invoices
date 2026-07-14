"""Tests for processor helpers and models."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.processor.config import resolve_worker_count
from src.processor.models import InvoiceData, LineItem
from src.processor.utils import list_pdf_files, parse_money


def test_resolve_worker_count_auto() -> None:
    workers = resolve_worker_count("auto")
    assert workers >= 1


def test_resolve_worker_count_int() -> None:
    assert resolve_worker_count(4) == 4
    assert resolve_worker_count("8") == 8


def test_resolve_worker_count_invalid() -> None:
    with pytest.raises(ValueError):
        resolve_worker_count("many")


def test_parse_money() -> None:
    assert parse_money("$1,234.50") == 1234.50
    assert parse_money("n/a") is None


def test_list_pdf_files(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    (tmp_path / "b.txt").write_text("nope")
    files = list_pdf_files(tmp_path)
    assert [f.name for f in files] == ["a.pdf"]


def test_invoice_data_flattening() -> None:
    invoice = InvoiceData(
        source_file="INV.pdf",
        invoice_number="INV-1",
        from_party="Acme",
        bill_to="Beta",
        subtotal=10.0,
        line_items=[LineItem(description="Widget", quantity=1, unit_price=10, total=10)],
    )
    flat = invoice.to_flat_dict()
    assert flat["from"] == "Acme"
    assert flat["line_item_count"] == 1
    rows = invoice.line_items_as_rows()
    assert rows[0]["description"] == "Widget"
