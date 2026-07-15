# py-review-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/py-review-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/py-review-skill/actions)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

**py-review-skill** — reviews Python code through an AI agent after it's been written. Covers type safety, error handling, anti-patterns, async patterns, and code style.

Load `py-review` first when you want a code review. It inspects the project's Python version, maturity, and toolchain, then activates only the relevant sub-skills based on what changed. If the diff has no async code, `py-async-patterns` stays quiet — less noise.

| Skill | Scope |
|---|---|
| `py-review` | Context router — dispatches to sub-skills by change type |
| `py-type-safety` | Any leaks, missing annotations, unsafe Optional, generics |
| `py-error-handling` | Boundary validation, generic exceptions, chaining, cleanup |
| `py-anti-patterns` | Hard-coded config, mixed I/O/logic, mutable defaults |
| `py-async-patterns` | Blocking calls, missing await, gather, cancellation, timeouts |
| `py-code-style` | Tool-aligned style, imports, naming, docstrings |

Each skill is a single SKILL.md with 5-7 inline rules and a verification checklist. No external config, no platform-specific commands. The router's portability note covers both dynamic-loading and static-checklist agent runtimes.

Compatible with Hermes, Claude Code, Codex, Gemini CLI, OpenCode, and any agentskills.io client.

For project setup and maintenance, pair this with [`python-project-workflow-skill`](https://github.com/CodeSigils/python-project-workflow-skill). It handles project structure, tooling, CI, packaging, and `.gitignore`; `py-review` focuses on evidence-backed findings in the code itself.

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

**For end users — clone the repository:**
```bash
git clone https://github.com/CodeSigils/py-review-skill.git
```

The skill is not currently indexed by Hermes Skills Hub under
`CodeSigils/py-review-skill`. After cloning, use the `external_dirs` setup above
until a hub identifier is published and verified.

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
cp -r skills/* .agents/skills/
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
├── review-fixtures.json                      # end-to-end routing fixtures
├── docs/
│   ├── compatibility.md                      # per-agent support evidence
│   ├── extraction-log.md                     # source provenance
│   └── methodology-alignment.md              # design principles
├── scripts/
│   ├── validate.py                           # rule schema enforcement
│   ├── validate-compatibility.py             # compatibility evidence contract
│   ├── validate-readme.py                    # README + CI routing contract
│   ├── extract-tests.py                      # generate test-cases from examples
│   ├── validate-review-fixtures.py           # router-to-skill fixture checks
│   ├── check-expiry.py                       # freshness marker checks
│   └── verify-urls.py                        # URL reachability checks
├── .github/
│   ├── workflows/ci.yml                      # full validation CI pipeline
│   ├── workflows/readme.yml                  # lightweight README contract
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

The current surface is structurally cross-agent portable — zero platform
references occur in any shipped skill file.

The router's "Load" instruction is inherently agent-dependent — each
runtime has its own mechanism for activating skills. A portability note
in the router skill covers both dynamic-loading and static-checklist
approaches, giving the routing logic a runtime-neutral fallback.

Structural portability does not prove runtime behavior. The current evidence
matrix, fixture, deviations, and support boundaries are recorded in
[`docs/compatibility.md`](docs/compatibility.md). Codex CLI is workflow-verified;
Hermes is workflow-verified with finding-quality deviations. Other documented
install paths remain unverified until an isolated agent run is recorded.

---

## Validate

```bash
python3 scripts/validate.py             # rule schema
python3 scripts/validate-compatibility.py # compatibility claims + review date
python3 scripts/validate-readme.py      # README coverage + lightweight CI routing
python3 scripts/extract-tests.py --check # test-case freshness
python3 scripts/validate-review-fixtures.py # router-to-skill fixtures
python3 scripts/check-expiry.py         # expiry markers
python3 scripts/verify-urls.py          # URL reachability (scheduled/manual CI)
python3 .github/scripts/check-portability.py  # cross-agent gate
```

CI checks the minimum supported Python 3.10 and the current stable boundary,
Python 3.14.

The routing fixtures require both positive and non-routing coverage for every
focused skill, preventing a trigger change from silently under-routing or
over-routing reviews.

---

## License

MIT — see [LICENSE](LICENSE).
