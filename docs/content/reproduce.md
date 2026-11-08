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

## Coming next

`make reproduce` will run 10 tasks × 2 models (one local, one API) × 3 trials end to end, for under €5 of API spend. It arrives with the agent runner.
