#!/usr/bin/env python3
"""Validate end-to-end review routing fixtures."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "review-fixtures.json"
SKILLS_DIR = ROOT / "skills"
RULE_RE = re.compile(r"^### Rule: (?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)", re.MULTILINE)

SKILL_TRIGGERS: dict[str, tuple[str, ...]] = {
    "py-type-safety": (
        "Any",
        "dict[",
        "list[",
        " | None",
        "Optional[",
        "cast(",
        "Protocol",
        "Generic",
    ),
    "py-error-handling": (
        "except",
        "raise",
        "try:",
        "payload",
        "config",
        "open(",
        "client.",
    ),
    "py-anti-patterns": (
        "API_KEY",
        "sk-",
        "https://",
        "timeout=",
        "=[]",
        "= []",
        " = {}",
        "db.",
    ),
    "py-async-patterns": (
        "async def",
        "await ",
        "asyncio.",
        "requests.",
        "aio",
        "AsyncClient",
    ),
    "py-code-style": (
        "ruff",
        "pyproject.toml",
        "import ",
        "def ",
        "class ",
    ),
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"{path}: could not read file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc


def known_rules() -> dict[str, str]:
    rules: dict[str, str] = {}
    for path in sorted(SKILLS_DIR.glob("py-*/SKILL.md")):
        if path.parent.name == "py-review":
            continue
        text = path.read_text(encoding="utf-8")
        for match in RULE_RE.finditer(text):
            rule_id = match.group("id")
            if rule_id in rules:
                raise SystemExit(f"duplicate rule id in skills: {rule_id}")
            rules[rule_id] = path.parent.name
    return rules


def combined_text(fixture: dict[str, Any]) -> str:
    chunks = [" ".join(fixture.get("toolchain", []))]
    for changed_file in fixture.get("changed_files", []):
        chunks.append(str(changed_file.get("path", "")))
        chunks.append(str(changed_file.get("content", "")))
    return "\n".join(chunks)


def route_skills(fixture: dict[str, Any]) -> set[str]:
    text = combined_text(fixture)
    routed: set[str] = set()
    for skill, triggers in SKILL_TRIGGERS.items():
        if any(trigger in text for trigger in triggers):
            routed.add(skill)
    return routed


def validate_fixture_shape(index: int, fixture: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(fixture, dict):
        return [f"fixture {index}: must be an object"]
    for key in ("name", "changed_files", "expected_skills", "expected_rules"):
        if key not in fixture:
            errors.append(f"fixture {index}: missing {key!r}")
    if not isinstance(fixture.get("changed_files"), list) or not fixture.get("changed_files"):
        errors.append(f"fixture {index}: changed_files must be a non-empty list")
    if not isinstance(fixture.get("expected_skills"), list) or not fixture.get("expected_skills"):
        errors.append(f"fixture {index}: expected_skills must be a non-empty list")
    if not isinstance(fixture.get("expected_rules"), list) or not fixture.get("expected_rules"):
        errors.append(f"fixture {index}: expected_rules must be a non-empty list")
    return errors


def main() -> int:
    fixtures = load_json(FIXTURES)
    if not isinstance(fixtures, list) or not fixtures:
        print(f"{FIXTURES}: must contain a non-empty list", file=sys.stderr)
        return 1

    rules = known_rules()
    known_skills = {path.parent.name for path in SKILLS_DIR.glob("py-*/SKILL.md")}
    errors: list[str] = []

    for index, fixture in enumerate(fixtures, start=1):
        errors.extend(validate_fixture_shape(index, fixture))
        if errors:
            continue

        name = fixture["name"]
        expected_skills = set(fixture["expected_skills"])
        unknown_skills = sorted(expected_skills - known_skills)
        if unknown_skills:
            errors.append(f"{name}: unknown expected skills: {unknown_skills}")

        routed = route_skills(fixture)
        missing_routes = sorted(expected_skills - routed)
        if missing_routes:
            errors.append(f"{name}: expected skills not routed: {missing_routes}")

        for rule_id in fixture["expected_rules"]:
            skill = rules.get(rule_id)
            if skill is None:
                errors.append(f"{name}: unknown expected rule: {rule_id}")
            elif skill not in expected_skills:
                errors.append(
                    f"{name}: expected rule {rule_id!r} belongs to {skill},"
                    " but that skill is not expected"
                )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated {len(fixtures)} review routing fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
