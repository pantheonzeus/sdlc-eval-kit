import csv
import json

import pytest

from sdlc_eval_kit.results import export_errors, load_labels, load_trials, render_results


def trial(task, model, n, passed, **extra):
    record = {
        "run_id": "r1",
        "task_id": task,
        "archetype": "bug" if task == "T1" else "feature",
        "model": model,
        "model_version": "2026-11-01",
        "trial": n,
        "date": "2026-11-08",
        "passed": passed,
        "visible_passed": True,
        "hidden_passed": passed,
        "touched_tests": False,
        "exit_status": "submitted",
        "cost_eur": 0.10,
        "tool_calls": 10,
        "wall_s": 60,
    }
    record.update(extra)
    return record


@pytest.fixture
def runs(tmp_path):
    trials = [
        trial("T1", "api", 1, True),
        trial("T1", "api", 2, True),
        trial("T1", "api", 3, True),
        trial("T2", "api", 1, True),
        trial("T2", "api", 2, False, touched_tests=True),
        trial("T2", "api", 3, False, exit_status="step_cap"),
        trial("T1", "local", 1, False, cost_eur=0.0),
        trial("T1", "local", 2, False, cost_eur=0.0),
        trial("T1", "local", 3, False, cost_eur=0.0),
        trial("T2", "local", 1, False, cost_eur=0.0),
        trial("T2", "local", 2, False, cost_eur=0.0),
        trial("T2", "local", 3, False, cost_eur=0.0),
    ]
    run_dir = tmp_path / "runs" / "r1"
    run_dir.mkdir(parents=True)
    (run_dir / "trials.jsonl").write_text("\n".join(json.dumps(t) for t in reversed(trials)) + "\n")
    return tmp_path / "runs"


def test_render_is_deterministic_and_correct(runs, tmp_path):
    trials = load_trials(runs)
    text = render_results(trials, {})
    assert text == render_results(load_trials(runs), {})
    api_row = next(line for line in text.splitlines() if line.startswith("| api |"))
    assert "| 2 | 6 | 66.7%" in api_row
    assert "pass^3 50.0%" in api_row
    assert "| 0.15 | 0.60 |" in api_row  # €0.60 total over 4 successes
    local_row = next(line for line in text.splitlines() if line.startswith("| local |"))
    assert "0.0%" in local_row and "| — |" in local_row
    assert "8 failed trials, 8 unlabelled." in text


def test_export_keeps_labels_and_hints(runs, tmp_path):
    csv_path = tmp_path / "results" / "error_analysis.csv"
    trials = load_trials(runs)
    assert export_errors(trials, csv_path) == 8
    rows = list(csv.DictReader(csv_path.open()))
    hints = {(r["model"], r["task_id"], r["trial"]): r["auto_hint"] for r in rows}
    assert hints[("api", "T2", "2")] == "edited_or_gamed_tests"
    assert hints[("api", "T2", "3")] == "step_cap"

    rows[0]["label"], rows[0]["note"] = "misread_brief", "solved F to C instead"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    assert export_errors(trials, csv_path) == 7
    labels = load_labels(csv_path)
    assert list(labels.values()).count("misread_brief") == 1
    assert "| misread_brief | 1 | 12.5% |" in render_results(trials, labels)


def test_unknown_label_rejected(runs, tmp_path):
    csv_path = tmp_path / "error_analysis.csv"
    export_errors(load_trials(runs), csv_path)
    rows = list(csv.DictReader(csv_path.open()))
    rows[0]["label"] = "made_up_label"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="unknown label"):
        load_labels(csv_path)


def test_missing_field_rejected(tmp_path):
    run_dir = tmp_path / "runs" / "r1"
    run_dir.mkdir(parents=True)
    (run_dir / "trials.jsonl").write_text(json.dumps({"run_id": "r1"}) + "\n")
    with pytest.raises(ValueError, match="missing"):
        load_trials(tmp_path / "runs")


def test_no_runs():
    assert "No runs yet." in render_results([], {})
