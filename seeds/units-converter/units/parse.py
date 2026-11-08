"""Parse and format quantities written as text, e.g. "5 km" or "5 km to mi"."""

import re
from dataclasses import dataclass

from units.core import UnitError, canonical, convert

_QUANTITY = re.compile(r"^\s*(?P<value>[-+]?\d+(?:\.\d+)?)\s*(?P<unit>[^\s\d][\S]*)\s*$")


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str


def parse_quantity(text: str) -> Quantity:
    """Parse '5 km' into Quantity(5.0, 'km')."""
    match = _QUANTITY.match(text)
    if not match:
        raise UnitError(f"not a quantity: {text!r}")
    return Quantity(float(match["value"]), canonical(match["unit"]))


def convert_string(text: str) -> float:
    """Convert '5 km to m' and return the number."""
    parts = re.split(r"\s+(?:to|in)\s+", text.strip(), maxsplit=1)
    if len(parts) != 2:
        raise UnitError(f"expected '<quantity> to <unit>': {text!r}")
    quantity = parse_quantity(parts[0])
    return convert(quantity.value, quantity.unit, parts[1])


def format_quantity(value: float, unit: str, precision: int = 2) -> str:
    """Format a value with its canonical unit symbol."""
    return f"{value:.{precision}f} {canonical(unit)}"
