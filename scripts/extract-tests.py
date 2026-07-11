#!/usr/bin/env python3
"""Extract rule examples into test-cases.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-cases.json"
RULE_RE = re.compile(
    r"^### Rule: (?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)\n(?P<body>.*?)(?=^### Rule: |\Z)",
    re.MULTILINE | re.DOTALL,
)
FIELD_RE = re.compile(r"^\*\*(?P<name>[^*]+):\*\* ?(?P<value>.*)$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```python\n(?P<code>.*?)\n```", re.DOTALL)


def fields(rule_body: str) -> dict[str, str]:
    return {
        match.group("name").strip(): match.group("value").strip()
        for match in FIELD_RE.finditer(rule_body)
    }


def extract() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for path in sorted((ROOT / "skills").glob("py-*/SKILL.md")):
        if path.parent.name == "py-review":
            continue
        text = path.read_text(encoding="utf-8")
        for match in RULE_RE.finditer(text):
            rule_id = match.group("id")
            body = match.group("body")
            data = fields(body)
            if "**Incorrect:**" not in body or "**Correct:**" not in body:
                continue
            code_blocks = CODE_BLOCK_RE.findall(body)
            if len(code_blocks) < 2:
                continue
            cases.append(
                {
                    "skill": path.parent.name,
                    "rule": rule_id,
                    "impact": data.get("Impact", ""),
                    "applies_when": data.get("Applies when", ""),
                    "review_signal": data.get("Review signal", ""),
                    "incorrect": code_blocks[0].strip(),
                    "correct": code_blocks[1].strip(),
                    "reason": data.get("Reason", ""),
                }
            )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if output differs")
    args = parser.parse_args()

    payload = json.dumps(extract(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUT.exists():
            print(f"{OUT}: missing generated file", file=sys.stderr)
            return 1
        current = OUT.read_text(encoding="utf-8")
        if current != payload:
            print(f"{OUT}: generated output differs; run scripts/extract-tests.py", file=sys.stderr)
            return 1
        print(f"{OUT}: up to date")
        return 0

    OUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
