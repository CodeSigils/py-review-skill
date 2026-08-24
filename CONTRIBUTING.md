# Contributing and maintenance

This is the maintainer entry point for `py-review-skill`. It follows a
Diátaxis-oriented structure:

- **Tutorial** — make and validate a focused change.
- **How-to** — update evidence, fixtures, and compatibility records.
- **Reference** — validation, CI, release, and payload boundaries.
- **Explanation** — why the repository separates runtime skills from tooling.

## Tutorial: make a focused change

1. Start from an up-to-date `main` and create a focused branch.
2. Change the smallest relevant file set. Only `skills/` is shipped to agents;
   scripts, fixtures, CI, and docs are maintainer infrastructure.
3. Preserve the sensitive-evidence contract in every standalone `SKILL.md`.
4. If examples change, regenerate `test-cases.json` with the extraction check.
5. Update the relevant documentation and compatibility evidence when behavior,
   installation guidance, or support claims change.
6. Run the full validation gate before opening a pull request.

Keep one logical change per pull request. Do not mix payload edits with
unrelated dependency or documentation cleanup.

## How-to: run the validation gate

From the repository root:

```bash
uv sync --locked --only-dev
uv run ruff check .
python3 .github/scripts/check-portability.py
python3 scripts/validate.py
python3 scripts/validate-compatibility.py
python3 scripts/check-runtime-matrix.py
python3 scripts/check-package-metadata.py
python3 scripts/extract-tests.py --check
python3 scripts/validate-review-fixtures.py
python3 scripts/run-codex-regression.py --self-test
python3 scripts/grade-codex-regression.py --self-test
python3 scripts/check-expiry.py
python3 -m unittest tests.test_release_workflow
python3 -m unittest tests.test_skill_contract
python3 scripts/validate-readme.py
```

The scheduled/manual URL check is network-dependent:

```bash
python3 scripts/verify-urls.py
```

If network access is unavailable, report that limitation; do not treat an old
URL result as current evidence.

## How-to: update rules or examples

### Focused skill rules

- Keep each focused skill self-contained and within the validator's rule budget.
- Use the required rule fields and include both incorrect and correct examples.
- Add `References`, `Checked`, and `Expires` together for version-sensitive
  guidance.
- Never add secrets, credential values, destructive probes, or agent-specific
  paths to the shipped payload.

### Router and fixtures

- Update routing only when the changed-code signal is concrete and evidence-based.
- Keep positive and non-routing cases for every focused skill in
  `review-fixtures.json`.
- Regenerate `test-cases.json` through `scripts/extract-tests.py`; do not edit
  generated examples manually.
- Run both regression self-tests after changing routing or output behavior.

## How-to: update compatibility evidence

1. Record the exact runtime version, model when relevant, installation path, and
   payload revision.
2. Test explicit and implicit discovery with positive and negative scenarios.
3. Preserve structured evidence without credentials or personal data.
4. Record deviations and the narrowest support level in `docs/compatibility.md`.
5. Update `docs/runtime-matrix.json` and its human-readable claims together.
6. Keep review-by dates current; expired evidence must be rechecked or narrowed.

Do not generalize one runtime result to other agents, models, versions, or later
payload revisions.

## Reference: CI and workflows

The `validate` workflow runs the full matrix on Python 3.12, 3.13, and 3.14.
The package metadata still supports Python 3.10 and newer, but Python 3.10 and
3.11 are compatibility boundaries rather than current matrix lanes.

The README workflow runs the lightweight README contract. Dependency freshness
runs weekly or by manual dispatch. The release workflow listens for successful
`validate` runs caused by tag pushes, verifies that exactly one `vX.Y.Z` tag
points at the validated commit, and publishes generated GitHub release notes.

Actions are SHA-pinned. Keep the runner override through the `RUNNER_X86_64`
repository variable; do not hard-code a different runner in one workflow.

## Reference: release process

1. Confirm `pyproject.toml`, `uv.lock`, and any version claims agree.
2. Run the full validation gate on the merged commit.
3. Create an annotated `vX.Y.Z` tag on that commit and push the tag.
4. Confirm the release workflow succeeds and generated notes are published.
5. Update `docs/compatibility.md` or the roadmap only when the release changes
   support claims or records a completed decision.

This repository does not maintain a separate changelog; GitHub release notes are
generated from commit history and pull requests.

## Explanation: shipped boundary

The runtime artifact is exactly the six files under `skills/`. It intentionally
contains no scripts, dependencies, configuration, fixtures, or platform adapter
directories. Keeping validation and research outside that directory allows
maintainers to improve evidence and CI without changing installation behavior.

Read [SECURITY.md](SECURITY.md) before reporting a vulnerability. Suspected
secrets must be reported by existence and location only, never reproduced.
