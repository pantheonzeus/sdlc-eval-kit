"""Score a workspace against a task's hidden tests.

The agent's copy of the visible tests is discarded and the seed's pristine tests are
restored, so editing tests can never turn a run green. Hidden tests are added only
here, after the agent has finished.
"""

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from filecmp import dircmp
from pathlib import Path

from sdlc_eval_kit.task import Task

IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc")
TIMEOUT_S = 300


@dataclass(frozen=True)
class Score:
    passed: bool
    visible_passed: bool
    hidden_passed: bool
    touched_tests: bool


def score(task: Task, workspace: Path, seeds_dir: Path) -> Score:
    """Run the seed's visible tests and the task's hidden tests on a copy of workspace."""
    seed_tests = seeds_dir / task.seed / "tests"
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "ws"
        shutil.copytree(workspace, ws, ignore=IGNORE)
        touched = _differs(seed_tests, ws / "tests")
        shutil.rmtree(ws / "tests", ignore_errors=True)
        shutil.copytree(seed_tests, ws / "tests", ignore=IGNORE)
        visible = _pytest(ws, "tests")
        shutil.copytree(task.hidden_tests, ws / "tests" / "hidden", ignore=IGNORE)
        hidden = _pytest(ws, "tests/hidden")
    return Score(visible and hidden, visible, hidden, touched)


def materialize(task: Task, seeds_dir: Path, dest: Path, with_reference: bool) -> Path:
    """Copy the seed to dest, optionally overlaying the reference solution."""
    shutil.copytree(seeds_dir / task.seed, dest, ignore=IGNORE)
    if with_reference:
        shutil.copytree(task.reference, dest, dirs_exist_ok=True, ignore=IGNORE)
    return dest


def _pytest(root: Path, target: str) -> bool:
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target]
    try:
        result = subprocess.run(cmd, cwd=root, capture_output=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0


def _differs(expected: Path, actual: Path) -> bool:
    if not actual.is_dir():
        return True
    cmp = dircmp(expected, actual, ignore=[".git", "__pycache__", ".pytest_cache"])
    return _tree_differs(cmp)


def _tree_differs(cmp: dircmp) -> bool:
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    return any(_tree_differs(sub) for sub in cmp.subdirs.values())
