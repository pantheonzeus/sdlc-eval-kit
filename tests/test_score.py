import pytest

from sdlc_eval_kit.score import materialize, score
from sdlc_eval_kit.task import load_tasks


@pytest.fixture
def task(root):
    return next(t for t in load_tasks(root / "tasks", root / "seeds") if t.id == "T02-units-fahrenheit-kelvin")


def test_seed_fails_reference_passes(root, task, tmp_path):
    base = score(task, materialize(task, root / "seeds", tmp_path / "base", False), root / "seeds")
    ref = score(task, materialize(task, root / "seeds", tmp_path / "ref", True), root / "seeds")
    assert (base.visible_passed, base.hidden_passed, base.passed) == (True, False, False)
    assert (ref.passed, ref.touched_tests) == (True, False)


def test_editing_visible_tests_is_detected_and_useless(root, task, tmp_path):
    ws = materialize(task, root / "seeds", tmp_path / "ws", False)
    core = ws / "units" / "core.py"
    core.write_text(core.read_text().replace("return value * 9 / 5 + 32", "return value"))
    (ws / "tests" / "test_core.py").write_text("def test_nothing():\n    assert True\n")
    result = score(task, ws, root / "seeds")
    assert result.touched_tests
    assert not result.visible_passed
    assert not result.passed


def test_deleted_tests_count_as_touched(root, task, tmp_path):
    ws = materialize(task, root / "seeds", tmp_path / "ws", True)
    for path in (ws / "tests").iterdir():
        if path.is_file():
            path.unlink()
    result = score(task, ws, root / "seeds")
    assert result.touched_tests
    assert result.passed


def test_hidden_tests_planted_by_agent_are_replaced(root, task, tmp_path):
    ws = materialize(task, root / "seeds", tmp_path / "ws", False)
    (ws / "tests" / "hidden").mkdir()
    (ws / "tests" / "hidden" / "test_hidden_t02.py").write_text("def test_ok():\n    assert True\n")
    result = score(task, ws, root / "seeds")
    assert result.touched_tests
    assert not result.hidden_passed
