"""Tests for invoice generator."""

from __future__ import annotations

from pathlib import Path

from src.invoice_generator import generate_invoices
from src.invoice_generator.utils import compute_subtotal, random_line_items


def test_random_line_items_have_totals() -> None:
    items = random_line_items(min_items=2, max_items=3)
    assert 2 <= len(items) <= 3
    assert compute_subtotal(items) == round(sum(i["total"] for i in items), 2)


def test_generate_invoices_creates_pdfs(tmp_path: Path) -> None:
    paths = generate_invoices(tmp_path, count=2, show_progress=False)
    assert len(paths) == 2
    assert all(p.exists() and p.suffix == ".pdf" for p in paths)
