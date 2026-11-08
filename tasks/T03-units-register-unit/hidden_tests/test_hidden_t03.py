import pytest
from units import UnitError, convert, dimension, known_units, register_unit


def test_register_temperature_unit():
    register_unit("R", "temperature", lambda r: r * 5 / 9, lambda k: k * 9 / 5, aliases=("rankine",))
    assert dimension("R") == "temperature"
    assert convert(491.67, "rankine", "C") == pytest.approx(0, abs=1e-9)
    assert convert(0, "C", "R") == pytest.approx(491.67)


def test_register_linear_unit():
    register_unit("nmi", "length", lambda v: v * 1852, lambda m: m / 1852)
    assert convert(1, "nmi", "km") == pytest.approx(1.852)
    assert "nmi" in known_units()


def test_register_new_dimension():
    register_unit("s", "time", lambda v: v, lambda v: v)
    register_unit("h", "time", lambda v: v * 3600, lambda v: v / 3600, aliases=("hour", "hours"))
    assert convert(2, "hours", "s") == pytest.approx(7200)
    with pytest.raises(UnitError):
        convert(1, "h", "m")


def test_duplicates_rejected():
    with pytest.raises(UnitError):
        register_unit("km", "length", lambda v: v, lambda v: v)
    with pytest.raises(UnitError):
        register_unit("xc", "temperature", lambda v: v, lambda v: v, aliases=("celsius",))


def test_existing_behaviour_kept():
    assert convert(100, "C", "F") == pytest.approx(212)
    assert convert(1, "mi", "km") == pytest.approx(1.609344)
