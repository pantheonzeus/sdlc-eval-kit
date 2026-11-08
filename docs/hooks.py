"""MkDocs hook: render the task catalog from tasks/*/task.yaml, so the site cannot drift from the tasks."""

from pathlib import Path

import yaml

TASKS = Path(__file__).resolve().parents[1] / "tasks"
MARKER = "<!-- task-catalog -->"


def on_page_markdown(markdown, page, config, files):
    if MARKER not in markdown:
        return markdown
    rows = ["| Task | Seed | Archetype | Brief |", "|---|---|---|---|"]
    for path in sorted(TASKS.glob("*/task.yaml")):
        task = yaml.safe_load(path.read_text(encoding="utf-8"))
        brief = " ".join(task["brief"].split())
        rows.append(f"| `{task['id']}` | {task['seed']} | {task['archetype']} | {brief} |")
    return markdown.replace(MARKER, "\n".join(rows))
