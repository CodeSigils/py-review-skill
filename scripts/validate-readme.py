#!/usr/bin/env python3
"""Validate README coverage and its lightweight CI routing contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
FULL_CI = ROOT / ".github/workflows/ci.yml"
README_CI = ROOT / ".github/workflows/readme.yml"


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    errors: list[str] = []

    skill_names = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
    for name in skill_names:
        if f"`{name}`" not in readme:
            errors.append(f"README.md: missing shipped skill `{name}`")

    required_commands = (
        "python3 scripts/validate.py",
        "python3 scripts/validate-compatibility.py",
        "python3 scripts/validate-readme.py",
        "python3 scripts/extract-tests.py --check",
        "python3 scripts/validate-review-fixtures.py",
        "python3 scripts/check-expiry.py",
        "python3 scripts/verify-urls.py",
        "python3 .github/scripts/check-portability.py",
    )
    for command in required_commands:
        if command not in readme:
            errors.append(f"README.md: missing validation command: {command}")

    full_ci = FULL_CI.read_text(encoding="utf-8")
    if '      - "README.md"' in full_ci:
        errors.append(".github/workflows/ci.yml: README.md must not trigger the full matrix")

    readme_ci = README_CI.read_text(encoding="utf-8")
    for path in (
        ".github/workflows/ci.yml",
        ".github/workflows/readme.yml",
        "README.md",
        "scripts/validate-readme.py",
    ):
        if readme_ci.count(f'      - "{path}"') != 2:
            errors.append(
                f".github/workflows/readme.yml: {path} must trigger push and pull-request checks"
            )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated README contract for {len(skill_names)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
