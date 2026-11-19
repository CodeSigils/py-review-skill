#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from exit_codes import FINDINGS, read_text, run

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "selection" / "cases.json"
KNOWN_SKILLS = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}


def load_cases() -> list[dict[str, Any]]:
    data = json.loads(read_text(CASES))
    if data.get("version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError(f"{CASES}: expected version 1 and a cases list")
    return data["cases"]


def main() -> int:
    try:
        cases = load_cases()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        return FINDINGS

    errors: list[str] = []
    selected_coverage: set[str] = set()
    excluded_coverage: set[str] = set()
    ids: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        selected = set(case.get("expected_selected", []))
        excluded = set(case.get("expected_not_selected", []))
        prompt = case.get("prompt")
        if not isinstance(case_id, str) or not case_id:
            errors.append("selection case: missing id")
            continue
        if case_id in ids:
            errors.append(f"{case_id}: duplicate id")
        ids.add(case_id)
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{case_id}: missing prompt")
        if selected - KNOWN_SKILLS or excluded - KNOWN_SKILLS:
            errors.append(f"{case_id}: references an unknown skill")
        if selected & excluded:
            errors.append(f"{case_id}: skill cannot be both selected and excluded")
        selected_coverage.update(selected)
        excluded_coverage.update(excluded)

    missing_selected = KNOWN_SKILLS - selected_coverage
    missing_excluded = KNOWN_SKILLS - excluded_coverage
    if missing_selected:
        errors.append(f"selection cases lack positive coverage: {sorted(missing_selected)}")
    if missing_excluded:
        errors.append(f"selection cases lack negative coverage: {sorted(missing_excluded)}")
    if not any(
        "py-error-handling" in set(case.get("expected_selected", []))
        and "py-anti-patterns" in set(case.get("expected_not_selected", []))
        for case in cases
    ):
        errors.append("selection cases lack the resource-lifecycle collision guard")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return FINDINGS
    print(f"validated {len(cases)} selection cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(main))
