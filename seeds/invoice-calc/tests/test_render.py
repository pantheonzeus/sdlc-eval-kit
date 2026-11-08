from datetime import datetime
from decimal import Decimal

from invoice import Invoice, LineItem, render_text


def test_render_text():
    inv = Invoice(
        number="2026-007",
        customer="Acme GmbH",
        items=[LineItem("Consulting day", 2, Decimal("950.00"))],
        discount_pct=Decimal("5"),
        issued_at=datetime(2026, 3, 2, 10, 30),
    )
    text = render_text(inv)
    assert text.startswith("INVOICE 2026-007\n")
    assert "Issued: 2026-03-02   Due: 2026-04-01" in text
    assert "Discount 5%" in text
    assert text.rstrip().endswith("€2,147.95")
    assert all(len(line) <= 60 for line in text.splitlines())
