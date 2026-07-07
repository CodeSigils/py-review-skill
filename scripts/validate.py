#!/usr/bin/env python3
"""Validate py-review-skill runtime skill files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
IMPACTS = {"CRITICAL", "HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"}
FOCUSED_SKILLS = {
    "py-type-safety": "type",
    "py-error-handling": "error",
    "py-anti-patterns": "anti",
    "py-async-patterns": "async",
    "py-code-style": "style",
}
RULE_RE = re.compile(
    r"^### Rule: (?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)\n(?P<body>.*?)(?=^### Rule: |\Z)",
    re.MULTILINE | re.DOTALL,
)
FIELD_RE = re.compile(r"^\*\*(?P<name>[^*]+):\*\* ?(?P<value>.*)$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```python\n(?P<code>.*?)\n```", re.DOTALL)


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"{path}: malformed YAML frontmatter") from exc

    data: dict[str, str] = {}
    for lineno, line in enumerate(raw.splitlines(), start=2):
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{path}:{lineno}: malformed frontmatter line")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    extra = set(data) - {"name", "description"}
    if extra:
        raise ValueError(f"{path}: unsupported frontmatter fields: {sorted(extra)}")
    for key in ("name", "description"):
        if not data.get(key):
            raise ValueError(f"{path}: missing frontmatter field {key!r}")
    if data["name"] != path.parent.name:
        raise ValueError(f"{path}: name must match folder {path.parent.name!r}")
    if len(data["description"].split()) < 12:
        raise ValueError(f"{path}: description is too short to trigger reliably")
    return data, body


def parse_fields(rule_body: str) -> dict[str, str]:
    return {
        match.group("name").strip(): match.group("value").strip()
        for match in FIELD_RE.finditer(rule_body)
    }


def validate_rule(path: Path, expected_prefix: str, rule_id: str, rule_body: str) -> list[str]:
    errors: list[str] = []
    if not rule_id.startswith(f"{expected_prefix}-"):
        errors.append(f"{path}: rule {rule_id!r} must start with {expected_prefix!r}")

    fields = parse_fields(rule_body)
    required = {
        "Impact",
        "Applies when",
        "Skip when",
        "Python",
        "Tools",
        "Review signal",
        "Reason",
    }
    missing = sorted(required - set(fields))
    if missing:
        errors.append(f"{path}: rule {rule_id}: missing fields {missing}")

    impact = fields.get("Impact")
    if impact and impact not in IMPACTS:
        errors.append(f"{path}: rule {rule_id}: invalid impact {impact!r}")

    for field in ("Applies when", "Skip when", "Review signal", "Reason"):
        if field in fields and len(fields[field].split()) < 4:
            errors.append(f"{path}: rule {rule_id}: {field!r} is too terse")

    if "**Incorrect:**" not in rule_body:
        errors.append(f"{path}: rule {rule_id}: missing Incorrect section")
    if "**Correct:**" not in rule_body:
        errors.append(f"{path}: rule {rule_id}: missing Correct section")

    code_blocks = CODE_BLOCK_RE.findall(rule_body)
    if len(code_blocks) < 2:
        errors.append(f"{path}: rule {rule_id}: expected two python code blocks")

    refs = fields.get("References")
    checked = fields.get("Checked")
    expires = fields.get("Expires")
    if refs and (not checked or not expires):
        errors.append(f"{path}: rule {rule_id}: References requires Checked and Expires")

    return errors


def validate_skill(path: Path, seen_rules: set[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    data, body = parse_frontmatter(text, path)
    errors: list[str] = []
    skill_name = data["name"]

    if skill_name == "py-review":
        if "## Routing" not in body:
            errors.append(f"{path}: router missing Routing section")
        return errors

    expected_prefix = FOCUSED_SKILLS.get(skill_name)
    if expected_prefix is None:
        errors.append(f"{path}: unexpected skill {skill_name!r}")
        return errors

    if "## Review Rules" not in body:
        errors.append(f"{path}: missing Review Rules section")

    rules = list(RULE_RE.finditer(body))
    if not 5 <= len(rules) <= 9:
        errors.append(f"{path}: expected 5-9 rules, found {len(rules)}")

    for match in rules:
        rule_id = match.group("id")
        if rule_id in seen_rules:
            errors.append(f"{path}: duplicate rule id {rule_id!r}")
        seen_rules.add(rule_id)
        errors.extend(validate_rule(path, expected_prefix, rule_id, match.group("body")))

    if len(text.splitlines()) > 500:
        errors.append(f"{path}: exceeds 500-line skill budget")

    return errors


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    expected = {"py-review", *FOCUSED_SKILLS}
    found = {path.parent.name for path in skill_files}
    if found != expected:
        errors.append(f"skills mismatch: expected {sorted(expected)}, found {sorted(found)}")

    if (ROOT / "references").exists():
        errors.append("top-level references/ is not allowed in v1")

    seen_rules: set[str] = set()
    for path in skill_files:
        try:
            errors.extend(validate_skill(path, seen_rules))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated {len(skill_files)} skills and {len(seen_rules)} rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
