# sdlc-eval-kit

**One run of a coding agent tells you little.** The same agent on the same task, run three times, often disagrees with itself. Public benchmarks have a second problem: their tasks are on the internet, so models may have seen them in training. sdlc-eval-kit measures agents in a way that avoids both problems:

- **Fresh tasks.** Ten tasks written for this kit, on three small codebases that exist nowhere else.
- **Hidden tests.** The agent never sees them. They're copied in only after the agent has finished.
- **Repeated trials.** Every task runs k times per model. The kit reports **pass^k**, the chance that *all* k runs succeed, next to pass@1.
- **Cost per success,** in euros, from provider usage data.
- **Error analysis.** Every failure gets one label from a fixed taxonomy, assigned by a human before any automatic label is trusted.

!!! warning "Status: pre-release, no results yet"
    The tasks, scorer, statistics and report generator are built and tested, and every task is proven sound. The agent runner, which drives an open-source coding agent in a fresh container against a local and an API model, is the next step. Until it runs, there are no numbers on this site, and there won't be any invented ones.

## What a result will look like

| Model | Version | Tasks | Trials | pass@1 | pass^3 | €/success |
|---|---|---:|---:|---|---|---:|
| *pending* | | 10 | 30 | x% [95% CI] | y% [95% CI] | €z |

Each result comes with the labelled failure breakdown, the model versions and run dates, and the stored logs it was generated from.

## Read on

- [Method](method.md): how tasks, scoring, the metrics and the error taxonomy work, and their limits.
- [Tasks](tasks.md): the ten tasks and their briefs.
- [Reproduce](reproduce.md): run the checks yourself and score a workspace.
