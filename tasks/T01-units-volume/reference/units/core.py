"""Unit tables and conversion."""


class UnitError(ValueError):
    """Raised for an unknown unit or a conversion across dimensions."""


# Linear units: the factor that converts one unit into the dimension's base unit.
_LINEAR = {
    "length": {
        "m": 1.0,
        "km": 1000.0,
        "cm": 0.01,
        "mm": 0.001,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.344,
    },
    "mass": {
        "kg": 1.0,
        "g": 0.001,
        "mg": 0.000001,
        "t": 1000.0,
        "lb": 0.45359237,
        "oz": 0.028349523125,
    },
    "volume": {
        "l": 1.0,
        "ml": 0.001,
        "cl": 0.01,
        "m3": 1000.0,
        "gal": 3.785411784,
    },
}

_TEMPERATURE = ("C", "F", "K")

_ALIASES = {
    "meter": "m",
    "meters": "m",
    "metre": "m",
    "metres": "m",
    "kilometer": "km",
    "kilometers": "km",
    "kilometre": "km",
    "kilometres": "km",
    "centimeter": "cm",
    "millimeter": "mm",
    "inch": "in",
    "inches": "in",
    "foot": "ft",
    "feet": "ft",
    "yard": "yd",
    "yards": "yd",
    "mile": "mi",
    "miles": "mi",
    "kilogram": "kg",
    "kilograms": "kg",
    "gram": "g",
    "grams": "g",
    "milligram": "mg",
    "tonne": "t",
    "tonnes": "t",
    "pound": "lb",
    "pounds": "lb",
    "lbs": "lb",
    "ounce": "oz",
    "ounces": "oz",
    "litre": "l",
    "litres": "l",
    "liter": "l",
    "liters": "l",
    "millilitre": "ml",
    "milliliter": "ml",
    "gallon": "gal",
    "gallons": "gal",
    "celsius": "C",
    "°c": "C",
    "fahrenheit": "F",
    "°f": "F",
    "kelvin": "K",
}


def known_units() -> list[str]:
    """Return every canonical unit symbol, sorted."""
    symbols = [unit for table in _LINEAR.values() for unit in table]
    return sorted([*symbols, *_TEMPERATURE])


def canonical(unit: str) -> str:
    """Return the canonical symbol for a unit name or alias."""
    name = unit.strip()
    if name in _TEMPERATURE:
        return name
    lowered = name.lower()
    if lowered in _ALIASES:
        return _ALIASES[lowered]
    if lowered.upper() in _TEMPERATURE and len(lowered) == 1:
        return lowered.upper()
    for table in _LINEAR.values():
        if lowered in table:
            return lowered
    raise UnitError(f"unknown unit: {unit!r}")


def dimension(unit: str) -> str:
    """Return the dimension ('length', 'mass', 'temperature') of a unit."""
    symbol = canonical(unit)
    if symbol in _TEMPERATURE:
        return "temperature"
    for name, table in _LINEAR.items():
        if symbol in table:
            return name
    raise UnitError(f"unknown unit: {unit!r}")


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value from one unit to another of the same dimension."""
    src, dst = canonical(from_unit), canonical(to_unit)
    dim = dimension(src)
    if dimension(dst) != dim:
        raise UnitError(f"cannot convert {dim} ({src}) to {dimension(dst)} ({dst})")
    if dim == "temperature":
        return _convert_temperature(value, src, dst)
    table = _LINEAR[dim]
    return value * table[src] / table[dst]


def _convert_temperature(value: float, src: str, dst: str) -> float:
    if src == dst:
        return value
    if src == "C" and dst == "F":
        return value * 9 / 5 + 32
    if src == "F" and dst == "C":
        return (value - 32) * 5 / 9
    if src == "C" and dst == "K":
        return value + 273.15
    if src == "K" and dst == "C":
        return value - 273.15
    if src == "F" and dst == "K":
        return (value - 32) * 5 / 9 - 273.15
    if src == "K" and dst == "F":
        return (value - 273.15) * 9 / 5 + 32
    raise UnitError(f"no temperature conversion from {src} to {dst}")
