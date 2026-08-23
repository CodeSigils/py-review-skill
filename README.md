# py-review-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/py-review-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/py-review-skill/actions)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

**py-review-skill** reviews existing Python code through an AI agent. It routes
evidence-backed review across type safety, error handling, anti-patterns, async
behavior, and code style without imposing a new project toolchain.

Load `py-review` first when you want a code review. It inspects the project's
Python version, maturity, toolchain, and changed files, then routes only to the
relevant focused skills. If the diff has no async code, `py-async-patterns`
stays quiet.

| Skill | Scope |
|---|---|
| `py-review` | Context router — dispatches to sub-skills by change type |
| `py-type-safety` | Any leaks, missing annotations, unsafe Optional, generics |
| `py-error-handling` | Boundary validation, generic exceptions, chaining, cleanup |
| `py-anti-patterns` | Hard-coded config, mixed I/O/logic, mutable defaults |
| `py-async-patterns` | Blocking calls, missing await, gather, cancellation, timeouts |
| `py-code-style` | Tool-aligned style, imports, naming, docstrings, regex/string hygiene |

Each focused skill is a single `SKILL.md` with inline review rules. The
router contains no review rules; it selects focused skills that match the
changed code. No external configuration or platform-specific runtime commands
ship with the payload.

The payload is agentskills.io-compatible and structurally portable across
Hermes, Claude Code, Codex, Gemini CLI, and OpenCode. Historical workflow
evidence covers Codex and Hermes at the recorded payload revision; other
installation paths remain runtime-unverified.

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

1. **Install all six skills together** — the router expects the five focused
   skills to be discoverable from the same skill directory.
2. **Load `py-review` first** — it inspects the project's Python version,
   maturity, toolchain, and changed files, then dispatches to sub-skills.
3. **Sub-skills load on demand** — only the focused skills matching the
   changed code are activated (type annotations → `py-type-safety`,
   async code → `py-async-patterns`, etc.).
4. **Review findings, not rule matches** — each finding must cite changed code
   and explain a concrete behavioral or maintenance risk.
5. **Keep review bounded** — default to one discovery pass and one post-fix
   verification pass; continue only for a newly exposed concrete regression.

Focused skills can also be loaded directly for a narrowly scoped review. Each
one carries its own rules and sensitive-evidence safety contract, so secret-safe
reporting does not depend on the router being active.

---

## Skill Payload — What Ships to the User

Only the `skills/` directory ships to an agent. It contains six standalone
Markdown instruction files: one router and five focused reviewers.

```text
skills/
├── py-review/SKILL.md                    # context router and review ordering
├── py-type-safety/SKILL.md               # annotations, Any, Optional, generics
├── py-error-handling/SKILL.md            # validation, exceptions, cleanup
├── py-anti-patterns/SKILL.md             # configuration, boundaries, defaults
├── py-async-patterns/SKILL.md            # blocking, await, cancellation, timeouts
└── py-code-style/SKILL.md                # style, imports, names, regex/string hygiene
```

What users receive:

- agentskills.io `name` and `description` frontmatter in every skill;
- inline routing or review instructions with no deferred rule files;
- sensitive-evidence guards in every standalone skill; and
- no runtime scripts, configuration files, dependencies, test fixtures, or
  maintainer-only validation tooling.

Copy the complete `skills/` directory to preserve router-to-skill discovery.
Everything outside it is repository-only development infrastructure.

## Security Model

Reviewing code can reveal credentials in changed files or tool output. Every
shipped skill therefore directs the agent to report only the existence and
location of suspected sensitive material, never reproduce its value, prioritize
credible exposure, and recommend revocation or rotation. Pattern or filename
checks are heuristic evidence, not proof that a repository is secret-free.

Repository disclosure policy, CI trust boundaries, and mechanically checked
skill guarantees are documented in [SECURITY.md](SECURITY.md).

---

## Repo Layout

```text
py-review-skill/
├── AGENTS.md                                 # cold-landing agent orientation
├── README.md                                 # you are here
├── SECURITY.md                               # vulnerability reporting and payload trust
├── LICENSE                                   # MIT
├── .gitignore                                # local artifacts and populated env files
├── pyproject.toml                            # project metadata + ruff config
├── test-cases.json                           # generated inline examples
├── review-fixtures.json                      # end-to-end routing fixtures
├── evals/codex/                              # optional agent behavior contracts
├── docs/
│   ├── compatibility.md                      # per-agent support evidence
│   ├── runtime-matrix.json                   # machine-readable runtime status source
│   ├── codex-regression.md                   # behavioral evaluation workflow
│   ├── extraction-log.md                     # source provenance
│   └── methodology-alignment.md              # design principles
├── scripts/
│   ├── validate.py                           # schema, security, payload, and fixture checks
│   ├── validate-compatibility.py             # compatibility evidence contract
│   ├── validate-readme.py                    # README + CI routing contract
│   ├── extract-tests.py                      # generate test-cases from examples
│   ├── validate-review-fixtures.py           # router-to-skill fixture checks
│   ├── run-codex-regression.py               # optional isolated model runs
│   ├── grade-codex-regression.py             # deterministic behavior grader
│   ├── check-expiry.py                       # freshness marker checks
│   ├── check-runtime-matrix.py               # compatibility table consistency
│   ├── check-package-metadata.py             # package and skill-surface smoke checks
│   ├── report-action-freshness.py            # scheduled pinned-action report
│   └── verify-urls.py                        # URL reachability checks
├── .github/
│   ├── workflows/ci.yml                      # full validation CI pipeline
│   ├── workflows/readme.yml                  # lightweight README contract
│   ├── workflows/dependency-freshness.yml    # scheduled action freshness report
│   ├── workflows/release.yml                 # validated-tag release publisher
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

Runtime versions and compatibility states are maintained in
[`docs/runtime-matrix.json`](docs/runtime-matrix.json). CI checks that the
human-readable compatibility tables match that source.

The router's "Load" instruction is inherently agent-dependent — each
runtime has its own mechanism for activating skills. A portability note
in the router skill covers both dynamic-loading and static-checklist
approaches, giving the routing logic a runtime-neutral fallback.

Structural portability does not prove runtime behavior. The current evidence
matrix, fixture, deviations, and support boundaries are recorded in
[`docs/compatibility.md`](docs/compatibility.md). Codex CLI is workflow-verified;
Hermes is workflow-verified with finding-quality deviations. Other documented
install paths remain unverified until an isolated agent run is recorded.

Behavioral regressions for untracked changes and reviewer-sandbox failures are
documented in [`docs/codex-regression.md`](docs/codex-regression.md). Normal CI
runs only their deterministic self-tests; authenticated model runs are optional.

---

## Validate

```bash
python3 scripts/validate.py             # skill, security, fixture, and ignore contracts
python3 scripts/validate-compatibility.py # compatibility claims + review date
python3 scripts/validate-readme.py      # README coverage + lightweight CI routing
python3 scripts/extract-tests.py --check # test-case freshness
python3 scripts/validate-review-fixtures.py # router-to-skill fixtures
python3 scripts/run-codex-regression.py --self-test # fixture + runner contract
python3 scripts/grade-codex-regression.py --self-test # deterministic grading
python3 scripts/check-expiry.py         # expiry markers
python3 scripts/verify-urls.py          # URL reachability (scheduled/manual CI)
python3 .github/scripts/check-portability.py  # cross-agent gate
```

CI exercises the latest three declared Python targets: Python 3.12, Python 3.13,
and Python 3.14.
The package metadata continues to support Python 3.10 and newer; the oldest
supported version remains a documented compatibility boundary rather than a
full matrix lane.

Workflow runners use `ubuntu-latest` by default. Maintainers can override the
runner centrally with the repository variable `RUNNER_X86_64` without editing
workflow files.

The routing fixtures require both positive and non-routing coverage for every
focused skill, preventing a trigger change from silently under-routing or
over-routing reviews.

---

## License

MIT — see [LICENSE](LICENSE).
