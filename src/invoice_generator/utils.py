"""Shared helpers for the invoice generator."""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from faker import Faker

fake = Faker()

# Sample catalog for line items
PRODUCT_CATALOG: list[tuple[str, float]] = [
    ("Consulting Services", 150.0),
    ("Software License", 299.0),
    ("Cloud Hosting (monthly)", 89.0),
    ("Hardware Support", 75.0),
    ("Training Workshop", 450.0),
    ("Design Package", 320.0),
    ("API Access Tier", 199.0),
    ("Maintenance Contract", 125.0),
    ("Data Migration", 500.0),
    ("Security Audit", 780.0),
    ("Technical Writing", 95.0),
    ("QA Testing", 110.0),
]


def random_invoice_number(seq: int) -> str:
    """Build a human-readable invoice number."""
    year = date.today().year
    return f"INV-{year}-{seq:06d}"


def random_invoice_date(days_back: int = 365) -> date:
    """Return a random date within the last ``days_back`` days."""
    offset = random.randint(0, days_back)
    return date.today() - timedelta(days=offset)


def random_company() -> dict[str, str]:
    """Generate a fake company / address block."""
    return {
        "name": fake.company(),
        "address": fake.street_address(),
        "city_line": f"{fake.city()}, {fake.state_abbr()} {fake.postcode()}",
        "email": fake.company_email(),
        "phone": fake.phone_number(),
    }


def random_line_items(min_items: int = 1, max_items: int = 6) -> list[dict[str, Any]]:
    """Generate a list of random line items with qty / unit price / total."""
    count = random.randint(min_items, max_items)
    items: list[dict[str, Any]] = []
    for description, base_price in random.sample(
        PRODUCT_CATALOG, k=min(count, len(PRODUCT_CATALOG))
    ):
        quantity = random.randint(1, 8)
        # Slight price jitter for realism
        unit_price = round(base_price * random.uniform(0.85, 1.15), 2)
        total = round(quantity * unit_price, 2)
        items.append(
            {
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total,
            }
        )
    return items


def compute_subtotal(line_items: list[dict[str, Any]]) -> float:
    """Sum line-item totals."""
    return round(sum(item["total"] for item in line_items), 2)
