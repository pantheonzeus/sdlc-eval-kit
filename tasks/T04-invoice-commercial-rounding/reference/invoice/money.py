"""Money helpers: every amount is a Decimal with two places."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def to_money(value: Decimal | int | str) -> Decimal:
    """Convert an int, str or Decimal to a Decimal amount. Floats are refused."""
    if isinstance(value, float):
        raise TypeError("use Decimal or str for money, not float")
    return Decimal(value)


def round_money(amount: Decimal) -> Decimal:
    """Round an amount half-up to the cent (commercial rounding)."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def format_eur(amount: Decimal) -> str:
    """Format an amount as euros with a thousands separator."""
    rounded = round_money(amount)
    sign = "-" if rounded < 0 else ""
    whole, _, cents = f"{abs(rounded):.2f}".partition(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return f"{sign}€{','.join(groups)}.{cents}"
