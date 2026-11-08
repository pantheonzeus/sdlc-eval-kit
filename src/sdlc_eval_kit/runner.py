"""Run a coding agent on tasks: one fresh, network-less container per trial.

Each trial starts mini-swe-agent against a new container that holds a copy of the task's seed
repo. When the agent stops, its workspace is copied out and scored in a second fresh container
the agent never touched. Results append to runs/<run_id>/trials.jsonl; every trial's
trajectory and diff are kept next to it, so failures can be labelled from the record.
"""

import difflib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from sdlc_eval_kit.score import materialize
from sdlc_eval_kit.task import Task

IMAGE = "sdlc-eval-kit:0.1"
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
AGENT_CONFIG = Path(__file__).with_name("agent.yaml")
CONTAINER_ARGS = ["--rm", "--network", "none", "--memory", "2g", "--pids-limit", "256"]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class RunConfig:
    model: str  # litellm model name, e.g. ollama_chat/qwen3-coder:30b
    k: int = 3
    step_limit: int = 50
    num_ctx: int = 32768


def model_label(model: str) -> str:
    """The model name without the litellm provider prefix."""
    return model.split("/", 1)[-1]


def default_run_id(model: str, today: date) -> str:
    return f"{today:%Y%m%d}-" + re.sub(r"[^a-z0-9]+", "-", model_label(model).lower()).strip("-")


def exit_status(info: dict, n_calls: int, step_limit: int) -> str:
    """Map mini-swe-agent's exit status onto the statuses taxonomy.auto_hint knows."""
    status = info.get("exit_status", "")
    if status == "Submitted":
        return "submitted"
    if status == "LimitsExceeded":
        return "step_cap" if n_calls >= step_limit else "cost_cap"
    if status == "RepeatedFormatError":
        return "format_error"
    return "error"


def usage(messages: list[dict]) -> dict:
    """Token and tool-call counts from a trajectory's messages."""
    counts = [(message.get("extra", {}).get("response") or {}).get("usage") or {} for message in messages]
    return {
        "tokens_in": sum(c.get("prompt_tokens") or 0 for c in counts),
        "tokens_out": sum(c.get("completion_tokens") or 0 for c in counts),
        "tool_calls": sum(1 for message in messages if message.get("role") == "tool"),
    }


def tree_diff(before: Path, after: Path) -> str:
    """Unified diff of two directory trees, paths relative to their roots."""
    files = sorted({p.relative_to(root) for root in (before, after) for p in _files(root)})
    out = []
    for rel in files:
        a, b = _lines(before / rel), _lines(after / rel)
        if a != b:
            out += difflib.unified_diff(a, b, f"a/{rel}", f"b/{rel}")
    return "".join(line if line.endswith("\n") else line + "\n" for line in out)


def run(tasks: list[Task], cfg: RunConfig, root: Path, run_id: str, log=print) -> list[dict]:
    """Run cfg.k trials of every task, skipping trials already in the run's trials.jsonl."""
    if not cfg.model.startswith("ollama"):
        raise SystemExit("Only local Ollama models for now: API cost accounting arrives with step 0.7.")
    version = ollama_digest(model_label(cfg.model))
    image = image_id()
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    done = _done(run_dir / "trials.jsonl")
    records = []
    for task in tasks:
        for n in range(1, cfg.k + 1):
            if (task.id, model_label(cfg.model), n) in done:
                continue
            record = run_trial(task, n, cfg, root, run_dir / task.id / f"t{n}")
            record |= {"run_id": run_id, "model_version": version, "image": image}
            with (run_dir / "trials.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
            records.append(record)
            log(
                f"{task.id} t{n}: {'PASS' if record['passed'] else 'fail'} ({record['exit_status']}, "
                f"{record['tool_calls']} tool calls, {record['wall_s']:.0f} s)"
            )
    return records


def run_trial(task: Task, n: int, cfg: RunConfig, root: Path, trial_dir: Path) -> dict:
    """One agent trial in a fresh container, scored in another. Keeps trajectory.json and diff.patch."""
    os.environ.setdefault("MSWEA_SILENT_STARTUP", "1")
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    from minisweagent import __version__ as mini_version
    from minisweagent.agents.default import DefaultAgent
    from minisweagent.environments.docker import DockerEnvironment
    from minisweagent.models.litellm_model import LitellmModel

    shutil.rmtree(trial_dir, ignore_errors=True)
    trial_dir.mkdir(parents=True)
    seed = materialize(task, root / "seeds", trial_dir / "seed", False)
    config = yaml.safe_load(AGENT_CONFIG.read_text(encoding="utf-8"))
    model_cfg = config["model"] | {"model_kwargs": config["model"]["model_kwargs"] | {"num_ctx": cfg.num_ctx}}
    model = LitellmModel(model_name=cfg.model, cost_tracking="ignore_errors", **model_cfg)

    start = time.monotonic()
    env = DockerEnvironment(image=IMAGE, run_args=CONTAINER_ARGS, **config["environment"])
    try:
        _docker("cp", f"{seed}/.", f"{env.container_id}:/work")
        setup = env.execute({"command": "git init -q && git add -A && git commit -qm seed"})
        if setup["returncode"] != 0:
            raise RuntimeError(f"workspace setup failed: {setup['output']}")
        agent = DefaultAgent(
            model,
            env,
            step_limit=cfg.step_limit,
            cost_limit=0,
            output_path=trial_dir / "trajectory.json",
            **config["agent"],
        )
        try:
            status = exit_status(agent.run(task.brief), agent.n_calls, cfg.step_limit)
        except Exception:
            status = "error"
        wall = time.monotonic() - start
        _docker("cp", f"{env.container_id}:/work", str(trial_dir / "workspace"))
    finally:
        _docker("rm", "-f", env.container_id, check=False)
        env.container_id = None

    workspace = trial_dir / "workspace"
    (trial_dir / "diff.patch").write_text(tree_diff(seed, workspace), encoding="utf-8")
    result = score_in_container(task.id, workspace, root)
    shutil.rmtree(seed)
    shutil.rmtree(workspace)
    return {
        "task_id": task.id,
        "archetype": task.archetype,
        "model": model_label(cfg.model),
        "trial": n,
        "date": date.today().isoformat(),
        **result,
        "exit_status": status,
        "cost_eur": 0.0,
        **usage(agent.messages),
        "steps": agent.n_calls,
        "step_limit": cfg.step_limit,
        "wall_s": round(wall, 1),
        "agent": f"mini-swe-agent {mini_version}",
    }


def score_in_container(task_id: str, workspace: Path, root: Path) -> dict:
    """Score a copied-out workspace in a fresh container that mounts the kit and workspace read-only."""
    out = _docker(
        "run",
        *CONTAINER_ARGS,
        "-e",
        "PYTHONPATH=/kit/src",
        "-v",
        f"{root.resolve()}:/kit:ro",
        "-v",
        f"{workspace.resolve()}:/ws:ro",
        IMAGE,
        "python",
        "-m",
        "sdlc_eval_kit.cli",
        "--root",
        "/kit",
        "score",
        task_id,
        "/ws",
    )
    return json.loads(out)


def ollama_digest(name: str) -> str:
    """Short digest of a pulled Ollama model, so results name a fixed model, not a moving tag."""
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as response:
        models = json.load(response)["models"]
    for entry in models:
        if entry["name"] == name:
            return entry["digest"][:12]
    raise SystemExit(f"Model {name} is not pulled in Ollama: run `ollama pull {name}`.")


def image_id() -> str:
    try:
        return _docker("image", "inspect", IMAGE, "-f", "{{.Id}}").strip()[7:19]
    except subprocess.CalledProcessError:
        raise SystemExit(f"Image {IMAGE} not found: run `make image`.") from None


def _docker(*args: str, check: bool = True) -> str:
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check, timeout=600).stdout


def _done(trials_jsonl: Path) -> set[tuple]:
    if not trials_jsonl.is_file():
        return set()
    lines = trials_jsonl.read_text(encoding="utf-8").splitlines()
    return {(r["task_id"], r["model"], r["trial"]) for r in map(json.loads, filter(str.strip, lines))}


def _files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*")
        if p.is_file() and not SKIP_PARTS & set(p.relative_to(root).parts) and p.suffix != ".pyc"
    ]


def _lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        return [f"<binary file, {path.stat().st_size} bytes>\n"]
