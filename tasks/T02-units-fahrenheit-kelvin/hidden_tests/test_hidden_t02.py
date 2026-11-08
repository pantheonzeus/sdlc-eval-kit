import pytest
from units import convert, convert_string


@pytest.mark.parametrize(
    ("value", "expected"),
    [(32, 273.15), (212, 373.15), (-459.67, 0.0), (98.6, 310.15)],
)
def test_fahrenheit_to_kelvin(value, expected):
    assert convert(value, "F", "K") == pytest.approx(expected)


def test_round_trip_through_fahrenheit():
    for kelvin in (0.0, 255.0, 300.0):
        assert convert(convert(kelvin, "K", "F"), "F", "K") == pytest.approx(kelvin, abs=1e-9)


def test_string_form():
    assert convert_string("32 fahrenheit to kelvin") == pytest.approx(273.15)
