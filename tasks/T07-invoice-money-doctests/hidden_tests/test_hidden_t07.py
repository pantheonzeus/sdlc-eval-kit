import doctest

import pytest
from invoice import money


def _examples(name):
    finder = doctest.DocTestFinder()
    tests = [t for t in finder.find(money) if t.name == f"{money.__name__}.{name}"]
    return tests[0] if tests else None


@pytest.mark.parametrize("name", ["to_money", "round_money", "format_eur"])
def test_function_has_examples(name):
    test = _examples(name)
    assert test is not None and len(test.examples) >= 1


def test_float_refusal_documented():
    test = _examples("to_money")
    assert test is not None
    assert any("TypeError" in example.want or "TypeError" in (example.exc_msg or "") for example in test.examples)


def test_doctests_pass():
    result = doctest.testmod(money)
    assert result.attempted >= 3
    assert result.failed == 0
