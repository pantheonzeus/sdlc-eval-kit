# Changelog

## Unreleased

- `sdlc-eval run`: mini-swe-agent 2.4.6 in a fresh, network-less container per trial; scoring in a second fresh container; trajectory, diff, tokens, tool calls, wall time and the model's Ollama digest recorded per trial. Local Ollama models only until API cost accounting lands.
- Sandbox image (`docker/Dockerfile`, `make image`).

## 0.1.0 (pre-release)

- Task schema (`task.yaml`) with archetype and evaluation tags, and validation.
- Three seed repos and ten fresh tasks with hidden tests and reference solutions.
- `check-tasks`: hidden tests fail on each seed and pass on each reference.
- Scorer that restores pristine visible tests and adds hidden tests after the run.
- pass@1, pass^k and Wilson intervals; failure taxonomy; `error_analysis.csv` export; `RESULTS.md` generator.
- Documentation site on GitHub Pages, with the task catalog generated from `tasks/`.
