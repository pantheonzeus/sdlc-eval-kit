import pytest
from units import Quantity, UnitError, canonical, convert, convert_string, dimension, known_units, parse_quantity


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (1, "m3", "l", 1000),
        (250, "ml", "l", 0.25),
        (1, "l", "cl", 100),
        (1, "gal", "l", 3.785411784),
        (2, "gal", "ml", 7570.823568),
    ],
)
def test_volume_conversions(value, src, dst, expected):
    assert convert(value, src, dst) == pytest.approx(expected)


def test_volume_dimension_and_aliases():
    assert dimension("l") == "volume"
    assert dimension("m3") == "volume"
    assert canonical("Litres") == "l"
    assert canonical("milliliter") == "ml"
    assert canonical("gallons") == "gal"


def test_volume_is_its_own_dimension():
    with pytest.raises(UnitError):
        convert(1, "l", "kg")


def test_volume_listed_and_parsed():
    assert {"l", "ml", "cl", "m3", "gal"} <= set(known_units())
    assert parse_quantity("2.5 liters") == Quantity(2.5, "l")
    assert convert_string("1 gal to ml") == pytest.approx(3785.411784)
