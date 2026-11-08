# Method

## Tasks

A task is a directory under `tasks/`:

```text
tasks/<id>/
  task.yaml        id, seed, archetype, evaluation, brief
  hidden_tests/    test_*.py, copied in only at scoring time
  reference/       the changed files of a human solution, overlaid on the seed
```

- **Seed:** one of three small Python codebases in `seeds/`: a unit converter, an invoice calculator and a CSV validator. Each has its own test suite. They were written for this kit, so no model has trained on them.
- **Archetype:** `feature`, `bug`, `refactor`, `upgrade` or `docs`. Results are broken down by archetype, because agents fail differently on each.
- **Evaluation:** `verifiable` (hidden tests decide) or `judgement` (needs a rubric). All ten current tasks are verifiable.
- **Brief:** what the agent is told, written like a ticket. It states the expected behaviour precisely enough that the hidden tests are fair.

**Soundness check.** `sdlc-eval check-tasks` proves two things for every task. On the untouched seed, the hidden tests **fail**. With the reference solution overlaid, the hidden tests and the seed's own tests **pass**. A task that fails either check is broken, not hard.

## Scoring

The scorer copies the agent's workspace and then:

1. Compares the agent's `tests/` with the seed's. Any difference sets `touched_tests`.
2. **Discards the agent's tests and restores the originals.** Editing, deleting or adding tests can never turn a run green.
3. Runs the seed's own tests. If they fail, the change broke something.
4. Copies the hidden tests in and runs them.

A trial passes only if both suites pass.

## Metrics

- **pass@1:** the mean per-task success rate over all trials.
- **pass^k** ([τ-bench, arXiv:2406.12045](https://arxiv.org/abs/2406.12045)): the probability that k independent trials of the same task all succeed, estimated per task as C(c, k) / C(n, k) and averaged over tasks. This is the number that matters when you need the agent to work *every* time.
- **95% Wilson intervals** on both.
- **€ per success:** total API cost divided by successful trials. Local models are costed at €0 plus wall time.
- Mean tool calls and wall time per trial.

## Error analysis

Every failed trial gets exactly one label:

| Label | Meaning |
|---|---|
| `misread_brief` | Solved a different problem than the brief asked for. |
| `wrong_file` | Changed the wrong module; the right code was never touched. |
| `incomplete` | Right place and intent, but part of the brief is missing or wrong. |
| `broke_other_tests` | The seed's own tests now fail. |
| `edited_or_gamed_tests` | Edited, deleted or special-cased tests instead of fixing the code. |
| `environment_error` | Sandbox, dependency or tool failure, unrelated to the agent's reasoning. |
| `gave_up` | Stopped and declared the task impossible, or finished without a change. |
| `step_cap` | Hit the step limit. |
| `cost_cap` | Hit the euro cap. |

`sdlc-eval errors` writes `results/error_analysis.csv` with a mechanical hint per failure (for example, touched tests suggest `edited_or_gamed_tests`). **A human fills in the label column.** Rerunning keeps existing labels, and `sdlc-eval results` refuses any label outside the table.

## Results are generated, never edited

Each run stores one JSON line per trial in `runs/<run_id>/trials.jsonl`. `sdlc-eval results` derives `RESULTS.md` from those logs and the labels, and regenerating it gives byte-identical output.

## Limitations and threats to validity

- **Ten tasks are few.** The intervals will be wide, and the kit reports them rather than hiding them.
- **Trials within a task are correlated.** The pass@1 interval treats them as independent, so it is too narrow. The pass^k interval counts tasks and is the honest one.
- **Small seed codebases are not production systems.** They trade realism for zero contamination and full control of the hidden tests.
- **One author wrote the tasks, tests and references,** so ambiguous briefs are a real risk. A second reader will check each brief against its hidden tests before the first published run.
