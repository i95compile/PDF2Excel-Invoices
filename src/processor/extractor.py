"""
Field extraction strategies.

``BaseExtractor`` is the extension point for text, OCR, and AI backends.
``TextExtractor`` implements rule-based parsing suited to InvoiceFlow's
generated layout; swap or compose extractors without touching workers.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from src.processor.models import InvoiceData, LineItem
from src.processor.parser import ParsedPdf, PdfParser
from src.processor.utils import first_match, parse_money


class BaseExtractor(ABC):
    """Strategy interface for turning a PDF into ``InvoiceData``."""

    @abstractmethod
    def extract(self, pdf_path: str | Path) -> InvoiceData:
        """Extract structured invoice data from a single PDF."""


class TextExtractor(BaseExtractor):
    """
    Regex / table-based extractor for text PDFs (pdfplumber).

    Tuned for InvoiceFlow generator templates; tolerant of minor variation.
    """

    def __init__(self, parser: PdfParser | None = None) -> None:
        self.parser = parser or PdfParser()

    def extract(self, pdf_path: str | Path) -> InvoiceData:
        path = Path(pdf_path)
        invoice = InvoiceData(
            source_file=path.name,
            extraction_method="text",
        )

        try:
            parsed = self.parser.parse(path)
        except Exception as exc:  # noqa: BLE001 — capture per-file failures
            invoice.errors.append(f"parse_failed: {exc}")
            return invoice

        invoice.raw_text = parsed.text
        self._extract_header_fields(invoice, parsed.text)
        invoice.line_items = self._extract_line_items(parsed)
        if invoice.subtotal is None and invoice.line_items:
            totals = [i.total for i in invoice.line_items if i.total is not None]
            if totals:
                invoice.subtotal = round(sum(totals), 2)

        return invoice

    def _extract_header_fields(self, invoice: InvoiceData, text: str) -> None:
        invoice.invoice_number = first_match(
            r"Invoice\s*#\s*:\s*([A-Z0-9\-]+)", text
        )
        invoice.date = first_match(r"Date\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)

        invoice.from_party = self._extract_party_block(text, "From")
        invoice.bill_to = self._extract_party_block(text, "Bill To")

        subtotal = first_match(r"Subtotal\s+\$?\s*([0-9,]+\.[0-9]{2})", text)
        invoice.subtotal = parse_money(subtotal) if subtotal else None

    def _extract_party_block(self, text: str, label: str) -> str | None:
        """
        Capture the party name under a From / Bill To heading.

        Supports sequential blocks::

            From
            Acme Corp
            ...
            Bill To
            Beta LLC
        """
        pattern = rf"{re.escape(label)}\s*\n([^\n]+)"
        return first_match(pattern, text)

    def _extract_line_items(self, parsed: ParsedPdf) -> list[LineItem]:
        items: list[LineItem] = []

        for table in parsed.tables:
            items.extend(self._line_items_from_table(table))

        if not items and parsed.text:
            items.extend(self._line_items_from_text(parsed.text))

        return items

    def _line_items_from_table(
        self, table: list[list[str | None]]
    ) -> list[LineItem]:
        if not table:
            return []

        items: list[LineItem] = []
        for row in table[1:]:  # skip header
            if not row or not any(row):
                continue
            cells = [(c or "").strip() for c in row]
            # Skip / harvest subtotal footer rows
            joined = " ".join(cells).lower()
            if "subtotal" in joined:
                money = parse_money(" ".join(cells))
                # Subtotal is handled at header level; ignore as line item
                _ = money
                continue
            if len(cells) < 4:
                continue

            description, qty_s, price_s, total_s = cells[0], cells[1], cells[2], cells[3]
            if not description:
                continue

            items.append(
                LineItem(
                    description=description,
                    quantity=parse_money(qty_s),
                    unit_price=parse_money(price_s),
                    total=parse_money(total_s),
                )
            )
        return items

    def _line_items_from_text(self, text: str) -> list[LineItem]:
        """
        Fallback: parse ``Description Qty UnitPrice Total`` style lines.

        TODO: Harden for vendor-specific layouts as real invoices are added.
        """
        items: list[LineItem] = []
        pattern = re.compile(
            r"^(.+?)\s+(\d+)\s+\$?([0-9,]+\.[0-9]{2})\s+\$?([0-9,]+\.[0-9]{2})\s*$",
            re.MULTILINE,
        )
        for match in pattern.finditer(text):
            description = match.group(1).strip()
            if description.lower() in {"description", "subtotal"}:
                continue
            items.append(
                LineItem(
                    description=description,
                    quantity=float(match.group(2)),
                    unit_price=parse_money(match.group(3)),
                    total=parse_money(match.group(4)),
                )
            )
        return items


class OcrExtractor(BaseExtractor):
    """
    Placeholder OCR extractor.

    TODO: Implement using ``PdfParser.parse_ocr`` + same field rules as text,
          or a dedicated OCR confidence pipeline.
    """

    def extract(self, pdf_path: str | Path) -> InvoiceData:
        raise NotImplementedError("OcrExtractor is planned for a future release.")


class AiExtractor(BaseExtractor):
    """
    Placeholder AI / LLM extractor.

    TODO: Call model API, validate JSON against ``InvoiceData``, set
          ``extraction_method='ai'`` and ``confidence``.
    """

    def extract(self, pdf_path: str | Path) -> InvoiceData:
        raise NotImplementedError("AiExtractor is planned for a future release.")


def get_default_extractor() -> BaseExtractor:
    """Factory for the current default extraction strategy."""
    return TextExtractor()
