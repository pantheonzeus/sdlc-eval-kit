"""Fixed failure taxonomy for error analysis. Every failed trial gets exactly one label."""

LABELS = {
    "misread_brief": "Solved a different problem than the brief asked for.",
    "wrong_file": "Changed the wrong module or location; the right code was never touched.",
    "incomplete": "Right place and intent, but part of the brief is missing or wrong.",
    "broke_other_tests": "Hidden tests may pass, but the seed's own tests now fail.",
    "edited_or_gamed_tests": "Edited, deleted or special-cased tests instead of fixing the code.",
    "environment_error": "Sandbox, dependency or tool failure unrelated to the agent's reasoning.",
    "gave_up": "Agent stopped and declared the task impossible or finished without a change.",
    "step_cap": "Hit the step limit before finishing.",
    "cost_cap": "Hit the euro cap before finishing.",
}


def auto_hint(record: dict) -> str:
    """A first guess from mechanical signals. It never replaces a human label."""
    if record.get("exit_status") in ("step_cap", "cost_cap"):
        return record["exit_status"]
    if record.get("exit_status") == "error":
        return "environment_error"
    if record.get("touched_tests"):
        return "edited_or_gamed_tests"
    if record.get("hidden_passed") and not record.get("visible_passed"):
        return "broke_other_tests"
    return ""
