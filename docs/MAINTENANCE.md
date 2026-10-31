# Maintenance

> Last reviewed: 2026-10-31

Maintainer guide for `py-review-skill`. For contribution workflow see [CONTRIBUTING.md](../CONTRIBUTING.md); for security matters see [SECURITY.md](../SECURITY.md).

## Sources of truth

- **Agent guidance:** [AGENTS.md](../AGENTS.md)
- **Contribution workflow:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Security policy:** [SECURITY.md](../SECURITY.md)
- **Verification/usage:** [README.md](../README.md)
- **Compatibility/evidence:** [docs/compatibility.md](compatibility.md), [docs/runtime-matrix.json](runtime-matrix.json)
- **Research/decisions:** [docs/](.)
- **CI/workflows:** [.github/workflows/](../.github/workflows/)
- **Scripts (maintainer):** [scripts/](../scripts/)
- **Shipped payload:** [skills/](../skills/) (exactly the six files under `skills/`)

## Standard verification

The canonical, ordered full validation gate is defined in [CONTRIBUTING.md](../CONTRIBUTING.md). Run from repo root:

```bash
uv sync --locked --only-dev
uvx --from git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref skills-ref validate skills/py-review
uv run ruff check .
uv run ty check
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
python3 -m unittest discover -s tests
python3 scripts/validate-readme.py
```

Network-dependent (report separately if unavailable):

```bash
python3 scripts/verify-urls.py
```

Notes:
- Only `skills/` ships to users. Scripts, fixtures, CI, and docs are maintainer infrastructure.
- Preserve the sensitive-evidence contract in every standalone `SKILL.md` (focused skills may load without the router).
- If examples change, regenerate `test-cases.json` via `scripts/extract-tests.py --check` (do not edit generated examples manually).
- Update README and CONTRIBUTING together when gate changes; `validate-readme.py` enforces agreement.

## Automation

- **GitHub Actions:** [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  - `quality` (push/PR/tags/schedule paths): runs on `ubuntu-latest` (or `RUNNER_X86_64` override) with Python 3.14, `uv sync --locked --only-dev`, validates with `skills-ref`, runs lint/typecheck (`ruff`, `ty`), portability check, payload/compat/runtime-matrix/package-metadata validation, fixture/extract/checks, regression self-tests, expiry checks, and `verify-urls.py` only on schedule/workflow_dispatch.
  - `python-compat` (push/PR): matrix Python 3.12/3.13/3.14 with `fail-fast: false`; runs `python3 -m unittest discover -s tests` (package metadata supports >=3.10).
- **README contract:** [.github/workflows/readme.yml](../.github/workflows/readme.yml) — lightweight README contract validation.
- **Dependency freshness:** [.github/workflows/dependency-freshness.yml](../.github/workflows/dependency-freshness.yml) — weekly or manual dispatch.
- **Release:** [.github/workflows/release.yml](../.github/workflows/release.yml) — listens for successful `validate` runs caused by tag pushes; verifies exactly one `vX.Y.Z` tag points at the validated commit and publishes generated GitHub release notes. Actions are SHA-pinned.
- **Branch protection:** `main` is PR-only with required status checks (follow repo policy). Actions use explicit Python versions; runner override via `RUNNER_X86_64` repo variable.

## Volatility

**Medium-High** — monitor CI (quality + python-compat matrix), dependency freshness, and tag-driven releases. Pay attention to payload validation (`skills-ref`, `scripts/validate.py`), portability, regression self-tests, and compatibility evidence freshness. Inspect before VCS writes and on exceptions.

## Escalation

- **Payload/skills:** Changes to `skills/*/SKILL.md`, router behavior, or sensitive-evidence contract; `skills-ref` validation failures
- **Validation/CI:** Workflow changes, Action pin updates (update all occurrences), runner changes, required check changes; failures in `validate.py`, `validate-compatibility.py`, `check-runtime-matrix.py`, `check-package-metadata.py`, `extract-tests.py --check`, `validate-review-fixtures.py`, regression self-tests
- **Fixtures/examples:** Changes to `review-fixtures.json`, `test-cases.json` generation or consistency
- **Compatibility:** New runtime support claims, expired evidence in `docs/compatibility.md`/`docs/runtime-matrix.json`, or cross-agent discovery issues
- **Release:** Tag/release workflow issues, version claim mismatches (`pyproject.toml`, README, compatibility), or publishing problems
- **Security/URLs:** URL verification failures, security policy changes ([SECURITY.md](../SECURITY.md))
