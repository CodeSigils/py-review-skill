#!/usr/bin/env python3
"""Regression tests for release gating and tag resolution."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_waits_for_successful_validation(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("workflow_run:", workflow)
        self.assertIn("workflows: [validate]", workflow)
        self.assertIn("types: [completed]", workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)
        self.assertIn("github.event.workflow_run.event == 'push'", workflow)

    def test_release_requires_one_validated_tag(self) -> None:
        release = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("git tag --points-at HEAD --list 'v*.*.*'", release)
        self.assertIn('Expected exactly one release tag', release)
        self.assertIn("steps.tag.outputs.tag != ''", release)


if __name__ == "__main__":
    unittest.main()
