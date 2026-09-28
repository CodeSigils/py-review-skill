"""Shared exit-code handling for maintainer validation scripts."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

CLEAN = 0
FINDINGS = 1
COULD_NOT_RUN = 2


class CouldNotRunError(Exception):
    """A required local input could not be read or decoded."""


def read_text(path: Path) -> str:
    """Read a required UTF-8 input or identify an incomplete check."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise CouldNotRunError(f"{path}: {exc}") from exc


def run(main: Callable[[], int]) -> int:
    """Run a checker and reserve code 2 for unavailable required inputs."""
    try:
        return main()
    except CouldNotRunError as exc:
        print(f"COULD NOT RUN: {exc}", file=sys.stderr)
        return COULD_NOT_RUN
