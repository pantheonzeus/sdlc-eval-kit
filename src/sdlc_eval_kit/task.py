"""Task definitions: one directory per task with task.yaml, hidden_tests/ and reference/."""

from dataclasses import dataclass
from pathlib import Path

import yaml

ARCHETYPES = ("feature", "bug", "refactor", "upgrade", "docs")
EVALUATIONS = ("verifiable", "judgement")
FIELDS = ("id", "seed", "archetype", "evaluation", "brief")


class TaskError(ValueError):
    """Raised for a task directory that does not match the schema."""


@dataclass(frozen=True)
class Task:
    id: str
    seed: str
    archetype: str
    evaluation: str
    brief: str
    root: Path

    @property
    def hidden_tests(self) -> Path:
        return self.root / "hidden_tests"

    @property
    def reference(self) -> Path:
        return self.root / "reference"


def load_task(task_dir: Path, seeds_dir: Path) -> Task:
    """Load and validate one task directory."""
    path = task_dir / "task.yaml"
    if not path.is_file():
        raise TaskError(f"{task_dir}: missing task.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TaskError(f"{path}: expected a mapping")
    missing = [key for key in FIELDS if not data.get(key)]
    if missing:
        raise TaskError(f"{path}: missing {', '.join(missing)}")
    unknown = sorted(set(data) - set(FIELDS))
    if unknown:
        raise TaskError(f"{path}: unknown keys {', '.join(unknown)}")
    if data["id"] != task_dir.name:
        raise TaskError(f"{path}: id {data['id']!r} must equal the directory name {task_dir.name!r}")
    if data["archetype"] not in ARCHETYPES:
        raise TaskError(f"{path}: archetype must be one of {', '.join(ARCHETYPES)}")
    if data["evaluation"] not in EVALUATIONS:
        raise TaskError(f"{path}: evaluation must be one of {', '.join(EVALUATIONS)}")
    if not (seeds_dir / data["seed"]).is_dir():
        raise TaskError(f"{path}: seed {data['seed']!r} not found in {seeds_dir}")
    task = Task(root=task_dir, **{key: data[key] for key in FIELDS})
    if not any(task.hidden_tests.glob("test_*.py")):
        raise TaskError(f"{task_dir}: hidden_tests/ needs at least one test_*.py")
    if not task.reference.is_dir() or not any(p.is_file() for p in task.reference.rglob("*")):
        raise TaskError(f"{task_dir}: reference/ must hold the changed files of a solution")
    return task


def load_tasks(tasks_dir: Path, seeds_dir: Path) -> list[Task]:
    """Load every task under tasks_dir, sorted by id."""
    return [load_task(d, seeds_dir) for d in sorted(tasks_dir.iterdir()) if d.is_dir()]
