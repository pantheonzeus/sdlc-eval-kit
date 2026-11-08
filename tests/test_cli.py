import shutil

from sdlc_eval_kit.cli import main


def test_check_tasks_on_shipped_tasks(root, capsys):
    assert main(["--root", str(root), "check-tasks"]) == 0
    assert "10/10 tasks sound" in capsys.readouterr().out


def test_check_tasks_catches_unsound_task(root, tmp_path, capsys):
    shutil.copytree(root / "seeds", tmp_path / "seeds")
    shutil.copytree(root / "tasks" / "T02-units-fahrenheit-kelvin", tmp_path / "tasks" / "T02-units-fahrenheit-kelvin")
    hidden = tmp_path / "tasks" / "T02-units-fahrenheit-kelvin" / "hidden_tests" / "test_hidden_t02.py"
    hidden.write_text("def test_trivial():\n    assert True\n")
    assert main(["--root", str(tmp_path), "check-tasks"]) == 1
    assert "hidden tests already pass on the seed" in capsys.readouterr().out


def test_validate_reports_bad_task(root, tmp_path, capsys):
    shutil.copytree(root / "seeds", tmp_path / "seeds")
    (tmp_path / "tasks" / "T00-empty").mkdir(parents=True)
    assert main(["--root", str(tmp_path), "validate"]) == 2
    assert "missing task.yaml" in capsys.readouterr().err


def test_results_without_runs(root, tmp_path, capsys):
    shutil.copytree(root / "seeds", tmp_path / "seeds")
    shutil.copytree(root / "tasks", tmp_path / "tasks")
    assert main(["--root", str(tmp_path), "results"]) == 0
    assert "No runs yet." in (tmp_path / "RESULTS.md").read_text()
