from decimal import Decimal

import pytest
from invoice import format_eur, round_money, to_money


def test_to_money_accepts_str_int_decimal():
    assert to_money("12.30") == Decimal("12.30")
    assert to_money(5) == Decimal("5")
    assert to_money(Decimal("1.1")) == Decimal("1.1")


def test_to_money_refuses_float():
    with pytest.raises(TypeError):
        to_money(0.1)


def test_round_money():
    assert round_money(Decimal("10.004")) == Decimal("10.00")
    assert round_money(Decimal("10.006")) == Decimal("10.01")


def test_format_eur():
    assert format_eur(Decimal("1234567.8")) == "€1,234,567.80"
    assert format_eur(Decimal("-12")) == "-€12.00"
    assert format_eur(Decimal("0.5")) == "€0.50"
