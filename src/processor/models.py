"""
Domain models for InvoiceFlow processor.

These dataclasses are the stable contract between extractors, workers,
and exporters. Future OCR/AI backends should map into these types.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class LineItem:
    """A single invoice line item."""

    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InvoiceData:
    """
    Structured representation of one invoice PDF.

    Fields intentionally mirror common invoice layouts and the generator output.
    """

    source_file: str
    invoice_number: Optional[str] = None
    date: Optional[str] = None
    bill_to: Optional[str] = None
    from_party: Optional[str] = None  # "from" is a reserved keyword
    subtotal: Optional[float] = None
    line_items: list[LineItem] = field(default_factory=list)
    # Extensibility hooks for future AI/OCR backends
    extraction_method: str = "text"  # text | ocr | ai
    confidence: Optional[float] = None
    raw_text: Optional[str] = None
    errors: list[str] = field(default_factory=list)

    def to_flat_dict(self) -> dict[str, Any]:
        """Flatten header fields for a summary DataFrame / Excel sheet."""
        return {
            "source_file": self.source_file,
            "invoice_number": self.invoice_number,
            "date": self.date,
            "bill_to": self.bill_to,
            "from": self.from_party,
            "subtotal": self.subtotal,
            "line_item_count": len(self.line_items),
            "extraction_method": self.extraction_method,
            "confidence": self.confidence,
            "errors": "; ".join(self.errors) if self.errors else None,
        }

    def line_items_as_rows(self) -> list[dict[str, Any]]:
        """Expand line items with invoice identity for a detail sheet."""
        rows: list[dict[str, Any]] = []
        for item in self.line_items:
            rows.append(
                {
                    "invoice_number": self.invoice_number,
                    "source_file": self.source_file,
                    **item.to_dict(),
                }
            )
        return rows
