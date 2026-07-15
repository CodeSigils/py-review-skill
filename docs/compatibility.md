# Agent Compatibility Evidence

This document separates portable payload design from behavior verified in an
agent runtime. Passing the portability gate means a shipped skill contains no
agent-specific command or path; it does not prove discovery, routing, or finding
quality in every agentskills.io-compatible client.

**Evidence captured:** 2026-07-14
**Review by:** 2026-09-30

The review-by marker covers agent evidence plus current installation, Python,
and GitHub Actions support boundaries enforced by the compatibility validator.

## Support Levels

- **Structurally portable:** base frontmatter and agent-neutral runtime text pass
  the deterministic portability gate.
- **Workflow verified:** an implicit, read-only agent run discovered the router,
  loaded appropriate focused skills, and produced evidence-backed findings.
- **Workflow verified with deviations:** discovery and routing worked, but the
  recorded review contained material quality deviations.
- **Setup documented:** an installation path is documented but no workflow run
  has been recorded.

## Current Matrix

| Agent | Version and model | Installation under test | Status | Evidence boundary |
|---|---|---|---|---|
| Codex CLI | 0.133.0; `gpt-5.4` | Legacy repository-local `.codex/skills/` used by the recorded run | Workflow verified | Implicit router selection, four focused skills loaded, and seeded defects reported with line evidence. |
| Hermes Agent | 0.18.2; `big-pickle` via `opencode-zen` | Repository `skills/` via `external_dirs` | Workflow verified with deviations | Implicit router selection and focused routing worked; three findings relied on unsupported assumptions. |
| Claude Code | Not recorded | `.claude/skills/` guidance | Setup documented | No isolated discovery or workflow run. |
| Gemini CLI | Not recorded | `.agents/skills/` guidance | Setup documented | No isolated discovery or workflow run. |
| OpenCode | Not recorded | `.opencode/skills/` guidance | Setup documented | No isolated discovery or workflow run. |

The Codex installation column records the historical test environment, not the
current recommendation. Current Codex documentation places repository and user
skills under `.agents/skills`; the README uses that current path. The legacy
`.codex/skills/` result remains useful behavioral evidence for CLI 0.133.0, but
must not be generalized to current installation guidance. See the current
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

Hermes Skills Hub was checked on 2026-07-15 and did not resolve
`CodeSigils/py-review-skill`. The verified Hermes development path remains the
repository `skills/` directory configured through `external_dirs` until a hub
identifier is published and tested.

All six shipped skills also pass
`python3 .github/scripts/check-portability.py` with zero platform-reference
exemptions.

## Recorded Fixture

The skill revision under test was commit `0ece74b`. Codex received a direct
copy of that revision's `skills/` directory in the legacy `.codex/skills/`
location used by the recorded run; Hermes loaded the same canonical directory
through its configured `external_dirs` path. No installed mirror was used for
either result.

Runs used an isolated Python 3.11 repository with Ruff configured and the
`async api boundary` source from `review-fixtures.json`. The reviewed function
accepts `dict[str, Any]`, calls synchronous `requests.get()` inside `async def`,
performs no input validation or HTTP timeout, calls an undefined `find_user`,
and immediately consumes the results.

The prompt requested a read-only review of `app/users.py`, allowed any relevant
installed skill, required line citations, and asked the final response to name
skills actually used. It did not name `py-review` or any focused skill.

Expected evidence:

- discover and use `py-review` without explicit preloading in the prompt;
- route to async, error-handling, anti-pattern, and type-safety guidance;
- report the blocking synchronous HTTP call and unchecked input boundary;
- cite local lines and avoid modifying the fixture; and
- avoid claims that require definitions or repository context not present in
  the fixture.

## 2026-07-14 Results

### Codex CLI

Codex read the repository-local `py-review` router, then loaded
`py-async-patterns`, `py-error-handling`, `py-anti-patterns`, and
`py-type-safety`. It reported the undefined symbol, blocking HTTP call, missing
timeout, unchecked payload, and unguarded response decoding with line evidence.
The run completed read-only with 61,712 input tokens, 44,544 cached input
tokens, 1,909 output tokens, and 588 reasoning output tokens.

An initial environment attempt did not reach the fixture because the configured
`gpt-5.6-sol` model required a newer Codex CLI. Retrying explicitly with
`gpt-5.4`, which was supported by CLI 0.133.0, produced the verified result. The
rejected attempt is not skill-compatibility evidence.

### Hermes Agent

Hermes implicitly used the same router and four focused skills. It reported the
undefined symbol, blocking HTTP call, missing timeout, `Any` boundary, and
missing payload validation. The run completed read-only with 24,696 input
tokens, 147,584 cache-read tokens, 4,535 output tokens, 2,534 reasoning tokens,
and six API calls.

The review also assumed without local evidence that `find_user` returns
`User | None`, that its result is an ORM model, and that a missing `__init__.py`
is a packaging problem. Those claims violate the router's requirement to avoid
generic findings without local evidence. Hermes therefore demonstrates working
discovery and routing, but not yet clean finding precision.

## Claim Boundary and Next Evidence

Do not generalize these runs to every model, agent version, repository shape, or
future skill revision. Re-run an agent after changing router triggers, focused
rule applicability, installation layout, or support wording. Recheck this
evidence no later than the review-by date above even if the payload is unchanged.

The most useful next compatibility run is an isolated Claude Code, Gemini CLI,
or OpenCode workflow using this same fixture and prompt. Promote that agent from
**Setup documented** only when discovery, routing, final findings, deviations,
agent version, and model are recorded here.
