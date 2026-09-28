# Portability Contract

**Status:** normative maintainer contract

**Scope:** packaging, adapter, validation, and compatibility claims for this
repository. This file is maintainer documentation and is not part of the
shipped skill payload.

## Canonical payload

`skills/py-review/SKILL.md` is the router. The five
`skills/<focused-skill>/SKILL.md` files are standalone focused skills. Together
these six files are the sole runtime source and installable artifact.

The router and each focused skill use only agentskills.io base frontmatter
(`name` + `description`) and reference only generic CLI tools — no
agent-specific commands, paths, or imports. This is enforced by
`.github/scripts/check-portability.py` in CI.

## Evidence levels

Use these claims consistently:

| Claim             | Required evidence                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| Payload portable  | Canonical files have valid frontmatter, contain no agent-specific references (CI gate passes), and have no known platform-only runtime dependency |
| Install verified  | A named runtime and version discovers or installs the exact payload through a recorded procedure  |
| Workflow verified | That runtime completes representative positive and negative tasks against the behavioral contract |

Evidence at one level does not establish the next.

## Runtime states

Use `candidate`, `install_verified`, `workflow_verified`, `historical`,
`limited`, or `unsupported`. `historical` preserves a successful run whose
payload, runtime, or evaluation contract is no longer current; it is not a
current support claim. Record the runtime version, date, installation path,
explicit and implicit selection, scenarios, evidence or grading criteria, and
limitations.

Do not extrapolate a result to untested runtimes or later versions. A material
change to any `SKILL.md`, the behavioral contract, prompt, or grader starts a
new evidence baseline.

## Current status

The canonical payload passes:
- Deterministic format, frontmatter, and reference validation (`validate.py`)
- Portability marker check (`check-portability.py`)
- Evaluation fixture and schema integrity

| Runtime                  | Version    | Status             |
| ------------------------ | ---------- | ------------------ |
| Hermes Agent             | 0.18.2     | `limited`          |
| Codex CLI                | 0.133.0    | `historical`        |
| Claude Code              | Not recorded | `candidate`      |
| Cursor                   | Not recorded | `candidate`      |
| Gemini CLI               | Not recorded | `candidate`      |
| OpenCode                 | Not recorded | `candidate`      |

Compatibility evidence and limitations are recorded in `docs/codex-regression.md`,
`docs/compatibility.md`, `docs/extraction-log.md`, and
`docs/methodology-alignment.md`.

## Adding runtime evidence

1. Select one runtime as an active target.
2. Record its exact version and discovery or installation path.
3. Test explicit and implicit selection with positive and negative scenarios.
4. Preserve reproducible or raw evidence without exposing sensitive values.
5. Grade against `evals/codex/cases.json` for focused skills (regression) or
   `review-fixtures.json` for the router workflow.
6. Record limitations and the narrowest supported state in
   `docs/compatibility.md`.

Keep model evaluation non-blocking. Reuse this contract and fixture vocabulary
before creating a runtime-specific runner. Extract a generic harness only after
two concrete uses share the same lifecycle and grading needs.

## Version consistency

The router plus five focused skills are versioned as one repository payload.
`pyproject.toml` is the package-version authority; user-facing docs deliberately
do not duplicate that version. `validate-readme.py` keeps the documented
validation gate aligned, while `validate-compatibility.py` checks declared
runtime boundaries and compatibility claims.
