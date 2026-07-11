# py-review-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/py-review-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/py-review-skill/actions)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

Portable Python code-review skills for agentskills.io-compatible agents.

This repo ships a routing skill plus five focused review skills that cover
type safety, error handling, anti-patterns, async patterns, and code style.
All skills use only base `name` + `description` frontmatter with no
agent-specific commands — compatible with Hermes, Claude Code, Codex CLI,
Gemini CLI, OpenCode, and any agentskills.io client.

- `py-review` — context router: inspects Python version, maturity, toolchain
- `py-type-safety` — Any leaks, missing annotations, unsafe Optional, generics
- `py-error-handling` — boundary validation, generic exceptions, chaining, cleanup
- `py-anti-patterns` — hard-coded config, mixed I/O/logic, mutable defaults
- `py-async-patterns` — blocking calls, missing await, gather, cancellation, timeouts
- `py-code-style` — tool-aligned style, imports, naming, docstrings

The runtime surface is intentionally small: `skills/*/SKILL.md` files use only
`name` and `description` frontmatter with rules inlined per skill.
Repo-local scripts validate the inline rule schema, extract test cases,
check freshness markers, and verify URL reachability.

---

## Quick Start

Make the skill set discoverable by your agent.

<details>
<summary><b>Hermes Agent</b></summary>

**Recommended for development — clone the repo and add to `external_dirs`:**
```yaml
skills:
  external_dirs:
    - /path/to/py-review-skill/skills
```
This loads all six skills directly from the repo — every commit is
immediately reflected without reinstalling.

**For end users — install from hub:**
```bash
hermes skills install CodeSigils/py-review-skill
```

*Other agents: see sections below for their native setup commands.*
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
cp -r skills/* ~/.claude/skills/
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
cp -r skills/* .codex/skills/
```
</details>

<details>
<summary><b>Gemini CLI / .agents/ path</b></summary>

```bash
cp -r skills/* .agents/skills/
```
</details>

<details>
<summary><b>OpenCode</b></summary>

```bash
cp -r skills/* .opencode/skills/
```
</details>

For agents that support external skill directories, point the config at
`skills/` for live-updating access.

---

## How to Use

1. **Load `py-review` first** — it inspects the project's Python version,
   maturity, toolchain, and changed files, then dispatches to sub-skills.
2. **Sub-skills load on demand** — only the focused skills matching the
   changed code are activated (type annotations → `py-type-safety`,
   async code → `py-async-patterns`, etc.).
3. **Rules are inline** — each sub-skill is a single `SKILL.md` with
   5-7 review rules. No per-rule files, no external references.

All skills are self-contained. No external setup, config files, or
environment variables required.

---

## What This Repo Contains

```text
py-review-skill/
├── AGENTS.md                                 # cold-landing agent orientation
├── README.md                                 # you are here
├── SECURITY.md                               # vulnerability reporting
├── LICENSE                                   # MIT
├── .gitignore
├── pyproject.toml                            # project metadata + ruff config
├── test-cases.json                           # generated inline examples
├── docs/
│   ├── extraction-log.md                     # source provenance
│   └── methodology-alignment.md              # design principles
├── scripts/
│   ├── validate.py                           # rule schema enforcement
│   ├── extract-tests.py                      # generate test-cases from examples
│   ├── check-expiry.py                       # freshness marker checks
│   └── verify-urls.py                        # URL reachability checks
├── .github/
│   ├── workflows/ci.yml                      # 5-step CI pipeline
│   └── scripts/check-portability.py          # cross-agent portability gate
└── skills/
    ├── py-review/SKILL.md                    # router skill
    ├── py-type-safety/SKILL.md               # focused: type annotations
    ├── py-error-handling/SKILL.md            # focused: exceptions + cleanup
    ├── py-anti-patterns/SKILL.md             # focused: correctness traps
    ├── py-async-patterns/SKILL.md            # focused: asyncio pitfalls
    └── py-code-style/SKILL.md                # focused: style + tooling
```

---

## Portability

Each shipped `SKILL.md` is checked by CI for agent-specific references
(`skill_view`, `hermes skills`, platform adapter paths, etc.). If a commit
adds a platform-specific command, CI fails before it reaches the runtime.

The current surface is entirely cross-agent compatible — zero platform
references in any shipped skill file.

The router's "Load" instruction is inherently agent-dependent — each
runtime has its own mechanism for activating skills. A portability note
in the router skill covers both dynamic-loading and static-checklist
approaches so the routing logic works everywhere.

---

## Validate

```bash
python3 scripts/validate.py             # rule schema
python3 scripts/extract-tests.py --check # test-case freshness
python3 scripts/check-expiry.py         # expiry markers
python3 scripts/verify-urls.py          # URL reachability
python3 .github/scripts/check-portability.py  # cross-agent gate
```

---

## License

MIT — see [LICENSE](LICENSE).
