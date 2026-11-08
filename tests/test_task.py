import shutil

import pytest

from sdlc_eval_kit.task import ARCHETYPES, TaskError, load_task, load_tasks


def test_shipped_tasks_load(root):
    tasks = load_tasks(root / "tasks", root / "seeds")
    assert len(tasks) == 10
    assert {t.archetype for t in tasks} == set(ARCHETYPES)
    assert len({t.id for t in tasks}) == 10


@pytest.fixture
def task_copy(root, tmp_path):
    dest = tmp_path / "T02-units-fahrenheit-kelvin"
    shutil.copytree(root / "tasks" / dest.name, dest)
    return dest


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("archetype: bug", "archetype: chore", "archetype"),
        ("evaluation: verifiable", "evaluation: vibes", "evaluation"),
        ("seed: units-converter", "seed: nowhere", "seed"),
        ("id: T02-units-fahrenheit-kelvin", "id: T99", "directory name"),
        ("archetype: bug", "archetype: bug\nowner: me", "unknown keys"),
    ],
)
def test_invalid_task_yaml(root, task_copy, old, new, message):
    path = task_copy / "task.yaml"
    path.write_text(path.read_text().replace(old, new))
    with pytest.raises(TaskError, match=message):
        load_task(task_copy, root / "seeds")


def test_task_needs_hidden_tests_and_reference(root, task_copy):
    shutil.rmtree(task_copy / "reference")
    with pytest.raises(TaskError, match="reference"):
        load_task(task_copy, root / "seeds")
    shutil.rmtree(task_copy / "hidden_tests")
    with pytest.raises(TaskError, match="hidden_tests"):
        load_task(task_copy, root / "seeds")
