from datetime import datetime
from decimal import Decimal

import pytest
from invoice import Invoice, LineItem, discount_amount, line_net, subtotal, total, vat_amount


def make(items, **kwargs):
    kwargs.setdefault("issued_at", datetime(2026, 1, 15, 9, 0))
    return Invoice(number="T-1", customer="Acme GmbH", items=items, **kwargs)


def test_line_net():
    assert line_net(LineItem("Widget", 3, Decimal("19.99"))) == Decimal("59.97")


def test_totals_without_discount():
    inv = make([LineItem("Day rate", 2, Decimal("950.00")), LineItem("Travel", 1, Decimal("120.40"))])
    assert subtotal(inv) == Decimal("2020.40")
    assert discount_amount(inv) == Decimal("0.00")
    assert vat_amount(inv) == Decimal("383.88")
    assert total(inv) == Decimal("2404.28")


def test_totals_with_discount():
    inv = make([LineItem("Licence", 4, Decimal("250.00"))], discount_pct=Decimal("10"))
    assert subtotal(inv) == Decimal("1000.00")
    assert discount_amount(inv) == Decimal("100.00")
    assert vat_amount(inv) == Decimal("171.00")
    assert total(inv) == Decimal("1071.00")


def test_custom_vat_rate():
    inv = make([LineItem("Book", 1, Decimal("20.00"))], vat_rate=Decimal("7"))
    assert total(inv) == Decimal("21.40")


def test_validation():
    with pytest.raises(ValueError):
        make([])
    with pytest.raises(ValueError):
        LineItem("Nothing", 0, Decimal("1"))
    with pytest.raises(ValueError):
        make([LineItem("X", 1, Decimal("1"))], discount_pct=Decimal("120"))


def test_due_date():
    inv = make([LineItem("X", 1, Decimal("1"))], payment_terms_days=14)
    assert inv.due_date.isoformat() == "2026-01-29"
