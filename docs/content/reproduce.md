# Reproduce

You need Python 3.12 and [uv](https://docs.astral.sh/uv/).

```console
git clone https://github.com/pantheonzeus/sdlc-eval-kit
cd sdlc-eval-kit
uv sync
make check
```

`make check` runs the linter, the unit tests and the task soundness check. It ends with:

```text
10/10 tasks sound
```

## Score a workspace yourself

You can score any attempt at a task by hand, from your own agent or your own keyboard:

```console
cp -r seeds/units-converter /tmp/attempt
# ... make your change in /tmp/attempt ...
uv run sdlc-eval score T02-units-fahrenheit-kelvin /tmp/attempt
```

```json
{"passed": true, "visible_passed": true, "hidden_passed": true, "touched_tests": false}
```

## From run logs to a report

```console
uv run sdlc-eval errors    # writes results/error_analysis.csv; fill in the label column
uv run sdlc-eval results   # writes RESULTS.md from runs/ and the labels
```

## Run an agent

You need Docker and [Ollama](https://ollama.com) with a model pulled.

```console
make image
ollama pull qwen3-coder:30b
uv run --extra runner sdlc-eval run --model ollama_chat/qwen3-coder:30b --tasks T02-units-fahrenheit-kelvin -k 1
```

Each trial starts [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 2.4.6 against a fresh container with no network, holding a copy of the seed repo. When the agent stops, its workspace is copied out and scored in a second fresh container that mounts the kit and the workspace read-only. The agent configuration is `src/sdlc_eval_kit/agent.yaml`.

A run appends to `runs/<date>-<model>/trials.jsonl` and keeps `trajectory.json` and `diff.patch` for every trial. The model is recorded by its Ollama digest, not its tag. Running the same command again resumes the run and skips trials already recorded. Default limits: 3 trials per task, 50 model calls per trial.

## Coming next

`make reproduce` will run 10 tasks × 2 models (one local, one API) × 3 trials end to end, for under €5 of API spend. It arrives with API cost accounting.
