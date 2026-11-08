from datetime import datetime
from decimal import Decimal

from invoice import Invoice, LineItem, render_text, total, vat_amount, vat_breakdown


def make(items, **kwargs):
    return Invoice(number="H-5", customer="Acme GmbH", items=items, issued_at=datetime(2026, 1, 1), **kwargs)


def mixed(**kwargs):
    return make(
        [
            LineItem("Licence", 2, Decimal("100.00")),
            LineItem("Book", 1, Decimal("50.00"), vat_rate=Decimal("7")),
        ],
        **kwargs,
    )


def test_line_item_rate_defaults_to_none():
    assert LineItem("X", 1, Decimal("1")).vat_rate is None


def test_breakdown_two_rates():
    inv = mixed()
    breakdown = vat_breakdown(inv)
    assert list(breakdown) == [Decimal("19"), Decimal("7")]
    assert breakdown[Decimal("19")] == (Decimal("200.00"), Decimal("38.00"))
    assert breakdown[Decimal("7")] == (Decimal("50.00"), Decimal("3.50"))
    assert vat_amount(inv) == Decimal("41.50")
    assert total(inv) == Decimal("291.50")


def test_breakdown_with_discount():
    inv = mixed(discount_pct=Decimal("10"))
    breakdown = vat_breakdown(inv)
    assert breakdown[Decimal("19")] == (Decimal("180.00"), Decimal("34.20"))
    assert breakdown[Decimal("7")] == (Decimal("45.00"), Decimal("3.15"))
    assert vat_amount(inv) == Decimal("37.35")
    assert total(inv) == Decimal("262.35")


def test_single_rate_unchanged():
    inv = make([LineItem("Day rate", 2, Decimal("950.00")), LineItem("Travel", 1, Decimal("120.40"))])
    assert vat_breakdown(inv) == {Decimal("19"): (Decimal("2020.40"), Decimal("383.88"))}
    assert total(inv) == Decimal("2404.28")


def test_render_shows_each_rate():
    text = render_text(mixed())
    assert "VAT 19%" in text and "VAT 7%" in text
    assert text.index("VAT 19%") < text.index("VAT 7%")
