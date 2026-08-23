#!/usr/bin/env python3
"""Validate package metadata and the complete shipped skill surface."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "py-review",
    "py-type-safety",
    "py-error-handling",
    "py-anti-patterns",
    "py-async-patterns",
    "py-code-style",
}


def main() -> int:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    errors: list[str] = []
    for required in ('name = "py-review-skill"', 'version = "0.1.0"', 'requires-python = ">=3.10"'):
        if required not in pyproject:
            errors.append(f"pyproject.toml: missing {required}")

    skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if skills != EXPECTED_SKILLS:
        errors.append(f"skills/: expected {sorted(EXPECTED_SKILLS)}, found {sorted(skills)}")
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        if not re.match(r"^---\nname: [^\n]+\ndescription: .+\n---\n", text):
            errors.append(f"{path}: invalid required frontmatter")

    if not (ROOT / ".github/release.yml").exists():
        errors.append(".github/release.yml: generated release configuration is missing")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated package metadata and {len(skills)} shipped skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
