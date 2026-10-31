"""Regression tests for scheduled GitHub Action freshness reporting."""

from __future__ import annotations

import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ACTION_FRESHNESS_SPEC = spec_from_file_location(
    "action_freshness", SCRIPTS / "report-action-freshness.py"
)
assert ACTION_FRESHNESS_SPEC is not None and ACTION_FRESHNESS_SPEC.loader is not None
action_freshness = module_from_spec(ACTION_FRESHNESS_SPEC)
sys.modules[ACTION_FRESHNESS_SPEC.name] = action_freshness
ACTION_FRESHNESS_SPEC.loader.exec_module(action_freshness)


class ActionFreshnessTests(unittest.TestCase):
    def test_pinned_entries_ignores_non_step_pins(self) -> None:
        sha = "a" * 40
        with tempfile.TemporaryDirectory() as raw:
            workflow_root = Path(raw)
            workflow = workflow_root / "ci.yml"
            workflow.write_text(
                "\n".join(
                    [
                        "jobs:",
                        "  validate:",
                        "    steps:",
                        f"      # - uses: actions/checkout@{sha} # v7",
                        f'      - run: echo "uses: actions/checkout@{sha} # v7"',
                        f"      - uses: actions/checkout@{sha} # v7",
                    ]
                ),
                encoding="utf-8",
            )
            entries = action_freshness.pinned_entries(workflow_root)
        self.assertEqual(entries, [(workflow, 6, "actions/checkout", sha, "7")])
