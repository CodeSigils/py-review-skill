#!/usr/bin/env python3
"""Behavioral contract checks for the shipped skill rule corpus."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_RE = re.compile(r"^### Rule: (?P<rule>[a-z0-9]+(?:-[a-z0-9]+)*)", re.MULTILINE)


class SkillContractTests(unittest.TestCase):
    def test_every_rule_has_a_generated_positive_and_negative_case(self) -> None:
        rules: set[str] = set()
        for path in sorted((ROOT / "skills").glob("py-*/SKILL.md")):
            rules.update(match.group("rule") for match in RULE_RE.finditer(path.read_text()))

        cases = json.loads((ROOT / "test-cases.json").read_text(encoding="utf-8"))
        covered = {case["rule"] for case in cases}
        self.assertEqual(rules, covered)
        for case in cases:
            self.assertTrue(case["incorrect"].strip(), case["rule"])
            self.assertTrue(case["correct"].strip(), case["rule"])

    def test_fixture_expected_rules_belong_to_the_expected_skill(self) -> None:
        fixtures = json.loads((ROOT / "review-fixtures.json").read_text(encoding="utf-8"))
        rule_to_skill = {
            case["rule"]: case["skill"]
            for case in json.loads((ROOT / "test-cases.json").read_text(encoding="utf-8"))
        }
        for fixture in fixtures:
            expected = set(fixture["expected_skills"])
            for rule in fixture["expected_rules"]:
                self.assertIn(rule_to_skill[rule], expected, fixture["name"])


if __name__ == "__main__":
    unittest.main()
