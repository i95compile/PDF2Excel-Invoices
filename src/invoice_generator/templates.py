"""
PDF invoice layout templates using ReportLab.

Keeps rendering concerns separate from data generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "InvoiceTitle",
            parent=base["Heading1"],
            fontSize=22,
            textColor=colors.HexColor("#1a365d"),
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "SectionHeader",
            parent=base["Heading2"],
            fontSize=11,
            textColor=colors.HexColor("#2c5282"),
            spaceBefore=12,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "BodyTextCustom",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
        ),
        "meta": ParagraphStyle(
            "MetaText",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2d3748"),
        ),
    }


def render_invoice_pdf(path: Path, invoice: dict[str, Any]) -> None:
    """
    Render a single invoice dictionary to a PDF file.

    Expected ``invoice`` keys:
        invoice_number, date, from, bill_to, line_items, subtotal
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story: list[Any] = []
    story.append(Paragraph("INVOICE", styles["title"]))
    story.append(
        Paragraph(
            f"<b>Invoice #:</b> {invoice['invoice_number']}<br/>"
            f"<b>Date:</b> {invoice['date']}",
            styles["meta"],
        )
    )
    story.append(Spacer(1, 0.25 * inch))

    # Sequential party blocks keep PDF text extraction unambiguous
    # (side-by-side tables often merge columns when read as plain text).
    from_party = invoice["from"]
    bill_to = invoice["bill_to"]

    story.append(Paragraph("From", styles["section"]))
    story.append(
        Paragraph(
            f"{from_party['name']}<br/>"
            f"{from_party['address']}<br/>"
            f"{from_party['city_line']}<br/>"
            f"{from_party['email']}<br/>"
            f"{from_party['phone']}",
            styles["body"],
        )
    )
    story.append(Paragraph("Bill To", styles["section"]))
    story.append(
        Paragraph(
            f"{bill_to['name']}<br/>"
            f"{bill_to['address']}<br/>"
            f"{bill_to['city_line']}<br/>"
            f"{bill_to['email']}<br/>"
            f"{bill_to['phone']}",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Line Items", styles["section"]))

    table_data: list[list[Any]] = [
        ["Description", "Qty", "Unit Price", "Total"],
    ]
    for item in invoice["line_items"]:
        table_data.append(
            [
                item["description"],
                str(item["quantity"]),
                f"${item['unit_price']:,.2f}",
                f"${item['total']:,.2f}",
            ]
        )

    table_data.append(["", "", "Subtotal", f"${invoice['subtotal']:,.2f}"])

    items_table = Table(
        table_data,
        colWidths=[3.6 * inch, 0.7 * inch, 1.2 * inch, 1.2 * inch],
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -2), 0.4, colors.HexColor("#cbd5e0")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#edf2f7")),
                ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.4 * inch))
    story.append(
        Paragraph(
            "Thank you for your business. Payment is due within 30 days.",
            styles["body"],
        )
    )

    doc.build(story)
