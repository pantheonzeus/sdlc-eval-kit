# sdlc-eval-kit

[![ci](https://github.com/pantheonzeus/sdlc-eval-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/pantheonzeus/sdlc-eval-kit/actions/workflows/ci.yml)

**Documentation:** https://pantheonzeus.github.io/sdlc-eval-kit/

**Claim (to be measured):** one run of a coding agent tells you little. The same agent on the same task, run three times, often disagrees with itself, so pass@1 overstates what you can rely on. This kit measures the gap: fresh tasks, hidden tests, k trials, cost per success, and every failure labelled by hand.

> **Status: pre-release (v0.1.0). No results yet.** The tasks, scorer, statistics, report generator and agent runner are in place and tested; the runner drives local Ollama models today. API models wait for cost accounting. Until a full run is published, the table below stays empty on purpose.

## Results

| Model | Version | Tasks | Trials | pass@1 | pass^3 | €/success | € total |
|---|---|---:|---:|---|---|---:|---:|
| — | — | — | — | — | — | — | — |

`RESULTS.md` is generated from the stored run logs and is never edited by hand.

## Reproduce

```console
uv sync
make check        # lint, unit tests, and the task soundness check below
make image       # the sandbox image, needs Docker
uv run --extra runner sdlc-eval run --model ollama_chat/qwen3-coder:30b   # local model, k=3 per task
make reproduce    # arrives with API cost accounting: 10 tasks x 2 models x k=3, under €5 API cost
```

Every trial runs [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) in a fresh container with no network. Its workspace is then scored in a second fresh container that the agent never touched. The trajectory and diff of every trial are kept in `runs/`.

`make check` proves that every task is sound: its hidden tests **fail** on the untouched seed repo, and **pass** together with the seed's own tests on the human reference solution.

## What is measured

- **Tasks** (`tasks/`): 10 tasks written fresh for this kit, so no model has seen them in training. They run on three small seed repos (`seeds/`): a unit converter, an invoice calculator and a CSV validator. The archetypes are feature (4), bug (3), refactor (1), upgrade (1) and docs (1).
- **Hidden tests:** the agent never sees them. Scoring discards the agent's copy of the visible tests and restores the originals, so editing a test can never turn a run green. Touched tests are recorded as a signal for error analysis.
- **pass@1:** mean per-task success rate. **pass^k:** the chance that k independent trials of a task *all* succeed ([τ-bench](https://arxiv.org/abs/2406.12045)). Both carry 95% Wilson intervals.
- **Cost:** euros per successful task, from provider usage fields. Local models are costed at €0 plus wall time.

## Error analysis

Every failed trial gets one label from a fixed taxonomy (`src/sdlc_eval_kit/taxonomy.py`): misread brief, wrong file, incomplete, broke other tests, edited or gamed tests, environment error, gave up, step cap, cost cap. `sdlc-eval errors` writes `results/error_analysis.csv` with a mechanical hint per failure. **A human fills the `label` column** before any auto-label is trusted, and `sdlc-eval results` refuses unknown labels.

## Limitations and threats to validity

- **Ten tasks are few.** Intervals will be wide. The kit reports them rather than hiding them.
- **Trials within a task are correlated.** The pass@1 interval treats trials as independent and is therefore too narrow; the pass^k interval counts tasks and is the honest one.
- **Small, self-written seed repos** are not production codebases. They trade realism for zero contamination and full control of the hidden tests.
- **One author wrote tasks, tests and references.** Brief ambiguity is a real risk; a second reader reviewing each brief against its hidden tests is planned before the first published run.

## Task format

```text
tasks/<id>/
  task.yaml        id, seed, archetype, evaluation (verifiable | judgement), brief
  hidden_tests/    test_*.py, copied in only at scoring time
  reference/       the changed files of a human solution, overlaid on the seed
```

## Licence

MIT. See `LICENSE`. Cite with `CITATION.cff`.
