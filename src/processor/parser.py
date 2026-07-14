"""
Low-level PDF text / table reading.

``PdfParser`` isolates pdfplumber I/O so extractors stay testable
and alternate backends (OCR images, AI vision) can reuse the same
``InvoiceData`` pipeline without coupling to pdfplumber.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import pdfplumber


@dataclass
class ParsedPdf:
    """Raw artifacts extracted from a PDF before domain parsing."""

    path: Path
    text: str = ""
    tables: list[list[list[Optional[str]]]] = field(default_factory=list)
    page_count: int = 0


class PdfParser:
    """
    Read text and tables from a digital (text-based) PDF.

    TODO: Add ``parse_ocr(path)`` that returns the same ``ParsedPdf`` shape
          after rasterizing pages and running Tesseract / cloud OCR.

    TODO: Add ``parse_via_ai(path)`` for multimodal model extraction that
          still feeds into ``BaseExtractor`` / ``InvoiceData``.
    """

    def parse(self, pdf_path: str | Path) -> ParsedPdf:
        """Open a PDF and collect concatenated text + table grids."""
        path = Path(pdf_path)
        texts: list[str] = []
        tables: list[list[list[Optional[str]]]] = []
        page_count = 0

        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text)
                for table in page.extract_tables() or []:
                    tables.append(table)

        return ParsedPdf(
            path=path,
            text="\n".join(texts),
            tables=tables,
            page_count=page_count,
        )

    # ------------------------------------------------------------------
    # Future extension points
    # ------------------------------------------------------------------

    def parse_ocr(self, pdf_path: str | Path) -> ParsedPdf:
        """
        OCR-backed parse (not implemented yet).

        TODO: Rasterize pages → OCR → populate ``ParsedPdf.text``.
        """
        raise NotImplementedError(
            "OCR parsing is on the roadmap. See README Roadmap section."
        )

    def parse_via_ai(self, pdf_path: str | Path) -> dict[str, Any]:
        """
        AI-backed structured extraction (not implemented yet).

        TODO: Send PDF/page images or text to an LLM and return a dict
              compatible with ``InvoiceData`` field names.
        """
        raise NotImplementedError(
            "AI extraction is on the roadmap. See README Roadmap section."
        )
