#!/usr/bin/env python3
"""Validate compatibility evidence, current setup guidance, and CI boundaries."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
COMPATIBILITY = ROOT / "docs/compatibility.md"
FULL_CI = ROOT / ".github/workflows/ci.yml"
REVIEW_BY_RE = re.compile(r"^\*\*Review by:\*\* (?P<date>\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def require(text: str, snippets: tuple[str, ...], source: str, errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{source}: missing required compatibility contract: {snippet}")


def main() -> int:
    errors: list[str] = []
    if not COMPATIBILITY.exists():
        print("docs/compatibility.md: compatibility evidence report is required", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    compatibility = COMPATIBILITY.read_text(encoding="utf-8")
    full_ci = FULL_CI.read_text(encoding="utf-8")

    require(
        readme,
        (
            "[`docs/compatibility.md`](docs/compatibility.md)",
            "cp -r skills/* .agents/skills/",
            "python3 scripts/validate-compatibility.py",
            "Python 3.14",
        ),
        "README.md",
        errors,
    )
    for stale in (
        "cp -r skills/* .codex/skills/",
        "hermes skills install CodeSigils/py-review-skill",
    ):
        if stale in readme:
            errors.append(f"README.md: stale setup guidance remains: {stale}")

    require(
        compatibility,
        (
            "**Evidence captured:**",
            "**Review by:**",
            "Structurally portable",
            "Workflow verified",
            "Setup documented",
            "Legacy repository-local `.codex/skills/` used by the recorded run",
            "Current Codex documentation places repository and user",
            "skills under `.agents/skills`",
            "Hermes Skills Hub was checked",
            "commit `0ece74b`",
        ),
        "docs/compatibility.md",
        errors,
    )
    for agent in ("Codex CLI", "Hermes Agent", "Claude Code", "Gemini CLI", "OpenCode"):
        if compatibility.count(f"| {agent} |") != 1:
            errors.append(f"docs/compatibility.md: expected one matrix row for {agent}")

    review_match = REVIEW_BY_RE.search(compatibility)
    if not review_match:
        errors.append("docs/compatibility.md: missing valid YYYY-MM-DD review-by marker")
    else:
        review_by = date.fromisoformat(review_match.group("date"))
        if review_by < date.today():
            errors.append(f"docs/compatibility.md: evidence review expired {review_by.isoformat()}")

    require(
        full_ci,
        (
            'python-version: ["3.10", "3.14"]',
            "actions/checkout@v7",
            "actions/setup-python@v6",
            "python3 scripts/validate-compatibility.py",
        ),
        ".github/workflows/ci.yml",
        errors,
    )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("validated compatibility evidence and current support contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
