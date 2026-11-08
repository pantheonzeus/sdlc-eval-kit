from datetime import date

import yaml

from sdlc_eval_kit.runner import AGENT_CONFIG, _done, default_run_id, exit_status, model_label, tree_diff, usage


def test_model_label_and_run_id():
    assert model_label("ollama_chat/qwen3-coder:30b") == "qwen3-coder:30b"
    assert default_run_id("ollama_chat/qwen3-coder:30b", date(2026, 11, 8)) == "20261108-qwen3-coder-30b"


def test_exit_status_maps_to_taxonomy_statuses():
    assert exit_status({"exit_status": "Submitted"}, 7, 50) == "submitted"
    assert exit_status({"exit_status": "LimitsExceeded"}, 50, 50) == "step_cap"
    assert exit_status({"exit_status": "LimitsExceeded"}, 12, 50) == "cost_cap"
    assert exit_status({"exit_status": "RepeatedFormatError"}, 3, 50) == "format_error"
    assert exit_status({"exit_status": "ContextWindowExceededError"}, 9, 50) == "error"


def test_usage_counts_tokens_and_tool_calls():
    messages = [
        {"role": "system", "content": "s"},
        {"role": "assistant", "extra": {"response": {"usage": {"prompt_tokens": 100, "completion_tokens": 20}}}},
        {"role": "tool", "content": "ls"},
        {"role": "tool", "content": "cat"},
        {"role": "user", "extra": {"interrupt_type": "FormatError", "response": None}},
        {"role": "assistant", "extra": {"response": {"usage": {"prompt_tokens": 150, "completion_tokens": 5}}}},
    ]
    assert usage(messages) == {"tokens_in": 250, "tokens_out": 25, "tool_calls": 2}


def test_tree_diff_ignores_git_and_caches(tmp_path):
    before, after = tmp_path / "a", tmp_path / "b"
    for root in (before, after):
        (root / "pkg").mkdir(parents=True)
        (root / "pkg" / "same.py").write_text("x = 1\n")
    (before / "pkg" / "core.py").write_text("def f():\n    return 1\n")
    (after / "pkg" / "core.py").write_text("def f():\n    return 2\n")
    (after / "pkg" / "new.py").write_text("y = 2")
    (after / ".git").mkdir()
    (after / ".git" / "HEAD").write_text("ref")
    (after / "pkg" / "__pycache__").mkdir()
    (after / "pkg" / "__pycache__" / "core.cpython-312.pyc").write_bytes(b"\0")
    diff = tree_diff(before, after)
    assert "--- a/pkg/core.py\n+++ b/pkg/core.py\n" in diff
    assert "-    return 1\n+    return 2\n" in diff
    assert "+++ b/pkg/new.py\n" in diff and diff.endswith("+y = 2\n")
    assert "same.py" not in diff and ".git" not in diff and "pycache" not in diff
    assert tree_diff(before, before) == ""


def test_done_reads_existing_trials(tmp_path):
    path = tmp_path / "trials.jsonl"
    assert _done(path) == set()
    path.write_text('{"task_id": "T01", "model": "m", "trial": 1}\n\n{"task_id": "T01", "model": "m", "trial": 2}\n')
    assert _done(path) == {("T01", "m", 1), ("T01", "m", 2)}


def test_agent_config_has_the_three_sections():
    config = yaml.safe_load(AGENT_CONFIG.read_text())
    assert set(config) == {"agent", "environment", "model"}
    assert "{{task}}" in config["agent"]["instance_template"]
    assert "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" in config["agent"]["instance_template"]
