# Extraction Log

Source repository: <https://github.com/wshobson/agents> at
`5cc2549a50fc672230efd0a0307e2fd27ffba792`.

Upstream licence: MIT, Copyright (c) 2024 Seth Hobson; text at
<https://github.com/wshobson/agents/blob/5cc2549a50fc672230efd0a0307e2fd27ffba792/LICENSE>.

## Ownership and redistribution attestation

CodeSigils owns this derivative payload and attests that the recorded MIT
source material may be redistributed under this repository's MIT licence.
The source commit is historical provenance, not a claim that the upstream
payload is current. CodeSigils owns review and approval of all later rule,
router, example, and validation changes.

| Skill | Source path | Extracted | Notes |
|-------|-------------|-----------|-------|
| `py-type-safety` | `plugins/python-development/skills/python-type-safety/SKILL.md` | 2026-07-07 | Condensed into inline review rules; added impact/applicability/examples. |
| `py-error-handling` | `plugins/python-development/skills/python-error-handling/SKILL.md` | 2026-07-07 | Condensed into review rules around validation, exceptions, chaining, and batches. |
| `py-anti-patterns` | `plugins/python-development/skills/python-anti-patterns/SKILL.md` | 2026-07-07 | Extracted high-signal anti-patterns; cross-domain duplicates kept out. |
| `py-async-patterns` | `plugins/python-development/skills/async-python-patterns/SKILL.md` | 2026-07-07 | Focused on async review failures: blocking, missing await, gather, cancellation, timeouts. |
| `py-code-style` | `plugins/python-development/skills/python-code-style/SKILL.md` | 2026-07-07 | Focused on reviewable style/tooling decisions; defers to configured tools. |

Transformation policy:

- Preserve review-relevant substance, not source prose structure.
- Keep each focused skill within the validator's 5–12 rule budget. The current
  corpus has five rules in each focused skill except `py-code-style`, which has
  ten because its scope covers formatting, names, regex, constants, reuse, and
  domain string transformations.
- Keep rules inline in `SKILL.md`; no per-rule files.
- Add references only for version-sensitive or non-obvious claims.

## Recheck triggers

Reconfirm this record before importing additional upstream material, changing
the repository licence, or making a new redistribution claim. For a new or
substantially rewritten rule, record whether it is upstream-derived (including
the source path and pinned revision) or repository-authored, and obtain
CodeSigils maintainer approval in the change review.
