import pytest
from units import Quantity, UnitError, convert_string, format_quantity, parse_quantity


def test_parse_quantity():
    assert parse_quantity("5 km") == Quantity(5.0, "km")
    assert parse_quantity("  -3.5kg ") == Quantity(-3.5, "kg")
    assert parse_quantity("10 miles") == Quantity(10.0, "mi")


def test_parse_rejects_garbage():
    with pytest.raises(UnitError):
        parse_quantity("five km")


def test_convert_string():
    assert convert_string("5 km to m") == pytest.approx(5000)
    assert convert_string("100 C in F") == pytest.approx(212)


def test_convert_string_needs_target():
    with pytest.raises(UnitError):
        convert_string("5 km")


def test_format_quantity():
    assert format_quantity(3.14159, "metre") == "3.14 m"
    assert format_quantity(2, "kg", precision=0) == "2 kg"
