"""Money helpers: every amount is a Decimal with two places."""

from decimal import Decimal

CENT = Decimal("0.01")


def to_money(value: Decimal | int | str) -> Decimal:
    """Convert an int, str or Decimal to a Decimal amount. Floats are refused.

    >>> to_money("12.30")
    Decimal('12.30')
    >>> to_money(5)
    Decimal('5')
    >>> to_money(0.1)
    Traceback (most recent call last):
        ...
    TypeError: use Decimal or str for money, not float
    """
    if isinstance(value, float):
        raise TypeError("use Decimal or str for money, not float")
    return Decimal(value)


def round_money(amount: Decimal) -> Decimal:
    """Round an amount to the cent.

    >>> round_money(Decimal("10.006"))
    Decimal('10.01')
    """
    return amount.quantize(CENT)


def format_eur(amount: Decimal) -> str:
    """Format an amount as euros with a thousands separator.

    >>> format_eur(Decimal("1234567.8"))
    '€1,234,567.80'
    >>> format_eur(Decimal("-12"))
    '-€12.00'
    """
    rounded = round_money(amount)
    sign = "-" if rounded < 0 else ""
    whole, _, cents = f"{abs(rounded):.2f}".partition(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return f"{sign}€{','.join(groups)}.{cents}"
