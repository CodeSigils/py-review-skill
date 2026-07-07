# py-review-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

Portable Python code-review skills for agentskills.io-compatible agents.

This repo ships a routing skill plus five focused review skills:

- `py-review`
- `py-type-safety`
- `py-error-handling`
- `py-anti-patterns`
- `py-async-patterns`
- `py-code-style`

The runtime surface is intentionally small: `skills/*/SKILL.md` files use only
`name` and `description` frontmatter. Repo-local scripts validate the inline
rule schema and generate `test-cases.json`.

## What This Repo Contains

```text
skills/                  runtime skill folders loaded by agents
scripts/                 repo-local validation and drift checks
docs/                    source provenance and methodology notes
test-cases.json          generated examples extracted from inline rules
```

Rules stay inline in the focused `SKILL.md` files. The repo intentionally does
not use one file per rule.

## Install

Copy or symlink the desired skill folders into your agent's skills directory.

```bash
cp -r skills/py-review ~/.codex/skills/
cp -r skills/py-type-safety ~/.codex/skills/
cp -r skills/py-error-handling ~/.codex/skills/
cp -r skills/py-anti-patterns ~/.codex/skills/
cp -r skills/py-async-patterns ~/.codex/skills/
cp -r skills/py-code-style ~/.codex/skills/
```

For agents that support external skill directories, point them at `skills/`.

## Source Provenance

The first rule set was extracted from `wshobson/agents` at commit
`5cc2549a50fc672230efd0a0307e2fd27ffba792`. See
[docs/extraction-log.md](docs/extraction-log.md).

## Validate

```bash
python3 scripts/validate.py
python3 scripts/extract-tests.py --check
python3 scripts/check-expiry.py
python3 scripts/verify-urls.py
```
