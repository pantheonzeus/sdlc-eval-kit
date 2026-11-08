"""Command line: sdlc-eval {validate,check-tasks,run,score,errors,results}."""

import argparse
import json
import sys
import tempfile
from dataclasses import asdict
from datetime import date
from pathlib import Path

from sdlc_eval_kit.results import export_errors, load_labels, load_trials, render_results
from sdlc_eval_kit.score import materialize, score
from sdlc_eval_kit.task import TaskError, load_tasks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdlc-eval", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="kit root holding tasks/, seeds/, runs/")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate every task.yaml")
    sub.add_parser("check-tasks", help="hidden tests must fail on the seed and pass on the reference")
    run_cmd = sub.add_parser("run", help="run an agent on tasks, k trials each, append to runs/<run_id>/")
    run_cmd.add_argument("--model", required=True, help="litellm model name, e.g. ollama_chat/qwen3-coder:30b")
    run_cmd.add_argument("--tasks", nargs="*", default=[], help="task ids (default: all)")
    run_cmd.add_argument("-k", type=int, default=3, help="trials per task")
    run_cmd.add_argument("--step-limit", type=int, default=50, help="model calls per trial")
    run_cmd.add_argument("--run-id", help="default: <date>-<model>; an existing run id resumes it")
    score_cmd = sub.add_parser("score", help="score a workspace against one task, print JSON")
    score_cmd.add_argument("task_id")
    score_cmd.add_argument("workspace", type=Path)
    sub.add_parser("errors", help="write results/error_analysis.csv, keeping existing labels")
    sub.add_parser("results", help="write RESULTS.md from runs/ and the labels")
    args = parser.parse_args(argv)

    root = args.root
    seeds, tasks_dir = root / "seeds", root / "tasks"
    labels_csv = root / "results" / "error_analysis.csv"
    try:
        tasks = load_tasks(tasks_dir, seeds)
    except TaskError as exc:
        print(f"task error: {exc}", file=sys.stderr)
        return 2

    if args.command == "validate":
        print(f"{len(tasks)} tasks valid")
        return 0
    if args.command == "check-tasks":
        return _check_tasks(tasks, seeds)
    if args.command == "run":
        from sdlc_eval_kit.runner import RunConfig, default_run_id, run

        unknown = sorted(set(args.tasks) - {t.id for t in tasks})
        if unknown:
            print(f"unknown task: {', '.join(unknown)}", file=sys.stderr)
            return 2
        selected = [t for t in tasks if not args.tasks or t.id in args.tasks]
        cfg = RunConfig(model=args.model, k=args.k, step_limit=args.step_limit)
        run(selected, cfg, root.resolve(), args.run_id or default_run_id(args.model, date.today()))
        return 0
    if args.command == "score":
        task = next((t for t in tasks if t.id == args.task_id), None)
        if task is None:
            print(f"unknown task: {args.task_id}", file=sys.stderr)
            return 2
        print(json.dumps(asdict(score(task, args.workspace, seeds))))
        return 0
    if args.command == "errors":
        unlabelled = export_errors(load_trials(root / "runs"), labels_csv)
        print(f"wrote {labels_csv}; {unlabelled} failures unlabelled")
        return 0
    text = render_results(load_trials(root / "runs"), load_labels(labels_csv))
    (root / "RESULTS.md").write_text(text, encoding="utf-8")
    print(f"wrote {root / 'RESULTS.md'}")
    return 0


def _check_tasks(tasks, seeds: Path) -> int:
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for task in tasks:
            base = score(task, materialize(task, seeds, Path(tmp) / task.id / "base", False), seeds)
            ref = score(task, materialize(task, seeds, Path(tmp) / task.id / "ref", True), seeds)
            problems = []
            if not base.visible_passed:
                problems.append("seed's own tests fail")
            if base.hidden_passed:
                problems.append("hidden tests already pass on the seed")
            if not ref.passed:
                problems.append("reference fails " + ("hidden" if not ref.hidden_passed else "visible") + " tests")
            bad += bool(problems)
            print(f"{'FAIL' if problems else 'ok  '} {task.id} {'; '.join(problems)}".rstrip())
    print(f"{len(tasks) - bad}/{len(tasks)} tasks sound")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
