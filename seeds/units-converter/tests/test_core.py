import pytest
from units import UnitError, canonical, convert, dimension, known_units


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (5, "km", "m", 5000),
        (1, "mi", "km", 1.609344),
        (12, "in", "ft", 1),
        (250, "g", "kg", 0.25),
        (1, "lb", "oz", 16),
        (2, "t", "kg", 2000),
    ],
)
def test_linear_conversions(value, src, dst, expected):
    assert convert(value, src, dst) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (100, "C", "F", 212),
        (212, "F", "C", 100),
        (0, "C", "K", 273.15),
        (0, "K", "C", -273.15),
        (0, "K", "F", -459.67),
        (20, "C", "C", 20),
    ],
)
def test_temperature_conversions(value, src, dst, expected):
    assert convert(value, src, dst) == pytest.approx(expected)


def test_aliases_resolve():
    assert canonical("Kilometres") == "km"
    assert canonical("celsius") == "C"
    assert canonical("c") == "C"
    assert canonical("lbs") == "lb"


def test_dimension():
    assert dimension("ft") == "length"
    assert dimension("oz") == "mass"
    assert dimension("K") == "temperature"


def test_cross_dimension_rejected():
    with pytest.raises(UnitError):
        convert(1, "kg", "m")


def test_unknown_unit_rejected():
    with pytest.raises(UnitError):
        convert(1, "parsec", "m")


def test_known_units_sorted_and_complete():
    units = known_units()
    assert units == sorted(units)
    assert {"m", "kg", "C", "F", "K"} <= set(units)
