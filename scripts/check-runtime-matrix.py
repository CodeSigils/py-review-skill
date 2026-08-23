#!/usr/bin/env python3
"""Check runtime compatibility tables against the machine-readable matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/runtime-matrix.json"
PORTABILITY = ROOT / "docs/portability-contract.md"
COMPATIBILITY = ROOT / "docs/compatibility.md"

COMPATIBILITY_STATUS = {
    "limited": "Workflow verified with deviations",
    "workflow_verified": "Workflow verified",
    "candidate": "Setup documented",
}


def row_for(text: str, name: str) -> str | None:
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) > 1 and cells[1] == name:
            return line
    return None


def main() -> int:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    portability = PORTABILITY.read_text(encoding="utf-8")
    compatibility = COMPATIBILITY.read_text(encoding="utf-8")
    errors: list[str] = []
    for runtime in data["runtimes"]:
        name = runtime["name"]
        version = runtime["version"]
        status = runtime["status"]
        portability_row = row_for(portability, name)
        if not portability_row or version not in portability_row or f"`{status}`" not in portability_row:
            errors.append(f"{PORTABILITY}: matrix drift for {name}")
        compatibility_row = row_for(compatibility, name)
        expected_status = COMPATIBILITY_STATUS[status]
        if not compatibility_row or version not in compatibility_row or expected_status not in compatibility_row:
            errors.append(f"{COMPATIBILITY}: matrix drift for {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated runtime matrix for {len(data['runtimes'])} runtimes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
