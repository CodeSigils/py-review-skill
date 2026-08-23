#!/usr/bin/env python3
"""Regression tests for release gating and tag resolution."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_waits_for_successful_validation(self) -> None:
        workflow = yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text())
        trigger = workflow.get("on", workflow.get(True))
        self.assertEqual(trigger["workflow_run"]["workflows"], ["validate"])
        self.assertEqual(trigger["workflow_run"]["types"], ["completed"])
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow["jobs"]["release"]["if"])

    def test_release_requires_one_validated_tag(self) -> None:
        release = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("git tag --points-at HEAD --list 'v*.*.*'", release)
        self.assertIn('Expected exactly one release tag', release)
        self.assertIn("steps.tag.outputs.tag != ''", release)


if __name__ == "__main__":
    unittest.main()
