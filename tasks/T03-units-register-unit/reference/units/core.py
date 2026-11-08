"""Unit registry and conversion. Every unit converts to and from its dimension's base unit."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass


class UnitError(ValueError):
    """Raised for an unknown unit or a conversion across dimensions."""


@dataclass(frozen=True)
class _Unit:
    dimension: str
    to_base: Callable[[float], float]
    from_base: Callable[[float], float]


_UNITS: dict[str, _Unit] = {}
_ALIASES: dict[str, str] = {}


def register_unit(
    symbol: str,
    dimension: str,
    to_base: Callable[[float], float],
    from_base: Callable[[float], float],
    aliases: Iterable[str] = (),
) -> None:
    """Add a unit; raise UnitError if the symbol or an alias is already taken."""
    aliases = [alias.lower() for alias in aliases]
    for name in (symbol, *aliases):
        if name in _UNITS or name.lower() in _ALIASES:
            raise UnitError(f"unit name already registered: {name!r}")
    _UNITS[symbol] = _Unit(dimension, to_base, from_base)
    for alias in aliases:
        _ALIASES[alias] = symbol


def _linear(symbol: str, dimension: str, factor: float, aliases: Iterable[str] = ()) -> None:
    register_unit(symbol, dimension, lambda v: v * factor, lambda v: v / factor, aliases)


_linear("m", "length", 1.0, ("meter", "meters", "metre", "metres"))
_linear("km", "length", 1000.0, ("kilometer", "kilometers", "kilometre", "kilometres"))
_linear("cm", "length", 0.01, ("centimeter",))
_linear("mm", "length", 0.001, ("millimeter",))
_linear("in", "length", 0.0254, ("inch", "inches"))
_linear("ft", "length", 0.3048, ("foot", "feet"))
_linear("yd", "length", 0.9144, ("yard", "yards"))
_linear("mi", "length", 1609.344, ("mile", "miles"))
_linear("kg", "mass", 1.0, ("kilogram", "kilograms"))
_linear("g", "mass", 0.001, ("gram", "grams"))
_linear("mg", "mass", 0.000001, ("milligram",))
_linear("t", "mass", 1000.0, ("tonne", "tonnes"))
_linear("lb", "mass", 0.45359237, ("pound", "pounds", "lbs"))
_linear("oz", "mass", 0.028349523125, ("ounce", "ounces"))
register_unit("K", "temperature", lambda v: v, lambda v: v, ("kelvin",))
register_unit("C", "temperature", lambda c: c + 273.15, lambda k: k - 273.15, ("celsius", "°c"))
register_unit(
    "F",
    "temperature",
    lambda f: (f - 32) * 5 / 9 + 273.15,
    lambda k: (k - 273.15) * 9 / 5 + 32,
    ("fahrenheit", "°f"),
)


def known_units() -> list[str]:
    """Return every canonical unit symbol, sorted."""
    return sorted(_UNITS)


def canonical(unit: str) -> str:
    """Return the canonical symbol for a unit name or alias."""
    name = unit.strip()
    if name in _UNITS:
        return name
    lowered = name.lower()
    if lowered in _ALIASES:
        return _ALIASES[lowered]
    if lowered in _UNITS:
        return lowered
    if len(name) == 1 and name.upper() in _UNITS:
        return name.upper()
    raise UnitError(f"unknown unit: {unit!r}")


def dimension(unit: str) -> str:
    """Return the dimension (e.g. 'length', 'mass', 'temperature') of a unit."""
    return _UNITS[canonical(unit)].dimension


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value from one unit to another of the same dimension."""
    src, dst = _UNITS[canonical(from_unit)], _UNITS[canonical(to_unit)]
    if src.dimension != dst.dimension:
        raise UnitError(f"cannot convert {src.dimension} ({from_unit}) to {dst.dimension} ({to_unit})")
    if src is dst:
        return value
    return dst.from_base(src.to_base(value))
