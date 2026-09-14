# Extraction Log

Source repo: `wshobson/agents` — commit `5cc2549a50fc672230efd0a0307e2fd27ffba792`

License: MIT, Copyright (c) 2024 Seth Hobson.

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
