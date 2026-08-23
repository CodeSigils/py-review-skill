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
SUPPORTED_PYTHON_VERSIONS = ("3.10", "3.11", "3.12", "3.13", "3.14")


def require(text: str, snippets: tuple[str, ...], source: str, errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{source}: missing required compatibility contract: {snippet}")


def extract_inline_list(text: str, key: str) -> tuple[str, ...] | None:
    """Return a quoted inline YAML list without depending on a YAML package."""
    match = re.search(
        rf"(?m)^\s*{re.escape(key)}:\s*\[(?P<items>[^\]]*)\]\s*$",
        text,
    )
    if not match:
        return None
    return tuple(re.findall(r'["\']([^"\']+)["\']', match.group("items")))


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
            "Historical workflow\nevidence",
            "recorded payload revision",
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
            "**Latest evidence captured:**",
            "**Review by:**",
            "Structurally portable",
            "Workflow verified",
            "Setup documented",
            "Current repository-local `.agents/skills/` symlinks",
            "legacy `.codex/skills/` copy also recorded",
            "current Codex recheck used repository-local `.agents/skills/` symlinks",
            "current installation guidance",
            "Hermes Skills Hub was checked",
            "commit `0ece74b`",
            "`5943e2d`",
            "20,145 total",
            "observed agent routing no longer",
            "historical evidence",
            "not verification of every later payload revision",
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
        ("python3 scripts/validate-compatibility.py",),
        ".github/workflows/ci.yml",
        errors,
    )
    python_boundaries = extract_inline_list(full_ci, "python-version")
    if python_boundaries != SUPPORTED_PYTHON_VERSIONS:
        errors.append(
            ".github/workflows/ci.yml: Python matrix must cover all declared "
            f"support versions {SUPPORTED_PYTHON_VERSIONS!r}"
        )
    checkout_pattern = re.compile(r"actions/checkout@[a-f0-9]{40}\s+#\s*v7\b")
    if not checkout_pattern.search(full_ci):
        errors.append(".github/workflows/ci.yml: missing pinned actions/checkout@<hash> # v7")
    setup_python_pattern = re.compile(r"actions/setup-python@[a-f0-9]{40}\s+#\s*v6\b")
    if not setup_python_pattern.search(full_ci):
        errors.append(".github/workflows/ci.yml: missing pinned actions/setup-python@<hash> # v6")
    setup_uv_pattern = re.compile(r"astral-sh/setup-uv@[a-f0-9]{40}\s+#\s*v\d+(?:\.\d+){2}\b")
    if not setup_uv_pattern.search(full_ci):
        errors.append(".github/workflows/ci.yml: missing SHA-pinned astral-sh/setup-uv action")
    if not re.search(r'(?m)^\s+version:\s*"\d+(?:\.\d+){2}"\s*$', full_ci):
        errors.append(".github/workflows/ci.yml: setup-uv must install an exact uv version")
    for command in ("uv sync --locked --only-dev", "uv run --no-sync ruff check ."):
        if command not in full_ci:
            errors.append(f".github/workflows/ci.yml: missing locked uv command: {command}")
    if "pip install" in full_ci:
        errors.append(".github/workflows/ci.yml: CI must consume uv.lock instead of pip install")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("validated compatibility evidence and current support contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
