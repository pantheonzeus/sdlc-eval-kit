from datetime import datetime
from decimal import Decimal

from invoice import Invoice, LineItem, discount_amount, line_net, round_money, total, vat_amount


def make(items, **kwargs):
    return Invoice(number="H-4", customer="Acme GmbH", items=items, issued_at=datetime(2026, 1, 1), **kwargs)


def test_line_rounds_half_up():
    assert line_net(LineItem("Screw", 3, Decimal("0.835"))) == Decimal("2.51")


def test_round_money_half_up_both_signs():
    assert round_money(Decimal("2.345")) == Decimal("2.35")
    assert round_money(Decimal("2.325")) == Decimal("2.33")
    assert round_money(Decimal("-2.345")) == Decimal("-2.35")


def test_discount_rounds_half_up():
    inv = make([LineItem("Item", 1, Decimal("10.05"))], discount_pct=Decimal("10"))
    assert discount_amount(inv) == Decimal("1.01")


def test_vat_rounds_half_up():
    inv = make([LineItem("Book", 1, Decimal("1.50"))], vat_rate=Decimal("7"))
    assert vat_amount(inv) == Decimal("0.11")
    assert total(inv) == Decimal("1.61")
