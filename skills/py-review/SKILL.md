---
name: py-review
description: Route Python code review to focused skills for type safety, error handling, anti-patterns, async behavior, and code style. Use before or during Python code review to orient on project version, maturity, toolchain, changed files, and which py-* review skills should be loaded.
---

# Python Review Router

Use this skill first for Python code review. Orient on context, then load only
the focused skills that match the changed code.

## Before Reviewing: Orient

1. Check Python version from `pyproject.toml`, `setup.cfg`, `tox.ini`, CI, or README.
   - If `>=3.10`: load all relevant core skills, but apply each rule only when its Python/tool caveat matches.
   - If `3.8-3.9`: skip syntax rules requiring `>=3.10`.
   - If unknown: assume minimum 3.10, but phrase version-sensitive findings conservatively.

2. Classify project maturity.
   - Active/greenfield: full rule set is appropriate.
   - Mature legacy/maintenance-only: prioritize CRITICAL and HIGH findings.
   - Automation/scripts: prioritize safety, correctness, resource handling, and clear errors.

3. Check toolchain.
   - If the project uses `pyright`, do not recommend `mypy`-specific config.
   - If the project uses `ruff`, defer style/import findings to its configuration.
   - If no tool is configured, make tool suggestions low-severity unless the issue is correctness-related.

4. Read the exact changed files before flagging issues.
   - Cite file and line for every finding.
   - Do not issue generic findings without local evidence.
   - A rule match is a signal, not a verdict.

## Routing

| Changed code touches... | Load | Skip when... |
|-------------------------|------|--------------|
| annotations, `Any`, casts, generics, protocols, public APIs | `py-type-safety` | change is trivial and has no typed surface |
| exceptions, validation, cleanup, retries, batch failures | `py-error-handling` | no failure path changed |
| defaults, config, resource use, ORM/API boundaries, mixed I/O/business logic | `py-anti-patterns` | change is docs/config only |
| `async def`, event loops, FastAPI/httpx/aio*, tasks, cancellation | `py-async-patterns` | project/change is sync-only |
| formatting, names, imports, docstrings, lint/type config | `py-code-style` | tool output already covers it or review requested correctness only |

## Portability Note

The "Load" column tells you which focused skill's rules to apply for each
change type. How you access those rules depends on your agent runtime:

- **Dynamic loading**: If your agent supports activating skills mid-session,
  make the named skill discoverable and activate it when the routing table
  signals its scope.
- **Static checklist**: Read the focused skill's `SKILL.md` file directly
  from the skills directory and apply its rules as a review checklist.

Both approaches produce the same review outcome. The routing table is the
decision tree; the focused skill provides the rule set.

## Review Output

Lead with bugs and behavioral risks. Keep style-only findings behind correctness
findings. For legacy code, prefer actionable high-impact issues over broad
modernization advice.

## Sensitive Evidence Safety

If changed code or tool output reveals a suspected credential, token, private
key, secret-bearing URL, or other sensitive value, do not quote or reproduce the
value. Report only its existence and location. Treat filename and pattern checks
as heuristic evidence, not proof that a repository is secret-free.

If the exposure appears credible, make it the first finding, stop lower-priority
review, and recommend revocation or rotation. Never place sensitive values in
reports, generated examples, or commit subjects or bodies.
