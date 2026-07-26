# Codex behavioral regression

The deterministic validators prove that the skill files are structurally
consistent. They cannot prove that an agent follows the review workflow.
This optional harness checks two behaviors observed during real use:

1. an untracked Python file is included in the review surface; and
2. a command blocked by a read-only reviewer sandbox is recorded as an
   environment limitation, not reported as a repository defect.

The harness follows the established local-agent regression pattern used by the
neighboring `repo-health-and-sync-skill`: isolated git fixtures, structured
final output, deterministic grading, retained raw evidence, and no model call in
normal CI.

## Deterministic checks

```bash
python3 scripts/run-codex-regression.py --self-test
python3 scripts/grade-codex-regression.py --self-test
```

These commands create temporary fixtures and exercise the grader without model
cost or authentication.

## Live regression

```bash
python3 scripts/run-codex-regression.py \
  --fixture-dir /tmp/py-review-fixtures \
  --output-dir artifacts/codex
```

The live run requires an authenticated `codex` CLI. It runs each case once in a
read-only sandbox and writes:

- one JSONL transcript, structured result, and stderr log per case;
- `run-summary.json` with commit, prompt, requested model, duration, status,
  paths, and token usage; and
- `grade.json` with case-level pass/fail evidence.

Use a fresh fixture directory for each run. Preserve failed artifacts; do not
rerun selectively and report only a passing attempt.

## Review budget

Model regression is an evidence tool, not a required loop. For normal reviews,
the router permits one discovery pass and one post-fix verification pass.
Continue only when verification exposes a new concrete regression. This
prevents repeated full-context reviews from consuming tokens without adding
new evidence.
